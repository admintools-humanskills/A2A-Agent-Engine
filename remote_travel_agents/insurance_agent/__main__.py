from a2a.types import AgentCapabilities, AgentSkill, AgentCard
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.server.tasks import InMemoryTaskStore
from agent import InsuranceAgent
from agent_executor import InsuranceAgentExecutor
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
@click.option("--port", "port", default=10008)
def main(host, port):
    """Entry point for the A2A + Google GenAI Cardif Insurance Agent."""
    try:
        capabilities = AgentCapabilities(streaming=True)
        quote_skill = AgentSkill(
            id="get_insurance_quote",
            name="Insurance Quote Generator",
            description="Generates quotes for BNP Paribas Cardif insurance products: mortgage insurance (assurance pret immobilier), home insurance (assurance habitation), life/disability insurance (prevoyance), and retirement savings (epargne retraite PER).",
            tags=["insurance", "quote", "cardif", "mortgage", "home", "prevoyance", "retirement"],
            examples=[
                "I need a mortgage insurance quote for a 250,000 EUR loan over 20 years",
                "Je cherche une assurance habitation pour mon appartement de 60m2 a Paris",
                "Devis prevoyance pour un cadre de 40 ans",
            ],
        )
        appointment_skill = AgentSkill(
            id="book_advisor_appointment",
            name="Advisor Appointment Booking",
            description="Books an appointment with a BNP Paribas Cardif insurance advisor for personalized consultation on any insurance product.",
            tags=["insurance", "appointment", "advisor", "cardif", "consultation"],
            examples=[
                "Je veux prendre rendez-vous avec un conseiller pour l'epargne retraite",
                "Book an appointment with an insurance advisor",
            ],
        )
        agent_host_url = (
            os.getenv("HOST_OVERRIDE")
            if os.getenv("HOST_OVERRIDE")
            else f"http://{host}:{port}/"
        )
        agent_card = AgentCard(
            name="insurance_agent",
            description="BNP Paribas Cardif insurance advisor — provides quotes for mortgage insurance, home insurance, life insurance, and retirement savings (PER). Can also book appointments with specialized advisors.",
            url=agent_host_url,
            version="1.0.0",
            defaultInputModes=InsuranceAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=InsuranceAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[quote_skill, appointment_skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=InsuranceAgentExecutor(),
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
