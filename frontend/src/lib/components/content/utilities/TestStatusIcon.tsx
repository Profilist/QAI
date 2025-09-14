
import { TestStatus } from "@/lib/types/Tests";
import clsx from "clsx";

export default function TestStatusIcon({ status, className }: { status: TestStatus, className?: string }) {
  return (
    <>
      {status === "RUNNING" && (
        <>
          <i className={clsx("ri-focus-2-line animate-ping text-pending absolute", className)}></i>
          <i className={clsx("ri-focus-2-line text-pending", className)}></i>
        </>
      )}
      {status === "FAILED" && (
        <i className={clsx("ri-close-circle-fill text-failed", className)}></i>
      )}
      {status === "PASSED" && (
        <i className={clsx("ri-checkbox-circle-fill text-passed", className)}></i>
      )}
      {status === "QUEUED" && <i className={clsx("ri-circle-line text-queued", className)}></i>}
    </>
  );
}
