import React, { useState, useEffect, useRef } from 'react';
import ActionItem from './ActionItem';
import ActionDetails from './ActionDetails';
import ColorLegend from './ColorLegend';
import { fetchAndCacheCommandOutputs } from './utils';
import { ACTIONS_PER_LINE, LINE_HEIGHT } from './constants';

// Main Timeline component
function Timeline({ data }) {
  const [viewportWidth, setViewportWidth] = useState(0);
  const [selectedAction, setSelectedAction] = useState(null);
  const [commandOutputs, setCommandOutputs] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const timelineRef = useRef(null);

  const { actions = [], id: demoId } = data;

  // Calculate number of lines needed
  const linesNeeded = Math.ceil(actions.length / ACTIONS_PER_LINE);

  // Fetch command outputs when component mounts
  useEffect(() => {
    const loadCommandOutputs = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const outputs = await fetchAndCacheCommandOutputs(actions, demoId);
        setCommandOutputs(outputs);
      } catch (err) {
        setError(err.message);
        console.error('Error loading command outputs:', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadCommandOutputs();
  }, [actions, demoId]);

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
            commandOutputs={commandOutputs}
            isLoading={isLoading}
            error={error}
          />
        )}
      </div>
    </div>
  );
}

export default Timeline;
