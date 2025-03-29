// Action types
export const VIEW_FILE = 'View file/folder';
export const EDIT_FILE = 'Edit file';
export const CREATE_FILE = 'Create file';
export const STR_REPLACE_EDITOR = 'str_replace_editor';
export const BASH = 'Bash';
export const FIND_GREP = 'Find/grep';
export const SUBMIT = 'Submit';
export const UNKNOWN = 'Unknown';

// Cache key for localStorage
export const COMMAND_OUTPUTS_CACHE_KEY = 'command_outputs_cache';

// Color mapping for different action types
export const ACTION_COLORS = {
  [VIEW_FILE]: '#0D47A1',      // Dark blue
  [EDIT_FILE]: '#66BB6A',      // Light green
  [CREATE_FILE]: '#2E7D32',    // Dark green
  [STR_REPLACE_EDITOR]: '#1B5E20', // Darkest green
  [BASH]: '#F4B400',           // Yellow
  [FIND_GREP]: '#2196F3',      // Medium blue
  [SUBMIT]: '#D32F2F',         // Red
  'default': '#757575'         // Grey (for unknown action types)
};

// Layout constants
export const ACTIONS_PER_LINE = 50;
export const LINE_HEIGHT = 30;
