import React from 'react';
import { ACTION_COLORS, ACTIONS_PER_LINE, LINE_HEIGHT } from './constants';

// Simple function to determine a step type from TrajectoryStep data
const getStepType = (step) => {
  if (step.action) {
    // Basic check for common command patterns or edit actions
    const actionLower = step.action.toLowerCase();
    if (actionLower.includes('apply_edit') || actionLower.includes('diff') || actionLower.includes('patch')) {
      return 'Edit';
    }
    // Crude check for commands - might need refinement
    if (actionLower.startsWith('bash') || actionLower.startsWith('run') || actionLower.startsWith('{') || actionLower.includes('command')) {
      return 'Command';
    }
    return 'Action'; // Generic action fallback
  }
  if (step.response) {
    return 'Response'; // LLM Response
  }
  if (step.thought) {
    return 'Thought';
  }
  return 'Unknown'; // Fallback for unknown steps
};

// Updated props: step, stepsLength instead of action, actionsLength
const ActionItem = ({ step, index, viewportWidth, stepsLength, lineIndex, onClick, isSelected }) => {
  const indexInLine = index % ACTIONS_PER_LINE;

  // Calculate width based on stepsLength
  const stepsInThisLine = Math.min(ACTIONS_PER_LINE, stepsLength - lineIndex * ACTIONS_PER_LINE);

  const maxWidth = viewportWidth / ACTIONS_PER_LINE;
  const segmentWidth = stepsInThisLine < ACTIONS_PER_LINE
    ? (viewportWidth / ACTIONS_PER_LINE) * (ACTIONS_PER_LINE / stepsInThisLine)
    : viewportWidth / ACTIONS_PER_LINE;

  const actualWidth = Math.min(segmentWidth, maxWidth);

  // Get step type using the new function
  const stepType = getStepType(step);

  // Get color based on the derived stepType
  const color = ACTION_COLORS[stepType] || ACTION_COLORS.default;

  const position = indexInLine * actualWidth;
  const width = actualWidth * 0.95;

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

  // Generate title based on stepType and step.action
  const title = `${stepType}${step.action ? `: ${step.action.substring(0, 100)}...` : ''}`;

  return (
    <div
      className="absolute cursor-pointer transition-all duration-200 m-[1px]"
      style={style}
      onClick={() => onClick(step)} // Pass step object
      title={title} // Use updated title
      data-step-type={stepType} // Use stepType for data attribute
    >
      {isSelected && (
        <div className="absolute inset-0 flex items-center justify-center text-white font-medium">
          {index + 1}
        </div>
      )}
    </div>
  );
};

export default ActionItem;
