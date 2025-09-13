"use client";

import { use } from "react";
import List from "@/lib/components/content/list/List";
import PageContent from "@/lib/components/content/PageContent";

const testSuites = [
  { id: 0, name: "Authentication", tests: ["Log in with username and password", "Log in with empty password", "Forgot password", "Log out"] },
  { id: 1, name: "Search, Sorting, and Filtering", tests: ["Search by product name", "Filter by category", "Sort by price", "Advanced search filters"] },
  { id: 2, name: "Checkout", tests: ["Add items to cart", "Remove items from cart", "Apply discount codes", "Complete payment"] },
  { id: 3, name: "Update Profile", tests: ["Update personal information", "Change password", "Update preferences", "Delete account"] },
];

interface PageProps {
  params: Promise<{
    suiteId: string;
  }>;
}

export default function Page({ params }: PageProps) {
  const resolvedParams = use(params);
  const suiteId = parseInt(resolvedParams.suiteId);
  const suite = testSuites.find(s => s.id === suiteId);
  
  if (!suite) {
    return (
      <PageContent title="Test Suite Not Found" breadcrumb="">
        <div className="flex items-center justify-center h-full">
            The requested test suite could not be found.
        </div>
      </PageContent>
    );
  }

  return (
    <PageContent title={suite.name} breadcrumb={`Actions/Test suites/${suite.name}`}>
      <div className="grid grid-cols-2 h-full gap-6">
        <List>
          <List.Item>Log in with username and password</List.Item>
          <List.Item>Log in with empty password</List.Item>
          <List.Item>Forgot password</List.Item>
          <List.Item>Log out</List.Item>
        </List>
        <div className="mb-6 flex flex-col gap-4">
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
