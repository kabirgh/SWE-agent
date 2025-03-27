import React from 'react';
import { useChat } from '@ai-sdk/react';

function ChatPane({ contextData }) {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    body: {
      // Pass timeline context to the API
      contextData
    }
  });

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-800">Chat Assistant</h2>
        <p className="text-sm text-gray-500">Ask about the timeline data</p>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-4">
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
            <div className="text-sm">{message.content}</div>
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

      <div className="p-4 border-t border-gray-200">
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
