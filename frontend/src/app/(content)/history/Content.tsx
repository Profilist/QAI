"use client";

import List from "@/lib/components/content/list/List";
import { useState } from "react";
import clsx from "clsx";

export type TestRun = {
  id: string;
  status: "pending" | "failed" | "passed";
  timeStarted: Date;
  timeCompleted: Date | null;
};

const dateFormatter = new Intl.DateTimeFormat("en-US");

function msToRoundedTimeString(ms: number): string {
  if (ms < 60 * 1000) {
    return `${Math.round(ms / 1000)} seconds`;
  } else if (ms < 60 * 60 * 1000) {
    return `${Math.round(ms / (60 * 1000))} minutes`;
  } else if (ms < 24 * 60 * 60 * 1000) {
    return `${Math.round(ms / (60 * 60 * 1000))} hours`;
  } else {
    return `${Math.round(ms / (24 * 60 * 60 * 1000))} days`;
  }
}

export default function Content({ testRuns }: { testRuns: TestRun[] }) {
  const [selectedTestRun, setSelectedTestRun] = useState<TestRun | null>(null);

  function onTestRunClick(testRun: TestRun) {
    if (selectedTestRun?.id === testRun.id) {
      setSelectedTestRun(null);
    } else {
      setSelectedTestRun(testRun);
    }
  }

  return (
    <div className="grid grid-cols-2 h-full gap-6">
      <List>
        {testRuns.map((testRun) => (
          <button
            className="hover:cursor-pointer"
            onClick={() => onTestRunClick(testRun)}
            key={testRun.id}
          >
            <List.Item
              className={clsx(
                "text-start transition",
                selectedTestRun?.id === testRun.id
                  ? "border-accent"
                  : clsx(
                      testRun.status === "passed" && "border-passed",
                      testRun.status === "failed" && "border-failed",
                      testRun.status === "pending" && "border-pending"
                    )
              )}
            >
              <div>
                <h3 className="font-heading">
                  {dateFormatter.format(testRun.timeStarted)}
                </h3>
                <p>
                  {testRun.timeCompleted === null ? "Started" : "Completed"}{" "}
                  {msToRoundedTimeString(
                    testRun.timeCompleted === null
                      ? new Date().getTime() - testRun.timeStarted.getTime()
                      : new Date().getTime() - testRun.timeCompleted.getTime()
                  )}{" "}
                  ago
                </p>
              </div>
            </List.Item>
          </button>
        ))}
      </List>
      <div className="mb-6 flex flex-col gap-4">
        {/* Video */}
        <div className="card aspect-[4/3]"></div>
        {/* Controls */}
      </div>
    </div>
  );
}
