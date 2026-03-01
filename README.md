# Travel & Event Concierge - A2A Multi-Agent Demo

> **DISCLAIMER: THIS IS NOT AN OFFICIALLY SUPPORTED GOOGLE PRODUCT. THIS PROJECT IS INTENDED FOR DEMONSTRATION PURPOSES ONLY.**

A Travel & Event Concierge that orchestrates **5 specialized agents** across **3 different frameworks** using the [A2A (Agent-to-Agent) protocol](https://github.com/google/A2A). The concierge agent (Google ADK) delegates tasks to remote agents deployed on Cloud Run, coordinating hotel, flight, train, event ticket, and restaurant reservations across Europe.

Includes a **Pixel Art visualization UI** showing real-time agent orchestration with animated characters, traveling envelopes, and speech bubbles.

## Architecture

```
                        Vertex AI Agent Engine
                     ┌──────────────────────────┐
                     │   Purchasing Concierge    │
                     │      (Google ADK)         │
                     │     Gemini 2.5 Flash      │
                     └─────────┬────────────────┘
                               │ A2A Protocol
          ┌──────────┬─────────┼─────────┬──────────┐
          │          │         │         │          │
     ┌────▼───┐ ┌───▼────┐ ┌──▼───┐ ┌───▼───┐ ┌───▼────────┐
     │ Hotel  │ │ Flight │ │Train │ │Ticket │ │ Restaurant │
     │LangGr. │ │ CrewAI │ │LangG.│ │CrewAI │ │ Google GenAI│
     └────────┘ └────────┘ └──────┘ └───────┘ └────────────┘
          Cloud Run (5 services)
```

| Agent | Framework | Description |
|-------|-----------|-------------|
| Hotel | LangGraph | Hotel reservations across European cities |
| Flight | CrewAI | Flight booking and search |
| Train | LangGraph | Train ticket reservations |
| Ticket | CrewAI | Event tickets (sports, concerts, theatre) |
| Restaurant | Google GenAI | Restaurant reservations |

## Two UIs Available

### 1. Pixel Art Visualization UI (recommended)

Split-screen interface with chat on the left and animated pixel art canvas on the right, showing the concierge coordinating agents in real-time.

```bash
uv run python pixel_ui_server.py
# Open http://localhost:8080
```

### 2. Gradio Chat UI

Simple chat interface powered by Gradio.

```bash
uv run python purchasing_concierge_ui.py
# Open http://localhost:8080
```

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- Google Cloud project with Vertex AI API enabled
- `gcloud` CLI authenticated

```bash
gcloud auth application-default login
gcloud services enable aiplatform.googleapis.com
```

Install uv and dependencies:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12
uv sync
```

## Deployment

### 1. Deploy Remote Agents to Cloud Run

```bash
bash deploy_agents_cloudrun.sh
```

This deploys all 5 agents. Note the URLs printed for each service.

### 2. Configure Environment

Create a `.env` file at the root:

```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT={your-project-id}
GOOGLE_CLOUD_LOCATION=us-central1
STAGING_BUCKET=gs://travel-concierge-{your-project-id}
HOTEL_AGENT_URL=https://hotel-agent-XXXXX.us-central1.run.app
FLIGHT_AGENT_URL=https://flight-agent-XXXXX.us-central1.run.app
TRAIN_AGENT_URL=https://train-agent-XXXXX.us-central1.run.app
TICKET_AGENT_URL=https://ticket-agent-XXXXX.us-central1.run.app
RESTAURANT_AGENT_URL=https://restaurant-agent-XXXXX.us-central1.run.app
```

### 3. Deploy Concierge to Agent Engine

```bash
gcloud storage buckets create gs://travel-concierge-{your-project-id} --location=us-central1
uv run python deploy_to_agent_engine.py
```

Add the printed resource name to your `.env`:

```bash
AGENT_ENGINE_RESOURCE_NAME=projects/{id}/locations/us-central1/reasoningEngines/{id}
```

### 4. Launch the UI

```bash
uv run python pixel_ui_server.py
```

## Covered Cities

Madrid, Barcelona, Paris, London, Rome.

## Project Structure

```
A2A-Agent-Engine/
├── pixel_ui_server.py              # Pixel Art UI backend (FastAPI + WebSocket)
├── purchasing_concierge_ui.py      # Gradio chat UI
├── deploy_to_agent_engine.py       # Deploy concierge to Vertex AI
├── deploy_agents_cloudrun.sh       # Deploy remote agents to Cloud Run
├── purchasing_concierge/           # Concierge agent (Google ADK)
│   ├── agent.py                    # Agent factory
│   ├── purchasing_agent.py         # Orchestrator logic
│   └── remote_agent_connection.py  # A2A client wrapper
├── static/                         # Pixel Art UI frontend
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── sprites.js              # Pixel art character sprites
│       ├── animation.js            # Canvas animation engine
│       ├── chat.js                 # Chat panel
│       └── app.js                  # WebSocket + event routing
└── remote_travel_agents/           # 5 remote agents
    ├── hotel_agent/                # LangGraph
    ├── flight_agent/               # CrewAI
    ├── train_agent/                # LangGraph
    ├── ticket_agent/               # CrewAI
    └── restaurant_agent/           # Google GenAI
```
