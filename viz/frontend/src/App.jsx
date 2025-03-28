import React, { useState, useEffect } from 'react';
import DemoList from './components/DemoList';
import Timeline from './components/Timeline';
import ChatPane from './components/ChatPane';

function App() {
  const [demos, setDemos] = useState([]);
  const [selectedDemo, setSelectedDemo] = useState(null);
  const [timelineData, setTimelineData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch the list of available demos
  useEffect(() => {
    async function fetchDemos() {
      try {
        const response = await fetch('/api/demos');
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setDemos(data);
      } catch (error) {
        console.error('Error fetching demos:', error);
        setError('Failed to load demos.');
      }
    }

    fetchDemos();
  }, []);

  // Load timeline data when a demo is selected
  const handleDemoSelect = async (demoId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/demos/${demoId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      setSelectedDemo(demoId);
      setTimelineData(data);
    } catch (error) {
      console.error('Error fetching timeline data:', error);
      setError('Failed to load timeline data.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-5 sticky top-0 z-10 shadow-sm">
        <h1 className="text-xl font-medium text-blue-600">Visualizer</h1>
      </header>

      <main className="flex flex-1 overflow-hidden">
        <aside className="w-72 border-r border-gray-200 flex-shrink-0 overflow-y-auto">
          <DemoList
            demos={demos}
            onSelectDemo={handleDemoSelect}
            selectedDemo={selectedDemo}
          />
        </aside>

        <section className="flex-1 overflow-auto">
          {loading && <div className="flex justify-center items-center h-full text-gray-500">Loading...</div>}
          {error && <div className="flex justify-center items-center h-full text-red-500 p-5 text-center">{error}</div>}
          {!loading && !error && timelineData && (
            <Timeline
              data={timelineData}
            />
          )}
          {!loading && !error && !timelineData && (
            <div className="flex justify-center items-center h-full text-gray-500 p-5 text-center">
              <p>Select a demo from the list to view its timeline.</p>
            </div>
          )}
        </section>

        {timelineData && (
          <aside className="w-96 border-l border-gray-200 flex-shrink-0 flex flex-col overflow-hidden">
            <ChatPane
              key={selectedDemo}
              contextData={timelineData}
            />
          </aside>
        )}
      </main>
    </div>
  );
}

export default App;
