import React from 'react';
// Import only necessary constants
import { ACTION_COLORS, FIND_GREP, VIEW_FILE, EDIT_FILE, CREATE_FILE, BASH, SUBMIT, UNKNOWN } from './constants';

// Simple function to determine a step type from TrajectoryStep data
const getStepType = (step) => {
  if (step.action) {
    const actionLower = step.action.toLowerCase();
    if (actionLower.startsWith('find') || actionLower.startsWith('grep')) {
      return FIND_GREP;
    } else if (actionLower.startsWith('str_replace_editor view')) {
      return VIEW_FILE;
    } else if (actionLower.startsWith('str_replace_editor str_replace')) {
      return EDIT_FILE;
    } else if (actionLower.startsWith('str_replace_editor create')) {
      return CREATE_FILE;
    } else if (actionLower.startsWith('submit')) {
      return SUBMIT;
    } else {
      return BASH;
    }
  }
  return UNKNOWN;
};

// Destructure ACTIONS_PER_LINE and LINE_HEIGHT from props
const ActionItem = ({
  step,
  index,
  viewportWidth,
  stepsLength,
  lineIndex,
  onClick,
  isSelected,
  ACTIONS_PER_LINE, // Add prop
  LINE_HEIGHT // Add prop
}) => {
  const indexInLine = index % ACTIONS_PER_LINE;

  // Calculate width based on stepsLength using the prop
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
    top: `${lineIndex * LINE_HEIGHT}px`, // Use prop
    width: `${width}px`,
    height: '28px', // Keep fixed height or pass LINE_HEIGHT if needed?
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
      className="absolute cursor-pointer m-[1px]"
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
