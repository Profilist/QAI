"use client";

import PageContent from "@/lib/components/content/PageContent";
import List from "@/lib/components/content/list/List";
import ProgressBar from "@/lib/components/content/progress-bar/ProgrssBar";
import TestStatusIcon from "@/lib/components/content/utilities/TestStatusIcon";
import {
  ExtendedTestSuite,
  Test,
  TestStatus,
  TestSuite,
} from "@/lib/types/Tests";
import { useParams } from "next/navigation";
import { use, useEffect, useState } from "react";

export default function Page() {
  const params = useParams<{
    resultId: string;
  }>();
  const resultId = params.resultId;
  const [extendedTestSuites, setExtendedTestSuites] = useState<
    ExtendedTestSuite[] | null
  >(null);

  console.log(resultId)

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        const res = await fetch(
          `https://qai-ashy.vercel.app/results/${resultId}/suites`
        );
        const json = await res.json();
        const suites: TestSuite[] = json["data"];

        const detailRequests = suites.map((suite) =>
          fetch(`https://qai-ashy.vercel.app/suites/${suite.id}/tests`)
            .then((res) => res.json())
            .then((json) => json["data"])
        );

        const detailResults: Test[][] = await Promise.all(detailRequests);
        const statuses = detailResults.map((results) => {
          if (results.every((v) => v.run_status === "PASSED")) {
            return "PASSED";
          } else if (
            results.every(
              (v) => v.run_status === "PASSED" || v.run_status === "FAILED"
            )
          ) {
            return "FAILED";
          } else if (results.every((v) => v.run_status === "QUEUED")) {
            return "QUEUED";
          } else {
            return "RUNNING";
          }
        });

        if (!isMounted) {
          return;
        }

        setExtendedTestSuites(
          suites.map((suite, i) => ({
            ...suite,
            status: statuses[i],
            tests: detailResults[i],
          }))
        );
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

  if (extendedTestSuites === null) {
    return (
      <PageContent title="Test suites" breadcrumb="Actions/Test suites">
        Loading...
      </PageContent>
    );
  }

  return (
    <PageContent title="Test suites" breadcrumb="Actions/Test suites">
      <List>
        {extendedTestSuites.map((testSuite, i) => (
          <a
            href={`/${resultId}/test-suites/${testSuite.id}`}
            key={testSuite.id}
            className="group"
          >
            <List.Item className="text-start transition flex flex-row gap-2 items-start relative">
              <TestStatusIcon status={testSuite.status} className="text-2xl" />
              <div className="flex flex-row gap-4 items-center w-full pr-1">
                <div className="flex flex-col mt-0.25 w-1/2">
                  <h3 className="font-heading group-hover:underline">
                    {testSuite.name}
                  </h3>
                </div>
                <div className="w-1/2 flex flex-row justify-center px-20">
                  <ProgressBar
                    current={
                      testSuite.tests.filter(
                        (test) => test.run_status !== "QUEUED"
                      ).length
                    }
                    max={testSuite.tests.length}
                  />
                </div>
              </div>
            </List.Item>
          </a>
        ))}
      </List>
    </PageContent>
  );
}
