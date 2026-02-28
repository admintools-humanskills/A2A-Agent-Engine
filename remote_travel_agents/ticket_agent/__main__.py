from a2a.types import AgentCapabilities, AgentSkill, AgentCard
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.server.tasks import InMemoryTaskStore
from agent import TicketReservationAgent
from agent_executor import TicketAgentExecutor
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
@click.option("--port", "port", default=10005)
def main(host, port):
    """Entry point for the A2A + CrewAI Ticket Reservation Agent."""
    try:
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="ticket_reservation",
            name="Event Ticket Reservation Tool",
            description="Reserves tickets for sports events (Real Madrid, FC Barcelona, Champions League), concerts, theatre, opera and tennis in Spain and Europe.",
            tags=["ticket", "event", "sports", "concert", "theatre"],
            examples=["I want tickets for Real Madrid vs Barcelona", "Book 2 tickets for the Coldplay concert in Madrid"],
        )
        agent_host_url = (
            os.getenv("HOST_OVERRIDE")
            if os.getenv("HOST_OVERRIDE")
            else f"http://{host}:{port}/"
        )
        agent_card = AgentCard(
            name="ticket_reservation_agent",
            description="Reserves tickets for sports events (Real Madrid, FC Barcelona, Champions League), concerts, theatre, opera and tennis in Spain and Europe.",
            url=agent_host_url,
            version="1.0.0",
            defaultInputModes=TicketReservationAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=TicketReservationAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=TicketAgentExecutor(),
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
