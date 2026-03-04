"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import uuid
from typing import List
import httpx

from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from .remote_agent_connection import RemoteAgentConnections

from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    Part,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)


class PurchasingAgent:
    """The purchasing agent.

    This is the agent responsible for choosing which remote seller agents to send
    tasks to and coordinate their work.
    """

    def __init__(
        self,
        remote_agent_addresses: List[str],
    ):
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.remote_agent_addresses = remote_agent_addresses
        self.cards: dict[str, AgentCard] = {}
        self.agents = ""
        self.a2a_client_init_status = False

    def create_agent(self) -> Agent:
        return Agent(
            model="gemini-2.5-flash",
            name="purchasing_agent",
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            before_agent_callback=self.before_agent_callback,
            description=(
                "Travel & Event concierge that orchestrates hotel, flight, train, event ticket,"
                " restaurant reservations, merchandise and shopping (clothing, formal wear, fan shop) orders across Europe via specialized agents."
            ),
            tools=[
                self.send_task,
            ],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        current_agent = self.check_active_agent(context)
        return f"""You are an expert travel, event and shopping concierge that orchestrates travel planning, reservations and product purchases across Europe.
You delegate user requests to the appropriate specialized remote agents: hotels, flights, trains, event tickets, restaurants, and merchandise/shopping (football fan items AND clothing/formal wear: shirts, suits, tuxedos, ties, shoes, etc.).

Covered cities: Madrid, Barcelona, Paris, London, Rome.

# Context enrichment rules (CRITICAL):
Each remote agent is STATELESS and has NO access to your conversation history.
You MUST write COMPLETE, SELF-CONTAINED task descriptions that include ALL necessary information.
- ALWAYS include the user's full name in EVERY task sent to any agent.
- ALWAYS include the city, dates, and number of travelers/guests.
- For restaurant: city, date, time (pick a reasonable default if not specified), party size, guest full name, dietary preferences if mentioned.
- For hotel: city, check-in date, check-out date, number of guests, guest full name, room preferences if mentioned.
- For flight: origin city, destination city, departure date, passenger full name, cabin class (default Economy), return date if mentioned.
- For train: origin city, destination city, travel date, passenger full name, class (default Standard), return date if mentioned.
- For tickets: event type/name, city, date, number of tickets, attendee full name, seating preference if mentioned.
- For merchandise: item name(s), size(s) (including suit size, shirt size, shoe size if applicable), quantity, customer full name, custom printing details if mentioned, clothing/formal wear preferences if mentioned.
- Write task descriptions as complete standalone requests that the agent can process WITHOUT asking follow-up questions.

# Execution:
- For actionable tasks, use `send_task` to assign tasks to the appropriate remote agents.
- When a user request involves multiple services (e.g. "book a flight, hotel, restaurant and match ticket", or "reserve a restaurant and buy me a white shirt"),
    delegate to ALL relevant agents simultaneously without asking for user permission. Send each task with only the relevant context for that agent.
- Never ask user permission when you want to connect with remote agents. If you need to make connections with multiple remote agents, directly
    connect with them without asking user permission or preferences.
- Always show the detailed response information from each agent and propagate it properly to the user.
- If a remote agent is asking for more information, enrich the task with information from the conversation history and resend.
- If the user already confirmed in the past conversation history, you can confirm on behalf of the user.
- Do not give irrelevant context to a remote agent. For example, hotel details are not relevant for the flight agent.
- Never ask booking confirmation to the remote agent.
- After all agents have responded, present a complete itinerary summary to the user with all bookings, references, and total costs.
- For ANY shopping/purchasing request — including clothing, formal wear, shirts, suits, tuxedos, ties, bow ties, shoes, pocket squares, as well as football merchandise (jerseys, scarves, caps, souvenirs) — ALWAYS delegate to the merchandise_agent. The merchandise agent handles ALL product purchases, not just football items.

Please rely on tools to address the request, and don't make up the response. If you are not sure, please ask the user for more details.
Focus on the most recent parts of the conversation primarily.

# Language:
ALWAYS respond in the same language the user is using. If the user writes in French, respond in French. If in Spanish, respond in Spanish. Match the user's language at all times.

If there is an active agent, send the request to that agent with the update task tool.

Agents:
{self.agents}

Current active agent: {current_agent["active_agent"]}
"""

    def check_active_agent(self, context: ReadonlyContext):
        state = context.state
        if (
            "session_id" in state
            and "session_active" in state
            and state["session_active"]
            and "active_agent" in state
        ):
            return {"active_agent": f"{state['active_agent']}"}
        return {"active_agent": "None"}

    async def before_agent_callback(self, callback_context: CallbackContext):
        if not self.a2a_client_init_status:
            httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(timeout=30))
            for address in self.remote_agent_addresses:
                card_resolver = A2ACardResolver(
                    base_url=address, httpx_client=httpx_client
                )
                try:
                    card = await card_resolver.get_agent_card()
                    remote_connection = RemoteAgentConnections(
                        agent_card=card, agent_url=address
                    )
                    self.remote_agent_connections[card.name] = remote_connection
                    self.cards[card.name] = card
                except Exception as e:
                    print(f"ERROR: Failed to get agent card from {address}: {type(e).__name__}: {e}")
            agent_info = []
            for ra in self.list_remote_agents():
                agent_info.append(json.dumps(ra))
            self.agents = "\n".join(agent_info)
            self.a2a_client_init_status = True

    async def before_model_callback(
        self, callback_context: CallbackContext, llm_request
    ):
        state = callback_context.state
        if "session_active" not in state or not state["session_active"]:
            if "session_id" not in state:
                state["session_id"] = str(uuid.uuid4())
            state["session_active"] = True

    def list_remote_agents(self):
        """List the available remote agents you can use to delegate the task."""
        if not self.remote_agent_connections:
            return []

        remote_agent_info = []
        for card in self.cards.values():
            print(f"Found agent card: {card.model_dump()}")
            print("=" * 100)
            remote_agent_info.append(
                {"name": card.name, "description": card.description}
            )
        return remote_agent_info

    def send_task(self, agent_name: str, task: str, tool_context: ToolContext):
        """Sends a task to a remote specialized agent.

        IMPORTANT: The remote agent is STATELESS and has NO access to conversation history.
        The task parameter must be a COMPLETE, SELF-CONTAINED description including ALL
        necessary details (user name, city, dates, quantities, preferences, etc.) so the
        remote agent can process it without asking follow-up questions.

        Args:
            agent_name: The name of the agent to send the task to.
            task: A complete, self-contained task description with all required details.
                Must include user name, relevant dates, city, and all domain-specific
                parameters so the agent can act immediately.
            tool_context: The tool context this method runs in.

        Returns:
            A dictionary with agent_name, status, and response text.
        """
        if agent_name not in self.remote_agent_connections:
            available = list(self.remote_agent_connections.keys())
            return {
                "agent_name": agent_name,
                "status": "error",
                "response": f"Agent '{agent_name}' not found. Available agents: {available}",
            }
        state = tool_context.state
        state["active_agent"] = agent_name
        client = self.remote_agent_connections[agent_name]
        if not client:
            return {
                "agent_name": agent_name,
                "status": "error",
                "response": f"Client not available for {agent_name}",
            }
        session_id = state["session_id"]
        message_id = ""
        metadata = {}
        if "input_message_metadata" in state:
            metadata.update(**state["input_message_metadata"])
            if "message_id" in state["input_message_metadata"]:
                message_id = state["input_message_metadata"]["message_id"]
        if not message_id:
            message_id = str(uuid.uuid4())

        payload = {
            "message": {
                "role": "user",
                "parts": [
                    {"type": "text", "text": task}
                ],
                "messageId": message_id,
                "contextId": session_id,
            },
        }

        message_request = SendMessageRequest(
            id=message_id, params=MessageSendParams.model_validate(payload)
        )

        try:
            send_response: SendMessageResponse = client.send_message(
                message_request=message_request
            )
        except Exception as e:
            print(f"ERROR calling {agent_name}: {type(e).__name__}: {e}")
            return {
                "agent_name": agent_name,
                "status": "error",
                "response": f"Failed to contact {agent_name}: {type(e).__name__}: {e}",
            }

        print(
            "send_response",
            send_response.model_dump_json(exclude_none=True, indent=2),
        )

        if not isinstance(send_response.root, SendMessageSuccessResponse):
            error_detail = send_response.model_dump_json(exclude_none=True)
            print(f"Non-success response from {agent_name}: {error_detail}")
            return {
                "agent_name": agent_name,
                "status": "error",
                "response": f"Agent {agent_name} returned an error: {error_detail}",
            }

        if not isinstance(send_response.root.result, Task):
            print(f"Non-task response from {agent_name}: {type(send_response.root.result)}")
            return {
                "agent_name": agent_name,
                "status": "error",
                "response": f"Agent {agent_name} returned unexpected response type: {type(send_response.root.result).__name__}",
            }

        task_result = send_response.root.result

        # Extract text from artifacts so the model gets a clear response
        response_text = ""
        if task_result.artifacts:
            for artifact in task_result.artifacts:
                for part in artifact.parts:
                    if part.root and hasattr(part.root, "text") and part.root.text:
                        response_text += part.root.text + "\n"

        # Fallback to status message
        if not response_text and task_result.status and task_result.status.message:
            for part in task_result.status.message.parts:
                if part.root and hasattr(part.root, "text") and part.root.text:
                    response_text += part.root.text + "\n"

        return {
            "agent_name": agent_name,
            "status": task_result.status.state.value if task_result.status else "unknown",
            "response": response_text.strip() or "No response from agent.",
        }


def convert_parts(parts: list[Part], tool_context: ToolContext):
    rval = []
    for p in parts:
        rval.append(convert_part(p, tool_context))
    return rval


def convert_part(part: Part, tool_context: ToolContext):
    # Currently only support text parts
    if part.type == "text":
        return part.text

    return f"Unknown type: {part.type}"
