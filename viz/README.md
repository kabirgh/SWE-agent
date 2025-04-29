# Agent Timeline Visualizer

A visualization tool for exploring agent actions in YAML files. The application allows you to browse through agent demos and visualize their actions in an interactive timeline.

## Features

- List all agent demos from YAML files
- Interactive timeline visualization similar to Chrome DevTools network panel
- Color-coded action types
- Zoom functionality to focus on specific parts of the timeline
- Detailed view for individual actions

## Stack

- **Backend**: FastAPI
- **Frontend**: React with custom timeline visualization

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm

### Running the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

### Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000

## Development

The project is structured as follows:

```
viz/
├── backend/         # FastAPI application
│   ├── main.py      # API endpoints
│   └── requirements.txt # Python dependencies
├── frontend/        # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── DemoList.jsx       # List of available demos
│   │   │   └── Timeline.jsx       # Timeline visualization
│   │   ├── styles/                # SCSS stylesheets
│   │   ├── App.jsx                # Main application component
│   │   └── main.jsx               # Entry point
```

## Timeline Visualization

The timeline is custom-built without external libraries and features:

- Color-coded segments based on action type
- Zoom controls for detailed inspection
- Action details popup on click
- Responsive design that adapts to screen size
