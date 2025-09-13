"use client";

import Link from "next/link";
import List from "@/lib/components/content/list/List";
import PageContent from "@/lib/components/content/PageContent";

const testSuites = [
  { id: 0, name: "Authentication", description: "User login, logout, and authentication flows" },
  { id: 1, name: "Search, Sorting, and Filtering", description: "Product search and filtering functionality" },
  { id: 2, name: "Checkout", description: "Shopping cart and payment processing" },
  { id: 3, name: "Update Profile", description: "User profile management and settings" },
];

export default function Page() {
  return (
    <PageContent title="Test suites">
      <div className="flex flex-row h-full gap-6">
        <List className="grow basis-0">
          {testSuites.map((suite) => (
            <Link 
              key={suite.id} 
              href={`/test-suites/${suite.id}`}
              className="block transition-all duration-200 hover:shadow-sm rounded-lg"
              style={{ backgroundColor: 'var(--gray-light)' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--gray-medium)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--gray-light)';
              }}
            >
              <List.Item className="cursor-pointer hover:bg-transparent">
                <div className="flex flex-col">
                  <span 
                    className="font-medium"
                    style={{ color: 'var(--gray-darker)' }}
                  >
                    {suite.name}
                  </span>
                  <span 
                    className="text-sm mt-1"
                    style={{ color: 'var(--gray-dark)' }}
                  >
                    {suite.description}
                  </span>
                </div>
              </List.Item>
            </Link>
          ))}
        </List>
        <div className="grow basis-0 mb-6 card"></div>
      </div>
    </PageContent>
  );
}
