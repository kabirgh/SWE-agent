import React from 'react';

// Utility to safely stringify JSON
const safeJsonStringify = (obj) => {
  try {
    return JSON.stringify(obj, null, 2);
  } catch (e) {
    console.error("Error stringifying JSON:", e);
    return '[Error displaying JSON]';
  }
};

const ActionDetails = ({ step, onClose }) => {
  if (!step) return null;

  // Helper function to render a detail section if value exists
  const renderDetailSection = (label, value, isPreformatted = false, isJson = false) => {
    if (value === null || value === undefined || value === '') return null;

    let displayValue = value;
    if (isJson) {
      displayValue = safeJsonStringify(value);
    } else if (typeof value !== 'string') {
      // Ensure non-string, non-JSON values are converted to string
      displayValue = String(value);
    }

    return (
      <div className="mb-4">
        <span className="block text-gray-500 text-sm mb-1 font-medium">{label}</span>
        {isPreformatted ? (
          <pre className="bg-gray-100 p-3 rounded text-xs leading-relaxed overflow-x-auto whitespace-pre-wrap break-words">
            {displayValue}
          </pre>
        ) : (
          <div className="text-sm text-gray-800 whitespace-pre-wrap break-words">{displayValue}</div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white mt-1 mb-2 rounded-sm border border-gray-200 relative overflow-y-auto">
      <button
        className="sticky top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center text-xl text-gray-500 hover:bg-gray-100 z-10 leading-none pb-1 bg-white bg-opacity-75"
        onClick={onClose}
        aria-label="Close"
      >
        &#215;
      </button>
      <div className="p-4 space-y-4">
        {/* Display fields from the TrajectoryStep object */}
        {renderDetailSection('Thought', step.thought, true)} {/* Preformatted thought */}
        {renderDetailSection('Action', step.action, true)} {/* Preformatted action string */}
        {renderDetailSection('Observation / Output', step.observation, true)} {/* Preformatted observation/output */}
        {renderDetailSection('State', step.state, true, true)} {/* Formatted JSON state */}
        {renderDetailSection('Execution Time (s)', step.execution_time?.toFixed(3))} {/* Formatted time */}
        {renderDetailSection('Extra Info', step.extra_info, true, true)} {/* Formatted JSON extra info */}

        {/* Fallback if no details were rendered */}
        {!step.thought && !step.action && !step.observation && !step.response && !step.messages && !step.state && step.execution_time === undefined && !step.extra_info && (
          <div className="text-sm text-gray-500">No details available for this step.</div>
        )}
      </div>
    </div>
  );
};

export default ActionDetails;
