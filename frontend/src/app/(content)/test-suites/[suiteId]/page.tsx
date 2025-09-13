import List from "@/lib/components/content/list/List";
import PageContent from "@/lib/components/content/PageContent";

export default function Page() {
  return (
    <PageContent title="Authentication" breadcrumb="Actions/Test suites/Authentication">
      <div className="flex flex-row h-full gap-6">
        <List className="grow basis-0">
          <List.Item>Log in with username and password</List.Item>
          <List.Item>Log in with empty password</List.Item>
          <List.Item>Forgot password</List.Item>
          <List.Item>Log out</List.Item>
        </List>
        <div className="grow basis-0 mb-6 flex flex-col gap-4">
            {/* Video */}
          <div className="card aspect-video">
            <video>

            </video>
          </div>
          {/* Controls */}
          <div className="card h-20"></div>
          {/* Other */}
          <div className="card h-12"></div>
        </div>
      </div>
    </PageContent>
  );
}
