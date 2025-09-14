import PageContent from "@/lib/components/content/PageContent";
import List from "@/lib/components/content/list/List";
import ProgressBar from "@/lib/components/content/progress-bar/ProgrssBar";
import TestStatusIcon from "@/lib/components/content/utilities/TestStatusIcon";
import { TestSuite } from "@/lib/types/Tests";

const testSuites: TestSuite[] = [
  {
    id: "0",
    title: "Authentication",
    description: "User login, logout, and authentication flows",
    status: "passed",
    tests: [
      {
        id: "0",
        title: "Log in with username and password",
        status: "passed",
        steps: [
          { id: "0", description: "Focused #username", status: "passed" },
          { id: "1", description: "Entered 'username'", status: "passed" },
          { id: "2", description: "Focused #password", status: "passed" },
          { id: "3", description: "Entered 'password'", status: "passed" },
          { id: "4", description: "Clicked #submit", status: "failed" },
        ],
      },
      {
        id: "1",
        title: "Log in with empty password",
        status: "passed",
        steps: [],
      },
      { id: "2", title: "Forgot password", status: "passed", steps: [] },
      { id: "3", title: "Log out", status: "passed", steps: [] },
    ],
  },
  {
    id: "1",
    title: "Search, Sorting, and Filtering",
    description: "Product search and filtering functionality",
    status: "failed",
    tests: [
      {
        id: "0",
        title: "Log in with username and password",
        status: "passed",
        steps: [
          { id: "0", description: "Focused #username", status: "passed" },
          { id: "1", description: "Entered 'username'", status: "passed" },
          { id: "2", description: "Focused #password", status: "passed" },
          { id: "3", description: "Entered 'password'", status: "passed" },
          { id: "4", description: "Clicked #submit", status: "failed" },
        ],
      },
      {
        id: "1",
        title: "Log in with empty password",
        status: "passed",
        steps: [],
      },
      { id: "2", title: "Forgot password", status: "failed", steps: [] },
      { id: "3", title: "Log out", status: "passed", steps: [] },
      { id: "3", title: "Log out", status: "passed", steps: [] },
      { id: "3", title: "Log out", status: "passed", steps: [] },
      { id: "3", title: "Log out", status: "failed", steps: [] },
    ],
  },
  {
    id: "2",
    title: "Checkout",
    description: "Shopping cart and payment processing",
    status: "pending",
    tests: [
      {
        id: "0",
        title: "Log in with username and password",
        status: "passed",
        steps: [
          { id: "0", description: "Focused #username", status: "passed" },
          { id: "1", description: "Entered 'username'", status: "passed" },
          { id: "2", description: "Focused #password", status: "passed" },
          { id: "3", description: "Entered 'password'", status: "passed" },
          { id: "4", description: "Clicked #submit", status: "failed" },
        ],
      },
      {
        id: "1",
        title: "Log in with empty password",
        status: "passed",
        steps: [],
      },
      { id: "2", title: "Forgot password", status: "passed", steps: [] },
      { id: "3", title: "Log out", status: "pending", steps: [] },
      { id: "3", title: "Log out", status: "queued", steps: [] },
      { id: "3", title: "Log out", status: "queued", steps: [] },
    ],
  },
  {
    id: "3",
    title: "Update Profile",
    description: "User profile management and settings",
    status: "queued",
    tests: [
      {
        id: "0",
        title: "Log in with username and password",
        status: "queued",
        steps: [
          { id: "0", description: "Focused #username", status: "passed" },
          { id: "1", description: "Entered 'username'", status: "passed" },
          { id: "2", description: "Focused #password", status: "passed" },
          { id: "3", description: "Entered 'password'", status: "passed" },
          { id: "4", description: "Clicked #submit", status: "failed" },
        ],
      },
      {
        id: "1",
        title: "Log in with empty password",
        status: "queued",
        steps: [],
      },
      { id: "2", title: "Forgot password", status: "queued", steps: [] },
    ],
  },
];

export default function Page() {
  return (
    <PageContent title="Test suites" breadcrumb="Actions/Test suites">
      <List>
        {testSuites.map((testSuite, i) => (
          <a
            href={`/test-suites/${testSuite.id}`}
            key={testSuite.id}
            className="group"
          >
            <List.Item className="text-start transition flex flex-row gap-2 items-start relative">
              <TestStatusIcon status={testSuite.status} className="text-2xl" />
              <div className="flex flex-row gap-4 items-center w-full pr-1">
                <div className="flex flex-col mt-0.25 w-1/2">
                  <h3 className="font-heading group-hover:underline">
                    {testSuite.title}
                  </h3>
                  <span className="text-base overflow-hidden whitespace-nowrap overflow-ellipsis">
                    QAI Autonomous Testing #13: Pull request #7 synchronize by
                    Profilist
                  </span>
                </div>
                <div className="w-1/2 flex flex-row justify-center px-20">
                  <ProgressBar
                    current={
                      testSuite.tests.filter((test) => test.status !== "queued")
                        .length
                    }
                    max={testSuite.tests.length}
                  />
                </div>
              </div>
            </List.Item>
          </a>
        ))}
      </List>
    </PageContent>
  );
}
