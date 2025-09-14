
import { TestStatus } from "@/lib/types/Tests";
import clsx from "clsx";

export default function TestStatusIcon({ status, className }: { status: TestStatus, className?: string }) {
  return (
    <>
      {status === "pending" && (
        <>
          <i className={clsx("ri-focus-2-line animate-ping text-pending absolute", className)}></i>
          <i className={clsx("ri-focus-2-line text-pending", className)}></i>
        </>
      )}
      {status === "failed" && (
        <i className={clsx("ri-close-circle-fill text-failed", className)}></i>
      )}
      {status === "passed" && (
        <i className={clsx("ri-checkbox-circle-fill text-passed", className)}></i>
      )}
      {status === "queued" && <i className={clsx("ri-circle-line text-queued", className)}></i>}
    </>
  );
}
