import { ForwardPropsWithRefAndChildren } from "@/lib/types/ForwardPropsWithRefAndChildren";
import ListItem from "./ListItem";
import clsx from "clsx";

export default function List({
  children,
  ...props
}: ForwardPropsWithRefAndChildren<"ul">) {
  return (
    <ul {...props} className={clsx("flex flex-col gap-4", props.className)}>
      {children}
    </ul>
  );
}

List.Item = ListItem;
