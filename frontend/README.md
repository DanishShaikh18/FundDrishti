# FundDrishti Frontend

A lightning-fast, highly visual fraud investigation console built with React.

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **react-router-dom** - Navigation
- **Cytoscape** - Transaction network visualization
- **Recharts** - Data visualization (radar charts)
- **Axios** - HTTP client

## Features

- 📊 **Alert Dashboard** - Real-time fraud alerts with advanced filtering
- 🔍 **Case Investigation** - Drill-down into individual cases
- 🌐 **Transaction Network** - Interactive node-link graph visualization
- 📈 **Behavioral Radar** - 8-axis profile comparison charts
- 🎨 **Dark Enterprise UI** - High-contrast, WCAG 2.1 AA compliant

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

The app will start on `http://localhost:3000` and proxy API requests to `http://localhost:8000`.

## Build

```bash
npm run build
```

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── components/        # React components
├── pages/             # Route pages
├── services/          # API client
├── hooks/             # Custom React hooks
├── context/           # Global state
├── utils/             # Helpers and constants
└── styles/            # CSS files
```

## API Integration

The frontend connects to the FastAPI backend via:

- `GET /alerts` - Fetch all fraud alerts
- `GET /cases/{case_id}` - Get case details
- `PUT /cases/{case_id}/status` - Update case status

See [Technical_Specification.md](../../production_artifacts/Technical_Specification.md) for full API contracts.
