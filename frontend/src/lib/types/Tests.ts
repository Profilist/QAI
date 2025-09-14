export type TestSuite = {
  id: string;
  title: string;
  description: string;
  status: TestStatus;
  tests: Test[];
};

export type TestSuiteWithoutTests = {
  id: string;
  title: string;
  description: string;
  status: TestStatus;
  tests: Test[];
};

export type TestStatus = "passed" | "failed" | "pending" | "queued";

export type Test = {
  id: string;
  title: string;
  status: TestStatus;
  steps: TestStep[];
};

export type TestStep = {
  id: string;
  description: string;
  status: "passed" | "failed";
};
