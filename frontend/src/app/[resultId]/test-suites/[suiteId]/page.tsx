"use client";

import List from "@/lib/components/content/list/List";
import ControlBar, {
  ControlType,
} from "@/lib/components/content/output/ControlBar";
import VideoPlayer from "@/lib/components/content/output/VideoPlayer";
import PageContent from "@/lib/components/content/PageContent";
import TestStatusIcon from "@/lib/components/content/utilities/TestStatusIcon";
import { ExtendedTestSuite, Test, TestSuite } from "@/lib/types/Tests";
import clsx from "clsx";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

export default function Page() {
  const { suiteId, resultId } = useParams<{
    suiteId: string;
    resultId: string;
  }>();
  const [extendedTestSuite, setExtendedTestSuite] =
    useState<ExtendedTestSuite | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        const res = await fetch(
          `https://qai-ashy.vercel.app/suites/${suiteId}`
        );
        const json = await res.json();
        const suite: TestSuite = json["data"];

        const detailResults: Test[] = await fetch(
          `https://qai-ashy.vercel.app/suites/${suiteId}/tests`
        )
          .then((res) => res.json())
          .then((json) => json["data"]);

        const computeStatus = () => {
          if (detailResults.every((v) => v.run_status === "PASSED")) {
            return "PASSED";
          } else if (
            detailResults.every(
              (v) => v.run_status === "PASSED" || v.run_status === "FAILED"
            )
          ) {
            return "FAILED";
          } else if (detailResults.every((v) => v.run_status === "QUEUED")) {
            return "QUEUED";
          } else {
            return "RUNNING";
          }
        };

        if (!isMounted) {
          return;
        }

        setExtendedTestSuite({
          ...suite,
          status: computeStatus(),
          tests: detailResults,
        });
      } catch (err) {
        console.error("Error fetching test suites:", err);
      }
    };

    fetchData();

    // repeat every 2s
    const interval = setInterval(fetchData, 2000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [resultId]);

  const [controlType, setControlType] = useState<ControlType>("video");

  const [openTests, setOpenTests] = useState(
    Array(extendedTestSuite?.tests.length ?? 0).fill(false)
  );
  const showPlayer = useMemo(() => openTests.some(Boolean), [openTests]);
  const selectedVideoSrc = useMemo(() => {
    const idx = openTests.findIndex((v) => v);
    if (idx === -1) return undefined;
    const url = extendedTestSuite?.tests?.[idx]?.s3_link;
    if (!url || typeof url !== "string") return undefined;
    console.log(url)
    return url;
  }, [openTests, extendedTestSuite]);

  useEffect(() => {
    setControlType("video");
  }, [showPlayer]);

    if (extendedTestSuite === null) {
    return (
      <PageContent title="Test Suite Not Found" breadcrumb="">
        <div>Loading...</div>
      </PageContent>
    );
  }

  console.log(extendedTestSuite.tests)

  return (
    <PageContent
      title={extendedTestSuite.name}
      breadcrumb={`Actions/Test suites/${extendedTestSuite.name}`}
    >
      <div className="grid grid-cols-2 h-full gap-6">
        <List>
          {extendedTestSuite.tests.map((test, i) => (
            <button
              className={clsx(
                test?.steps?.length > 0 && "group hover:cursor-pointer"
              )}
              onClick={() => {
                if (test?.steps?.length > 0) {
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
                <TestStatusIcon status={test.run_status} className="text-2xl" />
                <div className="flex flex-col gap-2 pt-0.5">
                  <h3 className="font-heading group-hover:underline">
                    {test.name}
                  </h3>

                  {openTests[i] && (
                    <div className="flex flex-col gap-1 relative">
                      <div className="absolute left-[9.25px] top-2 bottom-2 w-0.5 bg-queued -z-20"></div>
                      {test.steps.map((step) => (
                        <div
                          className="flex flex-row gap-2 items-center"
                          key={step}
                        >
                          <div className="relative flex flex-row justify-center items-center">
                            <div className="absolute inset-0 rounded-full bg-background -z-10 aspect-square my-auto"></div>
                            <i className="ri-circle-line text-queued"></i>
                          </div>
                          <span>{step}</span>
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
              {controlType === "video" && selectedVideoSrc && (
                <VideoPlayer src={selectedVideoSrc} />
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
