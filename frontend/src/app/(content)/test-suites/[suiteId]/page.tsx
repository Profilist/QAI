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
      <PageContent title="Test Suite Not Found">
        <div className="flex items-center justify-center h-full">
          <p style={{ color: 'var(--gray-medium)' }}>
            The requested test suite could not be found.
          </p>
        </div>
      </PageContent>
    );
  }

  return (
    <PageContent title={suite.name}>
      <div className="flex flex-row h-full gap-6">
        <List className="grow basis-0">
          {suite.tests.map((test, index) => (
            <List.Item 
              key={index} 
              className="cursor-pointer transition-colors duration-200"
              style={{ color: 'var(--gray-darker)' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--gray-medium)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              {test}
            </List.Item>
          ))}
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
