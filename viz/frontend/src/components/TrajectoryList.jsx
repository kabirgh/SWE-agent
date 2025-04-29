import React, { useState } from 'react';

// Function to determine the color based on status
const getStatusColor = (status) => {
  switch (status) {
    case 'passed':
      return 'bg-green-500'; // Green for passed
    case 'failed':
      return 'bg-red-600'; // Red for failed
    default:
      return 'bg-gray-400'; // Gray for unknown or other statuses
  }
};

export default function TrajectoryList({ trajectories, onSelectTrajectory, selectedTrajectoryId }) {
  const [searchTerm, setSearchTerm] = useState('');

  // Filter trajectories based on search term
  const filteredTrajectories = trajectories.filter(trajectory => // Updated variable name
    trajectory.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200 flex-shrink-0">
        <h2 className="text-lg font-medium mb-4">Available Trajectories</h2> {/* Updated title */}
        <div className="relative w-full">
          <input
            type="text"
            placeholder="Search trajectories..." // Updated placeholder
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Update checks and messages for trajectories */}
      {trajectories.length === 0 ? (
        <div className="flex items-center justify-center h-[100px] text-gray-500 text-sm text-center p-4">
          <p>No trajectories available.</p>
        </div>
      ) : filteredTrajectories.length === 0 ? (
        <div className="flex items-center justify-center h-[100px] text-gray-500 text-sm text-center p-4">
          <p>No trajectories match your search.</p>
        </div>
      ) : (
        <ul className="list-none overflow-y-auto flex-1 p-2">
          {/* Update mapping and props usage */}
          {filteredTrajectories.map(trajectory => (
            <li
              key={trajectory.id}
              className={`px-4 py-3 rounded-md cursor-pointer transition-colors duration-200 mb-1 text-sm flex items-center justify-between
                ${selectedTrajectoryId === trajectory.id // Updated selection check
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'hover:bg-gray-100'}`}
              onClick={() => onSelectTrajectory(trajectory.id)} // Updated handler call
            >
              <span>{trajectory.id}</span> {/* Display trajectory ID */}
              <div className="flex items-center">
                <span className={`w-2.5 h-2.5 rounded-full mr-2 ${getStatusColor(trajectory.status)}`}></span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}


