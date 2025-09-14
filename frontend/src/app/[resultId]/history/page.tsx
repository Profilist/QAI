import PageContent from "@/lib/components/content/PageContent";
import Content, { TestRun } from "./Content";

export default function Page() {
  return (
    <PageContent title="History" breadcrumb="Actions/History">
      <Content testRuns={testRuns} />
    </PageContent>
  );
}

const testRuns: TestRun[] = [
  {
    id: "3",
    status: "pending",
    timeStarted: new Date(2025, 8, 13, 14, 24, 54),
    timeCompleted: null,
  },
  {
    id: "2",
    status: "failed",
    timeStarted: new Date(2025, 8, 12, 16, 37, 54),
    timeCompleted: new Date(2025, 8, 12, 16, 42, 12),
  },
  {
    id: "1",
    status: "passed",
    timeStarted: new Date(2025, 8, 11, 14, 5, 4),
    timeCompleted: new Date(2025, 8, 11, 13, 58, 46),
  },
  {
    id: "0",
    status: "passed",
    timeStarted: new Date(2025, 8, 7, 11, 45, 45),
    timeCompleted: new Date(2025, 8, 7, 11, 58, 32),
  },
];
