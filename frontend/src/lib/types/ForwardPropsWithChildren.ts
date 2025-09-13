import { JSX } from "react";
import type { ForwardProps } from "./ForwardProps";

export type ForwardPropsWithChildren<T extends keyof JSX.IntrinsicElements> =
  ForwardProps<T> & {
    /**
     * React elements or nodes to be rendered inside this component.
     * This can include strings, numbers, JSX elements, fragments, arrays, or
     * any other renderable React node.
     */
    children: React.ReactNode;
  };
