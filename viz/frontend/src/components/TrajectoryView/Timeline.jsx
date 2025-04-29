import React from 'react';
import ActionItem from './ActionItem';

function Timeline({
  steps,
  selectedStep,
  onStepSelect,
  viewportWidth,
  stepsLength,
  ACTIONS_PER_LINE,
  LINE_HEIGHT
}) {

  if (!steps || stepsLength === 0) {
    return null; // Or a message indicating no steps
  }

  // Calculate number of lines needed based on steps
  // This could also be passed as a prop if calculated in parent
  const linesNeeded = Math.ceil(stepsLength / ACTIONS_PER_LINE);

  return (
    <div
      className="bg-gray-100 relative rounded"
      style={{
        width: '100%', // Takes full width of its container
        height: `${linesNeeded * LINE_HEIGHT}px`,
        position: 'relative' // Needed for absolute positioning of ActionItems
      }}
    >
      {steps.map((step, index) => {
        const lineIndex = Math.floor(index / ACTIONS_PER_LINE);

        return (
          <ActionItem
            key={index}
            step={step}
            index={index}
            viewportWidth={viewportWidth}
            stepsLength={stepsLength}
            lineIndex={lineIndex}
            onClick={onStepSelect} // Use the passed handler
            isSelected={selectedStep === step}
            ACTIONS_PER_LINE={ACTIONS_PER_LINE} // Pass down constants if needed by ActionItem
            LINE_HEIGHT={LINE_HEIGHT}
          />
        );
      })}
    </div>
  );
}

export default Timeline;
