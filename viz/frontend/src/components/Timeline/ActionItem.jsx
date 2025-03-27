import React from 'react';
import { getActionName } from './utils';
import { ACTION_COLORS, ACTIONS_PER_LINE, LINE_HEIGHT } from './constants';

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

export default ActionItem;
