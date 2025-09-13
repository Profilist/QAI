import { JSX } from "react";

// Type for forwarding props of a html element
// e.g. ForwardProps<HTMLButtonElement>
export type ForwardProps<T extends keyof JSX.IntrinsicElements> =
  JSX.IntrinsicElements[T];