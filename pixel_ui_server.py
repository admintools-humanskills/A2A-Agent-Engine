"""
Pixel Art Agent Visualization UI - FastAPI Backend

Serves the pixel art split-screen UI and bridges WebSocket connections
to the Vertex AI Agent Engine via stream_query().
"""

import asyncio
import json
import os
import traceback
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pprint import pformat
from vertexai import agent_engines

load_dotenv()

app = FastAPI()

# Serve static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Thread pool for running synchronous stream_query
executor = ThreadPoolExecutor(max_workers=4)

# Agent Engine connection (lazy init per session)
AGENT_ENGINE_RESOURCE = os.getenv("AGENT_ENGINE_RESOURCE_NAME")


def get_agent_engine():
    """Get the Agent Engine instance."""
    return agent_engines.get(AGENT_ENGINE_RESOURCE)


def extract_agent_name(name: str) -> str:
    """Extract a readable agent name from the function call name or args."""
    return name


def summarize_text(text: str, max_len: int = 120) -> str:
    """Truncate text for display."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def run_stream_query(remote_app, user_id: str, session_id: str, message: str, queue: asyncio.Queue, loop):
    """Run stream_query synchronously and push parsed events to the async queue."""
    try:
        # Signal that thinking has started
        asyncio.run_coroutine_threadsafe(
            queue.put({"type": "agent_thinking"}), loop
        )

        last_text = None

        for event in remote_app.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message,
        ):
            parts = event.get("content", {}).get("parts", [])
            if not parts:
                print("[DEBUG] No parts in event, skipping")
                continue

            for part in parts:
                part_type = "unknown"
                if part.get("function_call"):
                    part_type = "function_call"
                elif part.get("function_response"):
                    part_type = "function_response"
                elif part.get("text"):
                    part_type = "text"
                print(f"[DEBUG] Part type={part_type}, keys={list(part.keys())}")

                if part.get("function_call"):
                    fc = part["function_call"]
                    fn_name = fc.get("name", "")
                    fn_args = fc.get("args", {})
                    print(f"[DEBUG] function_call name={fn_name}, agent_name={fn_args.get('agent_name','?')}")

                    # send_task calls contain agent_name and task
                    agent_name = fn_args.get("agent_name", fn_name)
                    task_text = fn_args.get("task", "")

                    msg = {
                        "type": "agent_call",
                        "agent_name": agent_name,
                        "task_summary": summarize_text(task_text),
                    }
                    asyncio.run_coroutine_threadsafe(queue.put(msg), loop)

                elif part.get("function_response"):
                    fr = part["function_response"]
                    fn_name = fr.get("name", "")
                    response_data = fr.get("response", {})
                    print(f"[DEBUG] function_response name={fn_name}, data_keys={list(response_data.keys()) if isinstance(response_data, dict) else type(response_data)}")

                    # Try to extract agent name from function response
                    agent_name = fn_name
                    # If the response has args with agent_name
                    if isinstance(response_data, dict):
                        agent_name = response_data.get("agent_name", fn_name)

                    response_text = pformat(response_data, indent=2, width=80) if isinstance(response_data, dict) else str(response_data)

                    msg = {
                        "type": "agent_response",
                        "agent_name": agent_name,
                        "response_summary": summarize_text(response_text),
                    }
                    asyncio.run_coroutine_threadsafe(queue.put(msg), loop)

                elif part.get("text"):
                    last_text = part["text"]
                    print(f"[DEBUG] text={last_text[:200]}")

        print(f"[DEBUG] Stream finished. last_text={'set' if last_text else 'None'}")
        # Send final text response
        if last_text:
            asyncio.run_coroutine_threadsafe(
                queue.put({"type": "final_response", "text": last_text}), loop
            )
        else:
            asyncio.run_coroutine_threadsafe(
                queue.put({"type": "final_response", "text": "No response from agent."}), loop
            )

    except Exception as e:
        traceback.print_exc()
        asyncio.run_coroutine_threadsafe(
            queue.put({"type": "error", "message": str(e)}), loop
        )

    # Signal completion
    asyncio.run_coroutine_threadsafe(queue.put(None), loop)


@app.get("/")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    # Initialize Agent Engine for this session
    try:
        remote_app = get_agent_engine()
        user_id = "pixel_ui_user"
        session = remote_app.create_session(user_id=user_id)
        session_id = session["id"]
        await ws.send_json({"type": "connected"})
    except Exception as e:
        await ws.send_json({"type": "error", "message": f"Failed to connect to Agent Engine: {e}"})
        await ws.close()
        return

    loop = asyncio.get_event_loop()

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "user_message":
                user_text = msg.get("text", "")
                if not user_text.strip():
                    continue

                queue = asyncio.Queue()

                # Run stream_query in thread pool
                executor.submit(
                    run_stream_query,
                    remote_app, user_id, session_id, user_text, queue, loop,
                )

                # Forward events from queue to WebSocket
                while True:
                    event = await queue.get()
                    if event is None:
                        break
                    await ws.send_json(event)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        traceback.print_exc()
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
