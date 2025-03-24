#!/bin/bash

# Start the backend
echo "Starting backend server..."
cd backend
fastapi dev main.py &
BACKEND_PID=$!

# Start the frontend
echo "Starting frontend development server..."
cd ../frontend
pnpm run dev &
FRONTEND_PID=$!

# Handle shutdown
function cleanup {
  echo "Shutting down servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit 0
}

trap cleanup SIGINT

echo "Both servers are running!"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both servers"

# Keep script running
wait
