export type TestSuite = {
    id: number;
    created_at: string;
    name: string;
    s3_link: string;
    suites_success: boolean;
};

export type TestSuiteWithoutTests = {
  id: string;
  title: string;
  description: string;
  status: TestStatus;
};

export type TestStatus = "PASSED" | "FAILED" | "RUNNING" | "QUEUED";

export type Test = {
    id: number;
    created_at: string;
    suite_id: number;
    name: string;
    summary: string;
    test_success: boolean;
    run_status: TestStatus;
    steps: string[];
    s3_link: string;
};

export type TestStep = {
  id: string;
  description: string;
  status: "passed" | "failed";
};


export type ExtendedTestSuite = TestSuite & {
  status: TestStatus;
  tests: Test[];
};