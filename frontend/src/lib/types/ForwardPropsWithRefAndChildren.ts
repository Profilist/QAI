import { JSX } from "react";
import type { ForwardPropsWithRef } from "./ForwardPropsWithRef";

export type ForwardPropsWithRefAndChildren<
  T extends keyof JSX.IntrinsicElements
> = ForwardPropsWithRef<T> & {
  /**
   * React elements or nodes to be rendered inside this component.
   * This can include strings, numbers, JSX elements, fragments, arrays, or
   * any other renderable React node.
   */
  children: React.ReactNode;
};
