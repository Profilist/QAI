"use client";

import clsx from "clsx";
import { usePathname } from "next/navigation";
import { useParams } from "next/navigation";

export default function SideNavbar() {
  const pathname = usePathname();
  const params = useParams<{ resultId: string }>();

  return (
    <nav
      className="flex flex-col gap-6 px-10 py-8 font-content h-full"
      style={{ backgroundColor: "var(--sidebar-bg)" }}
    >
      {/* Logo */}
      <span className="font-heading text-5xl">QAI</span>

      {/* Actions */}
      <ul className="flex flex-col gap-1.5">
        <li className="font-heading text-2xl">Actions</li>
        {actions.map((route, i) => (
          <RouteLink
            prefix={params.resultId}
            route={route}
            key={i}
            active={isLinkActive(route, pathname)}
          />
        ))}
      </ul>
      {/* Help */}
      <ul className="flex flex-col gap-1.5">
        <li className="font-heading text-2xl">Help</li>
        {help.map((route, i) => (
          <RouteLink
            prefix={params.resultId}
            route={route}
            key={i}
            active={isLinkActive(route, pathname)}
          />
        ))}
      </ul>
    </nav>
  );
}

type Route = {
  text: string;
  href: string;
};

const actions: Route[] = [
  { text: "Dashboard", href: "/dashboard" },
  { text: "Test suites", href: "/test-suites" },
  { text: "Saved tests", href: "/saved-tests" },
  { text: "History", href: "/history" },
];

const help: Route[] = [
  { text: "Documentation", href: "/documentation" },
  { text: "FAQ", href: "/faq" },
  { text: "Contact", href: "/contact" },
];

function RouteLink({
  prefix,
  route,
  active,
}: {
  prefix: string;
  route: Route;
  active: boolean;
}) {
  return (
    <li className={clsx("text-xl", active && "underline text-accent")}>
      <a className="hover:underline" href={`/${prefix}${route.href}`}>
        {route.text}
      </a>
    </li>
  );
}

function isLinkActive(route: Route, pathname: string) {
  return pathname === route.href || `${pathname}/`.startsWith(route.href);
}
