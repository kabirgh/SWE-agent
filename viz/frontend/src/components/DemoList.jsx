import React, { useState } from 'react';

function DemoList({ demos, onSelectDemo, selectedDemo }) {
  const [searchTerm, setSearchTerm] = useState('');

  // Filter demos based on search term
  const filteredDemos = demos.filter(demo =>
    demo.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'passed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200 flex-shrink-0">
        <h2 className="text-lg font-medium mb-4">Available Demos</h2>
        <div className="relative w-full">
          <input
            type="text"
            placeholder="Search demos..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-500"
          />
        </div>
      </div>

      {demos.length === 0 ? (
        <div className="flex items-center justify-center h-[100px] text-gray-500 text-sm text-center p-4">
          <p>No demos available.</p>
        </div>
      ) : filteredDemos.length === 0 ? (
        <div className="flex items-center justify-center h-[100px] text-gray-500 text-sm text-center p-4">
          <p>No demos match your search.</p>
        </div>
      ) : (
        <ul className="list-none overflow-y-auto flex-1 p-2">
          {filteredDemos.map(demo => (
            <li
              key={demo.id}
              className={`px-4 py-3 rounded-md cursor-pointer transition-colors duration-200 mb-1 text-sm flex items-center justify-between
                ${selectedDemo === demo.id
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'hover:bg-gray-100'}`}
              onClick={() => onSelectDemo(demo.id)}
            >
              <span>{demo.id}</span>
              <span className={`ml-2 ${getStatusColor(demo.status)}`}>
                {demo.status === 'passed' ? '✓' : demo.status === 'failed' ? '✗' : '?'}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default DemoList;
