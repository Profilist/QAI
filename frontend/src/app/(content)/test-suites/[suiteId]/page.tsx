"use client";

import { use, useEffect, useMemo, useState } from "react";
import List from "@/lib/components/content/list/List";
import PageContent from "@/lib/components/content/PageContent";
import TestStatusIcon from "@/lib/components/content/utilities/TestStatusIcon";
import clsx from "clsx";
import VideoPlayer from "@/lib/components/content/output/VideoPlayer";
import ControlBar, {
  ControlType,
} from "@/lib/components/content/output/ControlBar";
import { Test } from "@/lib/types/Tests";


const tests: Test[] = [
  {
    id: "0",
    title: "Log in with username and password",
    status: "passed",
    steps: [
      { id: "0", description: "Focused #username", status: "passed" },
      { id: "1", description: "Entered 'username'", status: "passed" },
      { id: "2", description: "Focused #password", status: "passed" },
      { id: "3", description: "Entered 'password'", status: "passed" },
      { id: "4", description: "Clicked #submit", status: "failed" },
    ],
  },
  { id: "1", title: "Log in with empty password", status: "passed", steps: [] },
  { id: "2", title: "Forgot password", status: "failed", steps: [] },
  { id: "3", title: "Log out", status: "pending", steps: [] },
];

interface PageProps {
  params: Promise<{
    suiteId: string;
  }>;
}

export default function Page({ params }: PageProps) {
  const resolvedParams = use(params);
  const suiteId = parseInt(resolvedParams.suiteId);
  const suite = { name: "Authorization", tests };

  if (!suite) {
    return (
      <PageContent title="Test Suite Not Found" breadcrumb="">
        <div className="flex items-center justify-center h-full">
          The requested test suite could not be found.
        </div>
      </PageContent>
    );
  }

  const [openTests, setOpenTests] = useState(
    Array(suite.tests.length).fill(false)
  );
  const showPlayer = useMemo(() => openTests.some(Boolean), [openTests]);

  const [controlType, setControlType] = useState<ControlType>("video");

  useEffect(() => {
    setControlType("video");
  }, [showPlayer]);

  return (
    <PageContent
      title={suite.name}
      breadcrumb={`Actions/Test suites/${suite.name}`}
    >
      <div className="grid grid-cols-2 h-full gap-6">
        <List>
          {tests.map((test, i) => (
            <button
              className={clsx(
                test.steps.length > 0 && "group hover:cursor-pointer"
              )}
              onClick={() => {
                if (test.steps.length > 0) {
                  setOpenTests((prev) => {
                    const copy = [...prev];
                    copy[i] = !copy[i];
                    return copy;
                  });
                }
              }}
              key={test.id}
            >
              <List.Item className="text-start transition flex flex-row gap-2 items-start relative">
                <TestStatusIcon status={test.status} className="text-2xl" />
                <div className="flex flex-col gap-2 pt-0.5">
                  <h3 className="font-heading group-hover:underline">
                    {test.title}
                  </h3>

                  {openTests[i] && (
                    <div className="flex flex-col gap-1 relative">
                      <div className="absolute left-[9.25px] top-2 bottom-2 w-0.5 bg-queued -z-20"></div>
                      {test.steps.map((step) => (
                        <div
                          className="flex flex-row gap-2 items-center"
                          key={step.id}
                        >
                          <div className="relative flex flex-row justify-center items-center">
                            <div className="absolute inset-0 rounded-full bg-background -z-10 aspect-square my-auto"></div>
                            <TestStatusIcon status={step.status} />
                          </div>
                          <span>{step.description}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </List.Item>
            </button>
          ))}
        </List>
        {showPlayer && (
          <div className="mb-6 flex flex-col gap-4">
            {/* Video */}
            <div className="card aspect-[4/3] rounded-xl overflow-hidden">
              {controlType === "video" && (
                <VideoPlayer src="https://www.youtube.com/watch?v=dQw4w9WgXcQ" />
              )}
            </div>
            {/* Other */}
            <div className="card h-12 rounded-xl flex flex-row items-center px-4">
              <ControlBar
                controlType={controlType}
                onControlTypeChange={setControlType}
              />
            </div>
          </div>
        )}
      </div>
    </PageContent>
  );
}
