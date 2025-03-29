import React from 'react';
import { useChat } from '@ai-sdk/react';
import ReactMarkdown from 'react-markdown';

function ChatPane({ contextData, contextId }) {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    body: {
      // Pass both trajectoryData and trajectoryId to the API
      contextData, // This is trajectoryData
      contextId,   // This is selectedTrajectoryId
    }
  });

  // Custom styles for markdown content
  const markdownStyles = {
    pre: {
      overflowX: 'auto',
      whiteSpace: 'pre-wrap',
      wordWrap: 'break-word',
      maxWidth: '100%',
    },
    code: {
      overflowX: 'auto',
      whiteSpace: 'pre-wrap',
      wordWrap: 'break-word',
      maxWidth: '100%',
    }
  };

  return (
    <div className="grid grid-rows-[auto_1fr_auto] h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex-shrink-0">
        <h2 className="text-lg font-medium text-gray-800">Chat</h2>
      </div>

      {/* Messages container */}
      <div className="overflow-y-auto min-h-0">
        <div className="p-4 space-y-4">
          {messages.map(message => (
            <div
              key={message.id}
              className={`p-3 rounded-lg ${message.role === 'user'
                ? 'bg-blue-100 ml-8'
                : 'bg-gray-100 mr-8'
                }`}
            >
              <div className="font-semibold text-xs text-gray-500 mb-1">
                {message.role === 'user' ? 'You' : 'Assistant'}
              </div>
              <div className="text-sm prose prose-sm max-w-none">
                <ReactMarkdown
                  components={{
                    pre: ({ node, ...props }) => <pre style={markdownStyles.pre} {...props} />,
                    code: ({ node, ...props }) => <code style={markdownStyles.code} {...props} />
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="p-3 rounded-lg bg-gray-100 mr-8">
              <div className="font-semibold text-xs text-gray-500 mb-1">
                Assistant
              </div>
              <div className="text-sm">Thinking...</div>
            </div>
          )}
        </div>
      </div>

      {/* Input area - will always be at the bottom */}
      <div className="p-4 border-t border-gray-200 bg-white flex-shrink-0">
        <form onSubmit={handleSubmit} className="flex">
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            placeholder="Ask about the timeline..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-r-md hover:bg-blue-700 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-blue-400"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatPane;
