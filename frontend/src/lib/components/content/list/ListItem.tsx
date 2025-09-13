import { ForwardPropsWithRefAndChildren } from "@/lib/types/ForwardPropsWithRefAndChildren";
import clsx from "clsx";

export default function ListItem({
  className,
  children,
  ...props
}: ForwardPropsWithRefAndChildren<"li">) {
  return (
    <li
      {...props}
      className={clsx(
        "inline-block pl-3 pr-4 py-4 card border-l-[6px] text-xl w-full",
        className
      )}
    >
      {children}
    </li>
  );
}
