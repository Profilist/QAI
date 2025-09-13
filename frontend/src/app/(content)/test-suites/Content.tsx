"use client";

import List from "@/lib/components/content/list/List";
import { TestSuite } from "./page";
import { useState } from "react";
import clsx from "clsx";

export default function Content({ testSuites }: { testSuites: TestSuite[] }) {
  const [selectedTestSuite, setSelectedTestSuite] = useState<TestSuite | null>(
    null
  );

  function onTestSuiteClick(testSuite: TestSuite) {
    if (selectedTestSuite?.id === testSuite.id) {
      setSelectedTestSuite(null);
    } else {
      setSelectedTestSuite(testSuite);
    }
  }

  return (
    <div className="grid grid-cols-2 h-full gap-6">
      <List>
        {testSuites.map((testSuite) => (
          <button
            className="hover:cursor-pointer"
            onClick={() => onTestSuiteClick(testSuite)}
            key={testSuite.id}
          >
            <List.Item
              className={clsx(
                "text-start transition",
                selectedTestSuite?.id === testSuite.id && "border-accent"
              )}
            >
              {testSuite.title}
            </List.Item>
          </button>
        ))}
      </List>
      <div className="mb-6 flex flex-col gap-4">
        {/* Video */}
        <div className="card aspect-video"></div>
        {/* Controls */}
        {selectedTestSuite !== null && (
          <GoToSuiteButton testSuite={selectedTestSuite} />
        )}
      </div>
    </div>
  );
}

function GoToSuiteButton({ testSuite }: { testSuite: TestSuite }) {
  return (
    <a href={`/test-suites/${testSuite.id}`}>
      <div
        className="
        card h-16 border-accent bg-off-accent text-off-foreground
        flex flex-row justify-between items-center text-xl px-4"
      >
        <span className="overflow-ellipsis overflow-hidden whitespace-nowrap">Go to test suite "{testSuite.title}"</span>
        <i className="ri-arrow-right-line"></i>
      </div>
    </a>
  );
}
