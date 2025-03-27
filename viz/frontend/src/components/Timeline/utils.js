import { VIEW_FILE, CREATE_FILE, EDIT_FILE, FIND_GREP, UNKNOWN, STR_REPLACE_EDITOR, COMMAND_OUTPUTS_CACHE_KEY } from './constants';

// Function to determine the actual action name
export const getActionName = (action) => {
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

// Function to fetch and cache command outputs
export const fetchAndCacheCommandOutputs = async (actions, demoId) => {
  // Try to get cached data first
  const cachedData = localStorage.getItem(COMMAND_OUTPUTS_CACHE_KEY);
  if (cachedData) {
    try {
      const parsed = JSON.parse(cachedData);
      // Check if we have data for this demo
      if (parsed[demoId]) {
        return parsed[demoId];
      }
    } catch (e) {
      console.error('Error parsing cached command outputs:', e);
    }
  }

  // If no cache or invalid cache, fetch all outputs
  const outputs = {};
  const fetchPromises = actions.map(async (action) => {
    if (!action?.details?.tool_call?.function?.arguments) return;

    try {
      const args = JSON.parse(action.details.tool_call.function.arguments);
      const command = args.command || args.arguments || action.details.tool_call.function.arguments;

      if (command) {
        const response = await fetch(`/api/demos/${demoId}/command-output?command=${encodeURIComponent(command)}`);
        if (!response.ok) {
          throw new Error('Failed to fetch command output');
        }
        const data = await response.json();
        outputs[command] = data.output;
      }
    } catch (err) {
      console.error('Error fetching command output:', err);
      outputs[command] = `Error: ${err.message}`;
    }
  });

  await Promise.all(fetchPromises);

  // Cache the results
  try {
    const existingCache = localStorage.getItem(COMMAND_OUTPUTS_CACHE_KEY);
    const cacheData = existingCache ? JSON.parse(existingCache) : {};
    cacheData[demoId] = outputs;
    localStorage.setItem(COMMAND_OUTPUTS_CACHE_KEY, JSON.stringify(cacheData));
  } catch (e) {
    console.error('Error caching command outputs:', e);
  }

  return outputs;
};
