import PageContent from "@/lib/components/content/PageContent";
import ProgressBar from "@/lib/components/content/progress-bar/ProgrssBar";
import List from "@/lib/components/content/list/List";

export default function Page() {
  const stats = {
    totalSuites: 12,
    passed: 8,
    failed: 2,
    pending: 2,
  };

  const recentActivity = [
    { id: "1", title: "Suite A", status: "passed" },
    { id: "2", title: "Suite B", status: "failed" },
    { id: "3", title: "Suite C", status: "pending" },
  ];

  return (
    <PageContent title="Dashboard" breadcrumb="Dashboard">
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card rounded-xl p-5 flex flex-col gap-2">
          <h3 className="heading text-2xl">Overview</h3>
          <div className="flex flex-col gap-1 text-lg">
            <div className="flex justify-between"><span>Total suites</span><span>{stats.totalSuites}</span></div>
            <div className="flex justify-between text-passed"><span>Passed</span><span>{stats.passed}</span></div>
            <div className="flex justify-between text-failed"><span>Failed</span><span>{stats.failed}</span></div>
            <div className="flex justify-between text-pending"><span>Pending</span><span>{stats.pending}</span></div>
          </div>
        </div>

        <div className="card rounded-xl p-5 flex flex-col gap-2 md:col-span-2">
          <h3 className="heading text-2xl">Run progress</h3>
          <ProgressBar current={stats.passed} max={stats.totalSuites} />
        </div>
      </section>

      <section className="mt-6 card rounded-xl p-5">
        <h3 className="heading text-2xl mb-3">Recent activity</h3>
        <List>
          {recentActivity.map((item) => (
            <List.Item key={item.id} className="flex justify-between items-center">
              <span>{item.title}</span>
              <span className="text-sm opacity-80">{item.status}</span>
            </List.Item>
          ))}
        </List>
      </section>
    </PageContent>
  );
}
