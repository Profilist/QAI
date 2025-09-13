import React from "react";

const Sidebar = () => (
  <aside className="bg-[#242424] border-r-[1px] border-white w-64 min-h-screen flex flex-col justify-between p-8">
    <div>
      <h1 className="text-4xl font-serif font-bold mb-8 text-white">lorem</h1>
      <nav>
        <div className="mb-6">
          <h2 className="font-bold text-lg mb-2 text-gray-200">Actions</h2>
          <ul className="space-y-1">
            <li className="font-semibold text-white">Dashboard</li>
            <li className="text-gray-300">Test suites</li>
            <li className="text-gray-300">Saved tests</li>
            <li className="text-gray-300">History</li>
          </ul>
        </div>
        <div>
          <h2 className="font-bold text-lg mb-2 text-gray-200">Help</h2>
          <ul className="space-y-1">
            <li className="text-gray-300">Documentation</li>
            <li className="text-gray-300">FAQ</li>
            <li className="text-gray-300">Contact</li>
          </ul>
        </div>
      </nav>
    </div>
    <div className="border-t border-gray-800 pt-4 flex items-center justify-center">
      <span className="material-icons text-2xl text-gray-400">person</span>
    </div>
  </aside>
);

export default Sidebar;
