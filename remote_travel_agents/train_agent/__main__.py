from a2a.types import AgentCapabilities, AgentSkill, AgentCard
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.server.tasks import InMemoryTaskStore
from agent import TrainReservationAgent
from agent_executor import TrainAgentExecutor
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
@click.option("--port", "port", default=10004)
def main(host, port):
    """Entry point for the A2A + LangGraph Train Reservation Agent."""
    try:
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="train_reservation",
            name="Train Reservation Tool",
            description="Reserves high-speed train tickets in Europe: Eurostar, TGV/SNCF, Renfe AVE, Frecciarossa Trenitalia.",
            tags=["train", "reservation", "travel", "rail"],
            examples=["I need a train from Paris to London", "Book a first class AVE from Madrid to Barcelona"],
        )
        agent_host_url = (
            os.getenv("HOST_OVERRIDE")
            if os.getenv("HOST_OVERRIDE")
            else f"http://{host}:{port}/"
        )
        agent_card = AgentCard(
            name="train_reservation_agent",
            description="Reserves high-speed train tickets in Europe: Eurostar, TGV/SNCF, Renfe AVE, Frecciarossa Trenitalia.",
            url=agent_host_url,
            version="1.0.0",
            defaultInputModes=TrainReservationAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=TrainReservationAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=TrainAgentExecutor(),
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
