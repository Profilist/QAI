#!/usr/bin/env node
const { Octokit } = require('@octokit/rest');
const OpenAI = require('openai');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

class QAIPipeline {
  constructor() {
    this.octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
    this.openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    this.supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);
    this.prNumber = this.getPRNumber();
    this.repo = process.env.GITHUB_REPOSITORY?.split('/') || [];
    this.runId = `run_${Date.now()}_pr${this.prNumber}`;
    console.log(`🚀 Initializing QAI Pipeline - Run ID: ${this.runId}`);
  }

  getPRNumber() {
    if (process.env.GITHUB_EVENT_NUMBER) return process.env.GITHUB_EVENT_NUMBER;
    if (process.env.GITHUB_EVENT_PATH) {
      return JSON.parse(fs.readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8')).number;
    }
    return null;
  }

  async analyzePR() {
    console.log(`📊 Analyzing PR #${this.prNumber}...`);
    const [owner, repo] = this.repo;
    
    const { data: pr } = await this.octokit.pulls.get({
      owner, repo, pull_number: this.prNumber
    });
    console.log(`📝 PR Title: "${pr.title}"`);

    const { data: diff } = await this.octokit.pulls.get({
      owner, repo, pull_number: this.prNumber,
      mediaType: { format: 'diff' }
    });
    console.log(`🔍 Retrieved PR diff (${diff.length} characters)`);

    const codebaseSummary = this.loadCodebaseSummary();
    console.log(`📚 Loaded codebase summary (${codebaseSummary.length} characters)`);
    
    console.log(`🤖 Generating test scenarios with OpenAI...`);
    const completion = await this.openai.beta.chat.completions.parse({
      model: "gpt-4o-2024-08-06",
      messages: [{
        role: "system",
        content: `Analyze these changes and generate test scenarios:

CODEBASE: ${codebaseSummary}
PR: ${pr.title} - ${pr.body || 'No description'}
CHANGES: ${diff}

Generate focused test scenarios for autonomous agents.`
      }],
      response_format: {
        type: "json_schema",
        json_schema: {
          name: "scenarios",
          schema: {
            type: "object",
            properties: {
              scenarios: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    description: { type: "string" },
                    priority: { type: "string", enum: ["high", "medium", "low"] },
                    type: { type: "string", enum: ["ui", "api", "integration", "e2e"] },
                    persona: { type: "string" },
                    steps: { type: "array", items: { type: "string" } }
                  },
                  required: ["description", "priority", "type", "persona", "steps"]
                }
              }
            }
          }
        }
      }
    });

    const scenarios = completion.choices[0].message.parsed.scenarios;
    this.saveFile('test-scenarios.json', scenarios);
    console.log(`✅ Generated ${scenarios.length} test scenarios`);
    
    console.log(`💾 Uploading scenarios to Supabase...`);
    await this.uploadScenariosToDatabase(scenarios);
    
    return scenarios;
  }

  async runTests(scenarios) {
    console.log(`🧪 Running ${scenarios.length} test scenarios...`);
    
    // Create system prompt and options files for agents (as shown in flow diagram)
    this.createAgentFiles(scenarios);
    
    try {
      // Use our database-integrated agent runner instead of external endpoint
      console.log(`🤖 Running tests through integrated agent system...`);
      
      // Get the result_id from the database upload step
      if (!this.resultId) {
        throw new Error('No result_id available - database upload may have failed');
      }
      
      // Get suites for this result to run agents
      const { data: suites } = await this.supabase
        .from('suites')
        .select('id, name')
        .eq('result_id', this.resultId);
      
      if (!suites || suites.length === 0) {
        throw new Error('No suites found for this result');
      }
      
      console.log(`🏃 Running ${suites.length} agent suites...`);
      
      // Import and run our agent system for each suite
      const { spawn } = require('child_process');
      const path = require('path');
      
      const results = [];
      
      for (const suite of suites) {
        console.log(`🤖 Running suite: ${suite.name} (ID: ${suite.id})`);
        
        try {
          // Run Python agent runner with suite_id
          const pythonProcess = spawn('python3', [
            path.join(__dirname, '../agents/run_suite.py'),
            suite.id.toString()
          ], {
            env: { 
              ...process.env,
              SUITE_ID: suite.id.toString(),
              DEPLOYMENT_URL: process.env.DEPLOYMENT_URL || 'https://staging.example.com'
            }
          });
          
          let output = '';
          let errorOutput = '';
          
          pythonProcess.stdout.on('data', (data) => {
            output += data.toString();
            console.log(`[Suite ${suite.id}] ${data.toString().trim()}`);
          });
          
          pythonProcess.stderr.on('data', (data) => {
            errorOutput += data.toString();
            console.error(`[Suite ${suite.id} ERROR] ${data.toString().trim()}`);
          });
          
          await new Promise((resolve, reject) => {
            pythonProcess.on('close', (code) => {
              if (code === 0) {
                resolve();
              } else {
                reject(new Error(`Agent process exited with code ${code}: ${errorOutput}`));
              }
            });
            
            pythonProcess.on('error', (error) => {
              reject(new Error(`Failed to start agent process: ${error.message}`));
            });
            
            // Set timeout for agent execution
            setTimeout(() => {
              pythonProcess.kill();
              reject(new Error('Agent execution timed out'));
            }, parseInt(process.env.AGENT_TIMEOUT || '600000'));
          });
          
          // Parse agent result from output (agents save to database)
          results.push({
            suite_id: suite.id,
            suite_name: suite.name,
            success: true,
            output: output
          });
          
        } catch (error) {
          console.error(`❌ Suite ${suite.id} failed: ${error.message}`);
          results.push({
            suite_id: suite.id,
            suite_name: suite.name,
            success: false,
            error: error.message
          });
        }
      }
      
      console.log(`✅ Completed ${results.length} agent suite runs`);
      let results_legacy = results;
      
      this.saveFile('test-results.json', results);

      const passed = results.filter(r => r.success).length;
      const failed = results.length - passed;
      
      console.log(`📊 Test Results: ${passed}/${results.length} suites passed`);
      
      if (failed > 0) {
        console.log(`❌ Failed suites:`);
        results.filter(r => !r.success).forEach(result => {
          console.log(`   • ${result.suite_name}: ${result.error || 'Failed'}`);
        });
      }

      console.log(`💾 Database results already updated by agent system`);
      
      // Verify final database state
      const finalSuccess = await this.verifyFinalResults();
      
      console.log(`::set-output name=success::${finalSuccess}`);
      return finalSuccess;
    } catch (error) {
      console.error(`❌ Agent execution failed: ${error.message}`);
      
      // Update database with failure status
      if (this.resultId) {
        await this.supabase
          .from('results')
          .update({ 'run_status': 'FAILED' })
          .eq('id', this.resultId);
      }
      
      return false;
    }
  }

  async uploadScenariosToDatabase(scenarios) {
    try {
      // First, create the results record (PR level)
      const prData = {
        'pr-link': `https://github.com/${this.repo.join('/')}/pull/${this.prNumber}`,
        'pr_name': `PR #${this.prNumber}`,
        'overall_result': {},
        'run_status': 'PENDING'
      };

      const { data: resultData, error: resultError } = await this.supabase
        .from('results')
        .insert([prData])
        .select('id')
        .single();

      if (resultError) {
        console.error(`❌ Failed to create results record: ${resultError.message}`);
        return;
      }

      this.resultId = resultData.id;
      console.log(`✅ Created results record with ID: ${this.resultId}`);

      // Group scenarios by persona to create suites (agent level)
      const personaGroups = scenarios.reduce((groups, scenario) => {
        const persona = scenario.persona || 'default';
        if (!groups[persona]) groups[persona] = [];
        groups[persona].push(scenario);
        return groups;
      }, {});

      // Create suite records (one per persona/agent)
      this.suiteIds = {};
      for (const [persona, personaScenarios] of Object.entries(personaGroups)) {
        const suiteRecord = {
          result_id: this.resultId, // Foreign key to results table
          name: `${persona} Agent Suite`
        };

        const { data: suiteData, error: suiteError } = await this.supabase
          .from('suites')
          .insert([suiteRecord])
          .select('id')
          .single();

        if (suiteError) {
          console.error(`❌ Failed to create suite: ${suiteError.message}`);
          continue;
        }

        this.suiteIds[persona] = suiteData.id;

        // Create individual test records for this suite
        const testRecords = personaScenarios.map(scenario => ({
          suite_id: suiteData.id, // Foreign key to suites table
          name: scenario.description,
          test_success: null,
          run_status: 'PENDING',
          steps: []
        }));

        const { error: testsError } = await this.supabase
          .from('tests')
          .insert(testRecords);

        if (testsError) {
          console.error(`❌ Failed to create tests: ${testsError.message}`);
        }
      }

      console.log(`✅ Created ${Object.keys(personaGroups).length} suites with ${scenarios.length} tests`);
    } catch (error) {
      console.error(`❌ Database upload error: ${error.message}`);
    }
  }

  async updateTestResults(results) {
    try {
      // Update individual test results
      for (const result of results) {
        const { error } = await this.supabase
          .from('tests')
          .update({
            'test_success': result.success,
            'run_status': result.success ? 'PASSED' : 'FAILED'
          })
          .eq('name', result.scenario.description);

        if (error) {
          console.error(`❌ Failed to update test result: ${error.message}`);
        }
      }

      // Update suite-level success status
      const { data: suites } = await this.supabase
        .from('suites')
        .select('id, name')
        .eq('result_id', this.resultId);

      for (const suite of suites || []) {
        const { data: suiteTests } = await this.supabase
          .from('tests')
          .select('test_success')
          .eq('suite_id', suite.id);

        const allTestsComplete = suiteTests?.every(test => test.test_success !== null);
        const allTestsPassed = suiteTests?.every(test => test.test_success === true);

        // Note: suites table doesn't have success column in the provided schema
        // Tests success will be tracked at the result level
      }

      // Update overall PR result based on all tests
      const { data: allTests } = await this.supabase
        .from('tests')
        .select('test_success')
        .in('suite_id', suites?.map(s => s.id) || []);

      const totalTests = allTests?.length || 0;
      const passedTests = allTests?.filter(test => test.test_success === true).length || 0;
      const allTestsPassed = totalTests > 0 && passedTests === totalTests;

      if (totalTests > 0) {
        await this.supabase
          .from('results')
          .update({ 
            'run_status': allTestsPassed ? 'PASSED' : 'FAILED',
            'overall_result': { passed: passedTests, total: totalTests }
          })
          .eq('id', this.resultId);
      }

      console.log(`✅ Updated ${results.length} test results and cascade status updates`);
    } catch (error) {
      console.error(`❌ Database update error: ${error.message}`);
    }
  }

  createAgentFiles(scenarios) {
    console.log(`📝 Creating agent configuration files...`);
    
    // Create system-prompt.txt (as shown in flow diagram)
    const systemPrompt = `You are an autonomous QA testing agent. Your role is to thoroughly test web applications for bugs, usability issues, and functionality problems.

Your testing approach should be:
1. Methodical and comprehensive
2. Focus on finding unexpected issues and edge cases
3. Test both happy paths and error conditions
4. Document findings clearly with screenshots
5. Be creative in exploring the application

You have access to:
- Screenshot capabilities for documentation
- Full browser interaction (clicking, typing, navigation)
- Form submission and validation testing
- UI/UX evaluation capabilities

Your goal is to identify bugs and issues that human testers might miss through autonomous exploration and testing.`;
    
    this.saveFile('system-prompt.txt', systemPrompt, false);
    
    // Create options.json (as shown in flow diagram)
    const options = {
      "id": "agent_" + Date.now(),
      "thinking": "enabled", 
      "persona": "qa_tester",
      "timeout": parseInt(process.env.AGENT_TIMEOUT || '600000'),
      "deployment_url": process.env.DEPLOYMENT_URL || 'https://staging.example.com',
      "max_budget": 10.0,
      "screenshot_frequency": "high"
    };
    
    this.saveFile('options.json', options);
    
    // Create test-cases.json in the format expected by agents
    const testCases = {
      "suites": scenarios.map((scenario, index) => ({
        "id": `suite_${index + 1}`,
        "name": `${scenario.persona} - ${scenario.type} testing`,
        "description": scenario.description,
        "priority": scenario.priority,
        "type": scenario.type,
        "steps": scenario.steps
      }))
    };
    
    this.saveFile('test-cases.json', testCases);
    
    console.log(`✅ Created agent configuration files: system-prompt.txt, options.json, test-cases.json`);
  }

  async verifyFinalResults() {
    try {
      // Get final status from database
      const { data: result } = await this.supabase
        .from('results')
        .select('*, suites(*, tests(*))')
        .eq('id', this.resultId)
        .single();
      
      if (result) {
        const totalSuites = result.suites?.length || 0;
        const totalTests = result.suites?.reduce((acc, s) => acc + (s.tests?.length || 0), 0) || 0;
        const passedTests = result.suites?.reduce((acc, s) => 
          acc + (s.tests?.filter(t => t.test_success === true).length || 0), 0) || 0;
        
        // Calculate success based on run_status and test results
        const overallSuccess = result.run_status === 'PASSED' || (passedTests === totalTests && totalTests > 0);
        
        console.log(`📊 Final Results Summary:`);
        console.log(`   • Overall Status: ${result.run_status}`);
        console.log(`   • Overall Success: ${overallSuccess ? '✅' : '❌'}`);
        console.log(`   • Suites: ${totalSuites} total`);
        console.log(`   • Tests: ${passedTests}/${totalTests} passed`);
        
        return overallSuccess;
      }
    } catch (error) {
      console.error(`❌ Failed to verify results: ${error.message}`);
      return false;
    }
  }

  updateCodebaseSummary() {
    try {
      const summary = this.loadCodebaseSummary();
      const entry = `\n=== ${new Date().toISOString()} ===\nPR #${this.prNumber} merged after QAI testing\n`;
      const updated = (summary + entry).split('\n').slice(-500).join('\n'); // Keep last 500 lines
      this.saveFile('codebase-summary.txt', updated, false);
      console.log('✅ Summary updated');
    } catch (error) {
      console.warn('Summary update failed:', error.message);
    }
  }

  loadCodebaseSummary() {
    const path = this.getPath('codebase-summary.txt');
    return fs.existsSync(path) ? fs.readFileSync(path, 'utf8') : '';
  }

  saveFile(name, data, json = true) {
    fs.writeFileSync(this.getPath(name), json ? JSON.stringify(data, null, 2) : data);
  }

  getPath(file) {
    return path.join(__dirname, file);
  }
}

async function main() {
  const action = process.argv[2] || 'full';
  const pipeline = new QAIPipeline();

  console.log(`🎯 Running QAI Pipeline in '${action}' mode`);
  console.log(`📋 Environment Check:`);
  console.log(`   • OpenAI API Key: ${process.env.OPENAI_API_KEY ? '✅ Set' : '❌ Missing'}`);
  console.log(`   • Supabase URL: ${process.env.SUPABASE_URL ? '✅ Set' : '❌ Missing'}`);
  console.log(`   • QAI Endpoint: ${process.env.QAI_ENDPOINT ? '✅ Set' : '❌ Missing'}`);
  console.log(`   • GitHub Token: ${process.env.GITHUB_TOKEN ? '✅ Set' : '❌ Missing'}`);

  try {
    switch (action) {
      case 'analyze':
        console.log(`🔍 Starting analysis phase...`);
        await pipeline.analyzePR();
        console.log(`✅ Analysis complete`);
        break;
      case 'test':
        console.log(`🧪 Starting test phase...`);
        const scenarios = JSON.parse(fs.readFileSync(pipeline.getPath('test-scenarios.json')));
        const success = await pipeline.runTests(scenarios);
        console.log(`${success ? '✅' : '❌'} Test phase complete`);
        if (!success) process.exit(1);
        break;
      case 'update':
        console.log(`📝 Starting update phase...`);
        pipeline.updateCodebaseSummary();
        console.log(`✅ Update complete`);
        break;
      case 'full':
      default:
        console.log(`🚀 Starting full pipeline...`);
        console.log(`\n=== PHASE 1: ANALYSIS ===`);
        const testScenarios = await pipeline.analyzePR();
        
        console.log(`\n=== PHASE 2: TESTING ===`);
        const testSuccess = await pipeline.runTests(testScenarios);
        
        console.log(`\n=== PHASE 3: UPDATE ===`);
        if (testSuccess) {
          pipeline.updateCodebaseSummary();
          console.log(`🎉 Pipeline completed successfully!`);
        } else {
          console.log(`❌ Pipeline failed - tests did not pass`);
        }
        
        if (!testSuccess) process.exit(1);
    }
  } catch (error) {
    console.error(`💥 Pipeline failed: ${error.message}`);
    console.error(`Stack trace: ${error.stack}`);
    process.exit(1);
  }
}

if (require.main === module) main();

module.exports = { QAIPipeline };