import React from "react";

export default function ProgressBar({
  current,
  max,
}: {
  current: number;
  max: number;
}) {
  const percentage = max > 0 ? Math.min((current / max) * 100, 100) : 0;

  return (
    <div className="w-full flex flex-row gap-4 items-center">
      <div className="grow h-2 border-1 border-outline rounded">
        <div
          className="transition bg-accent h-full"
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
      <span className="text-md">{current}/{max}</span>
    </div>
  );
}
