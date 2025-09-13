import List from "@/lib/components/content/list/List";
import PageContent from "@/lib/components/content/PageContent";

export default function Page() {
  return (
    <PageContent title="Test suites" breadcrumb="Actions/Test suites">
      <div className="flex flex-row h-full gap-6">
        <List className="grow basis-0">
          <a href="/test-suites/0">
            <List.Item>Authentication</List.Item>
          </a>
          <a href="/test-suites/1">
            <List.Item>Search, Sorting, and Filtering</List.Item>
          </a>
          <a href="/test-suites/2">
            <List.Item>Checkout</List.Item>
          </a>
          <a href="/test-suites/3">
            <List.Item>Update Profile</List.Item>
          </a>
        </List>
        <div className="grow basis-0 mb-6 card"></div>
      </div>
    </PageContent>
  );
}
