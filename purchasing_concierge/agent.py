from .purchasing_agent import PurchasingAgent
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

root_agent = PurchasingAgent(
    remote_agent_addresses=[
        os.getenv("HOTEL_AGENT_URL", "http://localhost:10002"),
        os.getenv("FLIGHT_AGENT_URL", "http://localhost:10003"),
        os.getenv("TRAIN_AGENT_URL", "http://localhost:10004"),
        os.getenv("TICKET_AGENT_URL", "http://localhost:10005"),
        os.getenv("RESTAURANT_AGENT_URL", "http://localhost:10006"),
        os.getenv("MERCHANDISE_AGENT_URL", "http://localhost:10007"),
    ]
).create_agent()
