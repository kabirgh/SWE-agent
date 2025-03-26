import React, { useState, useEffect, useRef } from 'react';

const VIEW_FILE = 'View file/folder'
const EDIT_FILE = 'Edit file'
const CREATE_FILE = 'Create file'
const STR_REPLACE_EDITOR = 'str_replace_editor'
const BASH = 'bash'
const FIND_GREP = 'find/grep'
const SUBMIT = 'submit'
const UNKNOWN = 'unknown'


// Color mapping for different action types
const ACTION_COLORS = {
  [VIEW_FILE]: '#0D47A1',      // Dark blue
  [EDIT_FILE]: '#66BB6A',      // Light green
  [CREATE_FILE]: '#2E7D32',    // Dark green
  [STR_REPLACE_EDITOR]: '#1B5E20', // Darkest green
  [BASH]: '#F4B400',           // Yellow
  [FIND_GREP]: '#2196F3',      // Medium blue
  [SUBMIT]: '#D32F2F',         // Red
  'default': '#757575'         // Grey (for unknown action types)
};

// Constants
const ACTIONS_PER_LINE = 50;
const LINE_HEIGHT = 30;

// Function to determine the actual action name
const getActionName = (action) => {
  if (!action || !action.details?.tool_call?.function) {
    return action.type || UNKNOWN;
  }

  const { name, arguments: argsString } = action.details.tool_call.function;
  let args = {};

  try {
    if (argsString && argsString !== '{}' && argsString !== 'null') {
      args = JSON.parse(argsString);
    }
  } catch (e) {
    console.error('Error parsing arguments:', e);
  }

  const cmd = args.command || '';

  // Apply the specific conditions
  if (name === 'str_replace_editor' && cmd === 'view') {
    return VIEW_FILE;
  } else if (name === 'str_replace_editor' && cmd === 'create') {
    return CREATE_FILE;
  } else if (name === 'str_replace_editor' && cmd === 'str_replace') {
    return EDIT_FILE;
  } else if (action.type === 'bash' && (cmd.startsWith('find') || cmd.startsWith('grep'))) {
    return FIND_GREP;
  }

  return action.type || UNKNOWN;
};

// ActionItem component for individual timeline items
const ActionItem = ({ action, index, viewportWidth, actionsLength, lineIndex, onClick, isSelected }) => {
  const indexInLine = index % ACTIONS_PER_LINE;

  // Calculate width for each action in a line
  const actionsInThisLine = Math.min(ACTIONS_PER_LINE, actionsLength - lineIndex * ACTIONS_PER_LINE);

  // Calculate segment width based on viewport width and max items per line
  // If fewer than ACTIONS_PER_LINE, use proportional sizing
  const maxWidth = viewportWidth / ACTIONS_PER_LINE;
  const segmentWidth = actionsInThisLine < ACTIONS_PER_LINE
    ? (viewportWidth / ACTIONS_PER_LINE) * (ACTIONS_PER_LINE / actionsInThisLine)
    : viewportWidth / ACTIONS_PER_LINE;

  // Limit to maxWidth if there are fewer items
  const actualWidth = Math.min(segmentWidth, maxWidth);

  // Get action name
  const actionName = getActionName(action);

  // Get color for action
  const color = ACTION_COLORS[actionName] || ACTION_COLORS.default;

  // Position based on index in line
  const position = indexInLine * actualWidth;
  const width = actualWidth * 0.95; // Reduced gap between actions (was 0.9)

  const style = {
    left: `${position}px`,
    top: `${lineIndex * LINE_HEIGHT}px`,
    width: `${width}px`,
    height: '28px',
    backgroundColor: color,
    position: 'absolute',
    borderRadius: '0',
    outline: isSelected ? '3px solid #000' : 'none',
    outlineOffset: isSelected ? '-2px' : '0'
  };

  return (
    <div
      className="absolute cursor-pointer transition-all duration-200 m-[1px]"
      style={style}
      onClick={() => onClick(action)}
      title={`${actionName}${action.timestamp ? ` (${action.timestamp.toFixed(2)})` : ''}`}
      data-action-type={actionName}
    >
      {isSelected && (
        <div className="absolute inset-0 flex items-center justify-center text-white font-medium">
          {index + 1}
        </div>
      )}
    </div>
  );
};

// Details panel component
const ActionDetails = ({ action, onClose, demoId }) => {
  const [output, setOutput] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOutput = async () => {
      if (!action?.details?.tool_call?.function?.arguments) return;

      try {
        const args = JSON.parse(action.details.tool_call.function.arguments);
        const command = args.command || args.arguments || action.details.tool_call.function.arguments;

        if (command) {
          setLoading(true);
          setError(null);
          const response = await fetch(`/api/demos/${demoId}/command-output?command=${encodeURIComponent(command)}`);
          if (!response.ok) {
            throw new Error('Failed to fetch command output');
          }
          const data = await response.json();
          setOutput(data.output);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchOutput();
  }, [action, demoId]);

  if (!action) return null;

  // Get action name for display
  const actionName = getActionName(action);

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

        {/* Output section - now shown for all action types */}
        <div className="mb-6">
          <div className="space-y-3">
            <div className="flex">
              <span className="w-[100px] text-gray-500 text-sm">Output</span>
            </div>
            <div>
              {loading ? (
                <div className="mt-1 bg-gray-100 p-3 rounded text-xs text-gray-500">
                  Loading command output...
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

// Color legend component
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

// Main Timeline component
function Timeline({ data }) {
  const [viewportWidth, setViewportWidth] = useState(0);
  const [selectedAction, setSelectedAction] = useState(null);
  const timelineRef = useRef(null);

  const { actions = [], id: demoId } = data;

  // Calculate number of lines needed
  const linesNeeded = Math.ceil(actions.length / ACTIONS_PER_LINE);

  // Resize handler for responsive timeline
  useEffect(() => {
    const handleResize = () => {
      if (timelineRef.current) {
        setViewportWidth(timelineRef.current.clientWidth);
      }
    };

    handleResize(); // Initial size
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Automatically select the first action when timeline data is loaded
  useEffect(() => {
    if (actions.length > 0) {
      setSelectedAction(actions[0]);
    }
  }, [data]);

  return (
    <div className="flex flex-col h-full p-4">
      {/* Header with title and legend */}
      <div className="flex items-center justify-between py-2 mb-4">
        <div className="flex items-center">
          <span className="mr-4 font-medium text-sm">{data.name}</span>
          <span className="text-sm">{actions.length} actions</span>
        </div>
        <ColorLegend />
      </div>

      {/* Timeline visualization and details */}
      <div className="flex flex-col">
        <div className="overflow-x-auto relative [scrollbar-height:8px] [scrollbar-track-color:#f1f1f1] [scrollbar-thumb-color:#c1c1c1] [scrollbar-thumb-radius:4px] [scrollbar-thumb-hover-color:#a0a0a0]">
          <div
            className="bg-gray-100 relative rounded mb-4"
            ref={timelineRef}
            style={{
              width: '100%',
              height: `${linesNeeded * LINE_HEIGHT}px`,
              position: 'relative'
            }}
          >
            {actions.map((action, index) => {
              const lineIndex = Math.floor(index / ACTIONS_PER_LINE);

              return (
                <ActionItem
                  key={index}
                  action={action}
                  index={index}
                  viewportWidth={viewportWidth}
                  actionsLength={actions.length}
                  lineIndex={lineIndex}
                  onClick={setSelectedAction}
                  isSelected={selectedAction === action}
                />
              );
            })}
          </div>
        </div>

        {/* Action details panel */}
        {selectedAction && (
          <ActionDetails
            action={selectedAction}
            onClose={() => setSelectedAction(null)}
            demoId={demoId}
          />
        )}
      </div>
    </div>
  );
}

export default Timeline;
