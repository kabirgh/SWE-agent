import React from 'react';
import { ACTION_COLORS, BASH, FIND_GREP, VIEW_FILE, EDIT_FILE, CREATE_FILE, SUBMIT } from './constants';

const ColorLegend = () => {
  // Create a mapping of action types to display
  const displayTypes = [
    BASH,
    FIND_GREP,
    VIEW_FILE,
    EDIT_FILE,
    CREATE_FILE,
    SUBMIT
  ];

  return (
    <div className="flex flex-wrap mt-2 py-2">
      {displayTypes.map((name) => (
        <div key={name} className="flex items-center mr-4 mb-2">
          <span className="w-3 h-3 rounded mr-1.5" style={{ backgroundColor: ACTION_COLORS[name] || ACTION_COLORS.default }}></span>
          <span className="text-xs text-gray-500">{name}</span>
        </div>
      ))}
    </div>
  );
};

export default ColorLegend;
