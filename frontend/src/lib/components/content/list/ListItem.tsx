import { ForwardPropsWithRefAndChildren } from "@/lib/types/ForwardPropsWithRefAndChildren";
import clsx from "clsx";

export default function ListItem({
  className,
  children,
  ...props
}: ForwardPropsWithRefAndChildren<"li">) {
  return (
    <li {...props} className={clsx("text-xl w-full p-2 rounded-xl border-outline border-1", className)}>
      {children}
    </li>
  );
}
