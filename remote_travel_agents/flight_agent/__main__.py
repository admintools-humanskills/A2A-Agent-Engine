from a2a.types import AgentCapabilities, AgentSkill, AgentCard
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.server.tasks import InMemoryTaskStore
from agent import FlightReservationAgent
from agent_executor import FlightAgentExecutor
import uvicorn
from dotenv import load_dotenv
import logging
import os
import click

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", "host", default="0.0.0.0")
@click.option("--port", "port", default=10003)
def main(host, port):
    """Entry point for the A2A + CrewAI Flight Reservation Agent."""
    try:
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="flight_reservation",
            name="Flight Reservation Tool",
            description="Reserves flights between major European cities. Covers Air France, Iberia, Vueling, British Airways, ITA Airways in Economy and Business.",
            tags=["flight", "reservation", "travel", "airline"],
            examples=["I need a flight from Paris to Madrid", "Book a business class flight to London"],
        )
        agent_host_url = (
            os.getenv("HOST_OVERRIDE")
            if os.getenv("HOST_OVERRIDE")
            else f"http://{host}:{port}/"
        )
        agent_card = AgentCard(
            name="flight_reservation_agent",
            description="Reserves flights between major European cities. Covers Air France, Iberia, Vueling, British Airways, ITA Airways in Economy and Business.",
            url=agent_host_url,
            version="1.0.0",
            defaultInputModes=FlightReservationAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=FlightReservationAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=FlightAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        uvicorn.run(server.build(), host=host, port=port)

        logger.info(f"Starting server on {host}:{port}")
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()
