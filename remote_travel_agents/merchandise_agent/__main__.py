from a2a.types import AgentCapabilities, AgentSkill, AgentCard
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.server.tasks import InMemoryTaskStore
from agent import MerchandiseAgent
from agent_executor import MerchandiseAgentExecutor
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
@click.option("--port", "port", default=10007)
def main(host, port):
    """Entry point for the A2A + Google GenAI Merchandise Fan Shop Agent."""
    try:
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="merchandise_order",
            name="Merchandise & Formal Wear Shop",
            description="Orders football fan merchandise: jerseys (home, away, retro, kids), scarves, caps, accessories and collectibles for Real Madrid, Barcelona, PSG, Arsenal and Roma, plus formal wear (suits, tuxedos, dress shirts, ties, bow ties, pocket squares, dress shoes).",
            tags=["merchandise", "fan shop", "jersey", "football", "souvenir", "clothing", "formal wear", "suit", "tie", "shirt"],
            examples=[
                "I want to buy a Real Madrid home jersey",
                "Order a Barcelona scarf and a Champions League cap",
                "Get me an Arsenal Invincibles retro jersey with Henry 14 printing",
                "I need a black suit and a silk tie for dinner tonight",
            ],
        )
        agent_host_url = (
            os.getenv("HOST_OVERRIDE")
            if os.getenv("HOST_OVERRIDE")
            else f"http://{host}:{port}/"
        )
        agent_card = AgentCard(
            name="merchandise_agent",
            description="Orders football fan merchandise: jerseys (home, away, retro, kids), scarves, caps, accessories and collectibles for Real Madrid, Barcelona, PSG, Arsenal and Roma, plus formal wear (suits, tuxedos, dress shirts, ties, bow ties, pocket squares, dress shoes).",
            url=agent_host_url,
            version="1.0.0",
            defaultInputModes=MerchandiseAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=MerchandiseAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=MerchandiseAgentExecutor(),
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
