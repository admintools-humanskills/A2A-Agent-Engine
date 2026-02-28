from a2a.types import AgentCapabilities, AgentSkill, AgentCard
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.server.tasks import InMemoryTaskStore
from agent import RestaurantReservationAgent
from agent_executor import RestaurantAgentExecutor
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
@click.option("--port", "port", default=10006)
def main(host, port):
    """Entry point for the A2A + Google GenAI Restaurant Reservation Agent."""
    try:
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="restaurant_reservation",
            name="Restaurant Reservation Tool",
            description="Reserves tables at restaurants in Madrid, Barcelona, Paris, London and Rome. From tapas bars to 3 Michelin star restaurants.",
            tags=["restaurant", "reservation", "dining", "food"],
            examples=["Book a table at a restaurant in Madrid", "I need a restaurant near the Eiffel Tower for dinner"],
        )
        agent_host_url = (
            os.getenv("HOST_OVERRIDE")
            if os.getenv("HOST_OVERRIDE")
            else f"http://{host}:{port}/"
        )
        agent_card = AgentCard(
            name="restaurant_reservation_agent",
            description="Reserves tables at restaurants in Madrid, Barcelona, Paris, London and Rome. From tapas bars to 3 Michelin star restaurants.",
            url=agent_host_url,
            version="1.0.0",
            defaultInputModes=RestaurantReservationAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=RestaurantReservationAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=RestaurantAgentExecutor(),
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
