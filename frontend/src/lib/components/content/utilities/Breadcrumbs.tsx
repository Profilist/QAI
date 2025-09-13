"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRightIcon, HomeIcon } from "@heroicons/react/24/outline";

interface BreadcrumbItem {
  label: string;
  href: string;
}

export default function Breadcrumbs() {
  const pathname = usePathname();
  
  // Generate breadcrumbs based on the current path
  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const segments = pathname.split('/').filter(segment => segment !== '');
    const breadcrumbs: BreadcrumbItem[] = [];
    
    // Always start with home
    breadcrumbs.push({ label: 'Home', href: '/' });
    
    // Build breadcrumbs from path segments
    let currentPath = '';
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      
      // Convert segment to readable label
      let label = segment;
      if (segment === 'dashboard') {
        label = 'Dashboard';
      } else if (segment === 'test-suites') {
        label = 'Test Suites';
      } else if (segment === 'history') {
        label = 'History';
      } else if (segment === 'saved-tests') {
        label = 'Saved Tests';
      } else if (segment === 'actions') {
        label = 'Actions';
      } else if (segment.match(/^\d+$/)) {
        // Handle dynamic segments like suiteId
        label = `Suite ${segment}`;
      } else {
        // Capitalize first letter and replace hyphens with spaces
        label = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
      }
      
      breadcrumbs.push({ label, href: currentPath });
    });
    
    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs();

  return (
    <nav className="px-9 py-4 bg-breadcrumb-bg border-b border-breadcrumb-border" aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2 text-sm">
        {breadcrumbs.map((breadcrumb, index) => (
          <li key={breadcrumb.href} className="flex items-center">
            {index > 0 && (
              <ChevronRightIcon className="h-4 w-4 text-breadcrumb-text mx-2" />
            )}
            {index === 0 && (
              <HomeIcon className="h-4 w-4 text-breadcrumb-text mr-1" />
            )}
            {index === breadcrumbs.length - 1 ? (
              <span className="text-breadcrumb-text-active font-medium" aria-current="page">
                {breadcrumb.label}
              </span>
            ) : (
              <Link
                href={breadcrumb.href}
                className="text-breadcrumb-text hover:text-breadcrumb-text-hover transition-colors duration-200"
              >
                {breadcrumb.label}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
