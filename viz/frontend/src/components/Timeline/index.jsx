import React, { useState, useEffect, useRef } from 'react';
import ActionItem from './ActionItem';
import ActionDetails from './ActionDetails';
import ColorLegend from './ColorLegend';
import { ACTIONS_PER_LINE, LINE_HEIGHT } from './constants';

// Main Timeline component - Updated props
function Timeline({ trajectoryData, selectedTrajectoryId }) {
  const [viewportWidth, setViewportWidth] = useState(0);
  const [selectedStep, setSelectedStep] = useState(null); // Renamed state
  const timelineRef = useRef(null);

  // Extract trajectory steps, default to empty array if not present
  const steps = trajectoryData?.trajectory || [];

  // Calculate number of lines needed based on steps
  const linesNeeded = Math.ceil(steps.length / ACTIONS_PER_LINE);

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

  // Automatically select the first step when trajectory data is loaded
  useEffect(() => {
    if (steps.length > 0) {
      setSelectedStep(steps[0]); // Select first step
    } else {
      setSelectedStep(null); // Clear selection if no steps
    }
  }, [trajectoryData]); // Depend on trajectoryData

  // Handle potential null trajectoryData during loading or error states
  if (!trajectoryData) {
    // Optionally render a loading state or null
    // Handled by App.jsx for now
    return null;
  }

  return (
    <div className="flex flex-col h-full p-4">
      {/* Header with title and legend - Updated to use trajectory info */}
      <div className="flex items-center justify-between py-2 mb-4">
        <div className="flex items-center">
          {/* Display selectedTrajectoryId and step count */}
          <span className="mr-4 font-medium text-sm">{selectedTrajectoryId}</span>
          <span className="text-sm">{steps.length} steps</span>
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
            {/* Map over steps instead of actions */}
            {steps.map((step, index) => {
              const lineIndex = Math.floor(index / ACTIONS_PER_LINE);

              return (
                <ActionItem
                  key={index}
                  step={step} // Pass step data
                  index={index}
                  viewportWidth={viewportWidth}
                  stepsLength={steps.length} // Pass total steps length
                  lineIndex={lineIndex}
                  onClick={setSelectedStep} // Update state setter
                  isSelected={selectedStep === step} // Compare with selectedStep
                />
              );
            })}
          </div>
        </div>

        {/* Action details panel - Updated to use selectedStep */}
        {selectedStep && (
          <ActionDetails
            step={selectedStep} // Pass selected step data
            onClose={() => setSelectedStep(null)} // Update state setter
          />
        )}
      </div>
    </div>
  );
}

export default Timeline;
