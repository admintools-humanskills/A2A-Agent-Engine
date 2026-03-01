# Elevate Concierge - A2A Multi-Agent Travel Platform

> **DISCLAIMER: THIS IS NOT AN OFFICIALLY SUPPORTED GOOGLE PRODUCT. THIS PROJECT IS INTENDED FOR DEMONSTRATION PURPOSES ONLY.**

A Travel & Event Concierge that orchestrates **6 specialized agents** across **3 different frameworks** using the [A2A (Agent-to-Agent) protocol](https://github.com/google/A2A). The concierge agent (Google ADK on Vertex AI) delegates tasks to remote agents deployed on Cloud Run, coordinating hotel, flight, train, event ticket, restaurant, and merchandise reservations across Europe.

Includes a **Final Fantasy 2 NES-style pixel art UI** showing real-time agent orchestration with animated characters, black outlines, directional sprites, walk cycles, and speech bubbles.

![Elevate Concierge - Pixel Art UI](docs/screenshot.png)

## Architecture

```
                        Vertex AI Agent Engine
                     ┌──────────────────────────┐
                     │   Purchasing Concierge    │
                     │      (Google ADK)         │
                     │     Gemini 2.5 Flash      │
                     └─────────┬────────────────┘
                               │ A2A Protocol
          ┌──────────┬─────────┼──────────┬──────────┬──────────┐
          │          │         │          │          │          │
     ┌────▼───┐ ┌───▼────┐ ┌──▼───┐ ┌────▼───┐ ┌───▼──────┐ ┌▼─────────┐
     │ Hotel  │ │ Flight │ │Train │ │ Ticket │ │Restaurant│ │   Shop   │
     │LangGr. │ │ CrewAI │ │LangG.│ │ CrewAI │ │  GenAI   │ │  GenAI   │
     └────────┘ └────────┘ └──────┘ └────────┘ └──────────┘ └──────────┘
                      Cloud Run (6 services)
```

| Agent | Framework | Description |
|-------|-----------|-------------|
| Hotel | LangGraph | Hotel reservations across European cities |
| Flight | CrewAI | Flight booking and search |
| Train | LangGraph | Train ticket reservations |
| Ticket | CrewAI | Event tickets (sports, concerts, theatre) |
| Restaurant | Google GenAI | Restaurant reservations |
| Merchandise | Google GenAI | Fan shop merchandise (jerseys, scarves, collectibles) |

## Pixel Art Visualization

The main UI features a split-screen interface: chat on the left, animated pixel art village on the right. When you send a message, the concierge character walks to the relevant agent's building, triggers a reaction, and returns to the plaza with the response.

**Visual style:**
- NES-authentic color palette (~35 colors)
- Black pixel outlines on all sprites and buildings
- 4-frame walk cycle with directional sprites (face, left, right, back)
- Ground shadows and idle bobbing animation
- Three ground types: cobblestone paths, dirt around buildings, grass in open areas
- Roof textures, window frames, and building details

## Two UIs Available

### 1. Pixel Art Visualization UI (recommended)

```bash
uv run python pixel_ui_server.py
# Open http://localhost:8080
```

### 2. Gradio Chat UI

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

This deploys all 6 agents. Note the URLs printed for each service.

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
MERCHANDISE_AGENT_URL=https://merchandise-agent-XXXXX.us-central1.run.app
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
│   ├── purchasing_agent.py         # Orchestrator logic + send_task tool
│   └── remote_agent_connection.py  # A2A client wrapper
├── static/                         # Pixel Art UI frontend
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── sprites.js              # NES palette, buildings, character sprites
│       ├── animation.js            # Canvas engine, walker, NPC patrols
│       ├── chat.js                 # Chat panel
│       └── app.js                  # WebSocket + event routing
├── docs/
│   └── screenshot.png              # UI screenshot
└── remote_travel_agents/           # 6 remote agents
    ├── hotel_agent/                # LangGraph
    ├── flight_agent/               # CrewAI
    ├── train_agent/                # LangGraph
    ├── ticket_agent/               # CrewAI
    ├── restaurant_agent/           # Google GenAI
    └── merchandise_agent/          # Google GenAI
```
