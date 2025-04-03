import React, { useState, useEffect, useRef } from 'react';
import ActionDetails from './ActionDetails';
import ColorLegend from './ColorLegend';
import { ACTIONS_PER_LINE, LINE_HEIGHT } from './constants';
import Timeline from './Timeline';

function TrajectoryView({ trajectoryData, selectedTrajectoryId }) {
  const [viewportWidth, setViewportWidth] = useState(0);
  const [selectedStep, setSelectedStep] = useState(null);
  const timelineContainerRef = useRef(null);

  const steps = trajectoryData?.trajectory || [];
  const stepsLength = steps.length;

  // Calculate number of lines needed based on steps
  const linesNeeded = Math.ceil(stepsLength / ACTIONS_PER_LINE);

  // Resize handler for responsive timeline
  useEffect(() => {
    const handleResize = () => {
      if (timelineContainerRef.current) {
        setViewportWidth(timelineContainerRef.current.clientWidth);
      }
    };

    handleResize();
    const timeoutId = setTimeout(handleResize, 50);

    window.addEventListener('resize', handleResize);
    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('resize', handleResize);
    };
  }, [stepsLength]);

  // Automatically select the first step when trajectory data is loaded
  useEffect(() => {
    if (steps.length > 0) {
      setSelectedStep(steps[0]);
    } else {
      setSelectedStep(null);
    }
  }, [trajectoryData]);

  // Handle potential null trajectoryData during loading or error states
  if (!trajectoryData) {
    return null;
  }

  // Function to handle step selection, passed down to Timeline
  const handleStepSelect = (step) => {
    setSelectedStep(step);
  };

  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex items-center justify-between py-2 mb-4">
        <div className="flex items-center">
          <span className="mr-4 font-medium text-sm">{selectedTrajectoryId}</span>
          <span className="text-sm">{stepsLength} steps</span>
        </div>
        <ColorLegend />
      </div>

      <div className="flex flex-col flex-1 overflow-hidden">
        <div
          ref={timelineContainerRef}
          className="overflow-x-auto relative mb-4 [scrollbar-height:8px] [scrollbar-track-color:#f1f1f1] [scrollbar-thumb-color:#c1c1c1] [scrollbar-thumb-radius:4px] [scrollbar-thumb-hover-color:#a0a0a0]"
          style={{ height: `${linesNeeded * LINE_HEIGHT}px` }}
        >
          {viewportWidth > 0 && (
            <Timeline
              steps={steps}
              selectedStep={selectedStep}
              onStepSelect={handleStepSelect}
              viewportWidth={viewportWidth}
              stepsLength={stepsLength}
              ACTIONS_PER_LINE={ACTIONS_PER_LINE}
              LINE_HEIGHT={LINE_HEIGHT}
            />
          )}
        </div>

        {selectedStep && (
          <div className="flex-1 overflow-y-auto">
            <ActionDetails
              step={selectedStep}
              onClose={() => setSelectedStep(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default TrajectoryView;
