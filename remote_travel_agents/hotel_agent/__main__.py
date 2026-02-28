from a2a.types import AgentCapabilities, AgentSkill, AgentCard
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.server.tasks import InMemoryTaskStore
from agent import HotelReservationAgent
from agent_executor import HotelAgentExecutor
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
@click.option("--port", "port", default=10002)
def main(host, port):
    """Entry point for the A2A + LangGraph Hotel Reservation Agent."""
    try:
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="hotel_reservation",
            name="Hotel Reservation Tool",
            description="Reserves hotel rooms in major European cities (Madrid, Barcelona, Paris, London, Rome). Knows room types, prices, amenities and availability.",
            tags=["hotel", "reservation", "travel", "accommodation"],
            examples=["I need a hotel in Madrid for 3 nights", "What hotels are available in Paris?"],
        )
        agent_host_url = (
            os.getenv("HOST_OVERRIDE")
            if os.getenv("HOST_OVERRIDE")
            else f"http://{host}:{port}/"
        )
        agent_card = AgentCard(
            name="hotel_reservation_agent",
            description="Reserves hotel rooms in major European cities (Madrid, Barcelona, Paris, London, Rome). Knows room types, prices, amenities and availability.",
            url=agent_host_url,
            version="1.0.0",
            defaultInputModes=HotelReservationAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=HotelReservationAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=HotelAgentExecutor(),
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
