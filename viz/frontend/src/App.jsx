import React, { useState, useEffect } from 'react';
import TrajectoryList from './components/TrajectoryList';
import Timeline from './components/Timeline';
import ChatPane from './components/ChatPane';

function App() {
  const [trajectories, setTrajectories] = useState([]);
  const [selectedTrajectoryId, setSelectedTrajectoryId] = useState(null);
  const [trajectoryData, setTrajectoryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch the list of available trajectories
  useEffect(() => {
    async function fetchTrajectories() {
      try {
        const response = await fetch('/api/trajectories');
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setTrajectories(data);
      } catch (error) {
        console.error('Error fetching trajectories:', error);
        setError('Failed to load trajectories.');
      }
    }

    fetchTrajectories();
  }, []);

  // Load trajectory data when a trajectory is selected
  const handleTrajectorySelect = async (trajectoryId) => {
    setLoading(true);
    setError(null);
    setTrajectoryData(null);

    try {
      const response = await fetch(`/api/trajectories/${trajectoryId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      setSelectedTrajectoryId(trajectoryId);
      setTrajectoryData(data);
    } catch (error) {
      console.error('Error fetching trajectory data:', error);
      setError('Failed to load trajectory data.');
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
          <TrajectoryList
            trajectories={trajectories}
            onSelectTrajectory={handleTrajectorySelect}
            selectedTrajectoryId={selectedTrajectoryId}
          />
        </aside>

        <section className="flex-1 overflow-auto">
          {loading && <div className="flex justify-center items-center h-full text-gray-500">Loading...</div>}
          {error && <div className="flex justify-center items-center h-full text-red-500 p-5 text-center">{error}</div>}
          {!loading && !error && trajectoryData && (
            <Timeline
              trajectoryData={trajectoryData}
              selectedTrajectoryId={selectedTrajectoryId}
            />
          )}
          {!loading && !error && !trajectoryData && (
            <div className="flex justify-center items-center h-full text-gray-500 p-5 text-center">
              <p>Select a trajectory from the list to view its timeline.</p>
            </div>
          )}
        </section>

        {trajectoryData && (
          <aside className="w-96 border-l border-gray-200 flex-shrink-0 flex flex-col overflow-hidden">
            <ChatPane
              key={selectedTrajectoryId}
              contextData={trajectoryData}
              contextId={selectedTrajectoryId}
            />
          </aside>
        )}
      </main>
    </div>
  );
}

export default App;
