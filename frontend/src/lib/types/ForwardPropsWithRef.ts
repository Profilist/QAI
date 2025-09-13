import { JSX } from "react";
import type { ForwardProps } from "./ForwardProps";

// Type for forwarding props of a html element, with an addition ref prop
// e.g. ForwardPropsWithRef<HTMLButtonElement>
export type ForwardPropsWithRef<T extends keyof JSX.IntrinsicElements> =
  ForwardProps<T> & {
    /**
     * Optional ref forwarded to the underlying HTML element
     */

    ref?: React.ComponentRef<T>;
  };
