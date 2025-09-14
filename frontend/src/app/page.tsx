"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div 
      className="min-h-screen flex items-center justify-center"
      style={{ backgroundColor: 'var(--gray-light)' }}
    >
      <div className="text-center">
        <h1 
          className="text-6xl font-bold mb-8"
          style={{ color: 'var(--gray-darker)' }}
        >
          QAI
        </h1>
        <p 
          className="text-xl mb-12"
          style={{ color: 'var(--gray-dark)' }}
        >
          Quality Assurance Intelligence Platform
        </p>
        <div className="space-x-4">
          <Link 
            href="/1000/test-suites" 
            className="px-8 py-3 rounded-lg text-lg font-semibold transition-colors duration-200"
            style={{ 
              backgroundColor: 'var(--gray-dark)', 
              color: 'var(--gray-light)' 
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--gray-darker)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--gray-dark)';
            }}
          >
            Go to Dashboard
          </Link>
          <Link 
            href="/1000/test-suites" 
            className="px-8 py-3 rounded-lg text-lg font-semibold transition-colors duration-200"
            style={{ 
              backgroundColor: 'var(--gray-medium)', 
              color: 'var(--gray-light)' 
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--gray-dark)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--gray-medium)';
            }}
          >
            View Test Suites
          </Link>
        </div>
      </div>
    </div>
  );
}
