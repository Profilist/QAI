"use client";
import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function SideNavbar() {
  const pathname = usePathname();

  return (
    <nav 
      className="flex flex-col gap-6 px-10 py-8 font-content h-full"
      style={{ backgroundColor: 'var(--sidebar-bg)' }}
    >
      {/* Logo */}
      <div 
        className="border-b pb-6"
        style={{ borderColor: 'var(--sidebar-border)' }}
      >
        <span className="font-heading text-5xl text-white">QAI</span>
      </div>
      
      {/* Actions */}
      <div className="flex flex-col gap-3">
        <h2 
          className="font-heading text-2xl font-semibold"
          style={{ color: 'var(--sidebar-text)' }}
        >
          Actions
        </h2>
        <ul className="flex flex-col gap-1">
          {actions.map((route, i) => (
            <Route
              route={route}
              key={i}
              active={isLinkActive(route, pathname)}
            />
          ))}
        </ul>
      </div>
      
      {/* Help */}
      <div className="flex flex-col gap-3 mt-auto">
        <h2 
          className="font-heading text-2xl font-semibold"
          style={{ color: 'var(--sidebar-text)' }}
        >
          Help
        </h2>
        <ul className="flex flex-col gap-1">
          {help.map((route, i) => (
            <Route
              route={route}
              key={i}
              active={isLinkActive(route, pathname)}
            />
          ))}
        </ul>
      </div>
    </nav>
  );
}

interface Route {
  text: string;
  href: string;
}

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

function Route({ route, active }: { route: Route; active: boolean }) {
  return (
    <li 
      className={clsx(
        "text-xl transition-colors duration-200 rounded-md px-2 py-1 -mx-2 -my-1",
        active && "font-semibold"
      )}
      style={{
        color: active ? 'var(--sidebar-text-active)' : 'var(--sidebar-text)',
      }}
    >
      <Link 
        href={route.href} 
        className="block rounded-md px-2 py-1 -mx-2 -my-1 transition-colors duration-200"
        style={{
          color: 'inherit',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--sidebar-bg-hover)';
          e.currentTarget.style.color = 'var(--sidebar-text-hover)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
          e.currentTarget.style.color = 'inherit';
        }}
      >
        {route.text}
      </Link>
    </li>
  );
}

function isLinkActive(route: Route, pathname: string) {
  return pathname === route.href || `${pathname}/`.startsWith(route.href);
}
