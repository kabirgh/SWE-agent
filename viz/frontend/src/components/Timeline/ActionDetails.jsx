import React from 'react';
import { getActionName } from './utils';

const ActionDetails = ({ action, onClose, commandOutputs, isLoading, error }) => {
  if (!action) return null;

  // Get action name for display
  const actionName = getActionName(action);

  // Get command output if available
  let output = null;
  if (action?.details?.tool_call?.function?.arguments) {
    try {
      const args = JSON.parse(action.details.tool_call.function.arguments);
      const command = args.command || args.arguments || action.details.tool_call.function.arguments;
      if (command && commandOutputs) {
        output = commandOutputs[command];
      }
    } catch (e) {
      console.error('Error getting command output:', e);
    }
  }

  return (
    <div className="bg-white mt-1 mb-2 rounded-sm border border-gray-200 relative">
      <button
        className="absolute top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center text-xl text-gray-500 hover:bg-gray-100 z-10 leading-none pb-1"
        onClick={onClose}
        aria-label="Close"
      >
        &#215;
      </button>
      <div className="p-4">
        {/* Tool call section */}
        {action.details?.tool_call && (
          <div className="mb-6">
            <div className="space-y-3">
              <div className="flex">
                <span className="w-[100px] text-gray-500 text-sm">Action</span>
                <span className="flex-1 font-medium">{actionName}</span>
              </div>
              {action.details.tool_call.function.arguments &&
                action.details.tool_call.function.arguments !== '{}' &&
                action.details.tool_call.function.arguments !== 'null' &&
                action.details.tool_call.function.arguments.trim() !== '' && (
                  <div>
                    <span className="text-gray-500 text-sm">Arguments</span>
                    <pre className="mt-1 bg-gray-100 p-3 rounded text-xs leading-relaxed overflow-x-auto whitespace-pre-wrap break-words">
                      {JSON.stringify(JSON.parse(action.details.tool_call.function.arguments), null, 2)}
                    </pre>
                  </div>
                )}
            </div>
          </div>
        )}

        {/* Content section */}
        {action.details?.content && (
          <div className="mb-6">
            <div className="space-y-3">
              <div className="flex">
                <span className="w-[100px] text-gray-500 text-sm">Content</span>
              </div>
              <div>
                <pre className="mt-1 bg-gray-100 p-3 rounded text-xs leading-relaxed overflow-x-auto whitespace-pre-wrap break-words">
                  {action.details.content}
                </pre>
              </div>
            </div>
          </div>
        )}

        {/* Output section */}
        <div className="mb-6">
          <div className="space-y-3">
            <div className="flex">
              <span className="w-[100px] text-gray-500 text-sm">Output</span>
            </div>
            <div>
              {isLoading ? (
                <div className="mt-1 bg-gray-100 p-3 rounded text-xs text-gray-500">
                  Loading command outputs...
                </div>
              ) : error ? (
                <div className="mt-1 bg-gray-100 p-3 rounded text-xs text-red-500">
                  Error: {error}
                </div>
              ) : output ? (
                <pre className="mt-1 bg-gray-100 p-3 rounded text-xs leading-relaxed overflow-x-auto whitespace-pre-wrap break-words">
                  {output}
                </pre>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActionDetails;
