import clsx from "clsx";

const CONTROL_TYPES = ["video", "console", "network"] as const;
export type ControlType = (typeof CONTROL_TYPES)[number]; // 'a'|'b'|'c';

export default function ControlBar({
  controlType,
  onControlTypeChange,
}: {
  controlType: ControlType;
  onControlTypeChange: (controlType: ControlType) => void;
}) {
  return (
    <div className="flex flex-row gap-4">
      {CONTROL_TYPES.map((type) => (
        <button
          key={type}
          onClick={() => onControlTypeChange(type)}
          className={clsx(
            "px-2 py-0.5 rounded-lg hover:cursor-pointer",
            controlType === type && "bg-background"
          )}
        >
          {type}
        </button>
      ))}
    </div>
  );
}
