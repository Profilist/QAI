import PageContent from "@/lib/components/content/PageContent";
import Content from "./Content";

export type TestSuite = {
  id: string;
  title: string;
  description: string;
};

const testSuites: TestSuite[] = [
  { id: "0", title: "Authentication", description: "User login, logout, and authentication flows" },
  { id: "1", title: "Search, Sorting, and Filtering", description: "Product search and filtering functionality" },
  { id: "2", title: "Checkout", description: "Shopping cart and payment processing" },
  { id: "3", title: "Update Profile", description: "User profile management and settings" },
];

export default function Page() {
  return (
    <PageContent title="Test suites" breadcrumb="Actions/Test suites">
      <Content testSuites={testSuites}/>
    </PageContent>
  );
}