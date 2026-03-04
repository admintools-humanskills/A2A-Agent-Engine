from langchain_google_vertexai import ChatVertexAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

memory = MemorySaver()


class TrainReservation(BaseModel):
    booking_ref: str
    train_number: str
    operator: str
    origin: str
    destination: str
    departure: str
    arrival: str
    travel_class: str
    price: float
    passenger_name: str


@tool
def create_train_reservation(
    train_number: str,
    travel_class: str,
    travel_date: str,
    passenger_name: str,
    return_train: str = "",
    return_date: str = "",
) -> str:
    """Creates a train ticket reservation.

    Args:
        train_number: The train number to book (e.g. ES9001).
        travel_class: Standard or First Class.
        travel_date: Travel date (YYYY-MM-DD).
        passenger_name: Full name of the passenger.
        return_train: Optional return train number for round trips.
        return_date: Optional return date (YYYY-MM-DD).

    Returns:
        str: Confirmation message with booking details.
    """
    try:
        trains = {
            # Eurostar: London <-> Paris
            "ES9001": {"operator": "Eurostar", "origin": "London St Pancras", "destination": "Paris Gare du Nord", "departure": "06:01", "arrival": "09:17", "duration": "2h16", "standard": 69, "first": 199},
            "ES9005": {"operator": "Eurostar", "origin": "London St Pancras", "destination": "Paris Gare du Nord", "departure": "10:31", "arrival": "13:47", "duration": "2h16", "standard": 89, "first": 245},
            "ES9014": {"operator": "Eurostar", "origin": "Paris Gare du Nord", "destination": "London St Pancras", "departure": "07:13", "arrival": "08:30", "duration": "2h17", "standard": 69, "first": 199},
            "ES9040": {"operator": "Eurostar", "origin": "Paris Gare du Nord", "destination": "London St Pancras", "departure": "18:01", "arrival": "19:17", "duration": "2h16", "standard": 99, "first": 265},
            # TGV/SNCF: Paris <-> Barcelona
            "TGV6101": {"operator": "SNCF TGV", "origin": "Paris Gare de Lyon", "destination": "Barcelona Sants", "departure": "09:42", "arrival": "16:22", "duration": "6h40", "standard": 59, "first": 149},
            "TGV6103": {"operator": "SNCF TGV", "origin": "Barcelona Sants", "destination": "Paris Gare de Lyon", "departure": "08:30", "arrival": "15:08", "duration": "6h38", "standard": 59, "first": 149},
            # TGV/SNCF: Paris <-> Madrid (via Barcelona)
            "TGV6201": {"operator": "SNCF TGV + Renfe", "origin": "Paris Gare de Lyon", "destination": "Madrid Atocha", "departure": "09:42", "arrival": "19:10", "duration": "9h28", "standard": 89, "first": 199},
            # Renfe AVE: Madrid <-> Barcelona
            "AVE3100": {"operator": "Renfe AVE", "origin": "Madrid Atocha", "destination": "Barcelona Sants", "departure": "06:30", "arrival": "09:05", "duration": "2h35", "standard": 35, "first": 95},
            "AVE3110": {"operator": "Renfe AVE", "origin": "Madrid Atocha", "destination": "Barcelona Sants", "departure": "11:00", "arrival": "13:35", "duration": "2h35", "standard": 45, "first": 110},
            "AVE3120": {"operator": "Renfe AVE", "origin": "Madrid Atocha", "destination": "Barcelona Sants", "departure": "16:00", "arrival": "18:35", "duration": "2h35", "standard": 50, "first": 120},
            "AVE3150": {"operator": "Renfe AVE", "origin": "Barcelona Sants", "destination": "Madrid Atocha", "departure": "07:00", "arrival": "09:35", "duration": "2h35", "standard": 35, "first": 95},
            "AVE3160": {"operator": "Renfe AVE", "origin": "Barcelona Sants", "destination": "Madrid Atocha", "departure": "14:30", "arrival": "17:05", "duration": "2h35", "standard": 45, "first": 110},
            "AVE3170": {"operator": "Renfe AVE", "origin": "Barcelona Sants", "destination": "Madrid Atocha", "departure": "19:00", "arrival": "21:35", "duration": "2h35", "standard": 55, "first": 125},
            # Frecciarossa: Rome <-> Milan (connecting hub)
            "FR9600": {"operator": "Trenitalia Frecciarossa", "origin": "Rome Termini", "destination": "Milan Centrale", "departure": "06:50", "arrival": "09:45", "duration": "2h55", "standard": 39, "first": 89},
            "FR9620": {"operator": "Trenitalia Frecciarossa", "origin": "Rome Termini", "destination": "Milan Centrale", "departure": "12:00", "arrival": "14:55", "duration": "2h55", "standard": 49, "first": 109},
            "FR9650": {"operator": "Trenitalia Frecciarossa", "origin": "Milan Centrale", "destination": "Rome Termini", "departure": "08:00", "arrival": "10:55", "duration": "2h55", "standard": 39, "first": 89},
            "FR9660": {"operator": "Trenitalia Frecciarossa", "origin": "Milan Centrale", "destination": "Rome Termini", "departure": "17:00", "arrival": "19:55", "duration": "2h55", "standard": 55, "first": 119},
            # Frecciarossa: Rome <-> Florence
            "FR9400": {"operator": "Trenitalia Frecciarossa", "origin": "Rome Termini", "destination": "Florence SMN", "departure": "07:30", "arrival": "09:00", "duration": "1h30", "standard": 29, "first": 59},
            "FR9410": {"operator": "Trenitalia Frecciarossa", "origin": "Florence SMN", "destination": "Rome Termini", "departure": "16:00", "arrival": "17:30", "duration": "1h30", "standard": 29, "first": 59},
            # Eurostar: London <-> Barcelona (via Paris)
            "ES9501": {"operator": "Eurostar + SNCF", "origin": "London St Pancras", "destination": "Barcelona Sants", "departure": "06:01", "arrival": "16:22", "duration": "10h21", "standard": 119, "first": 299},
        }

        train_info = trains.get(train_number)
        if not train_info:
            return f"Error: Train {train_number} not found in our catalog."

        price_key = "standard" if travel_class.lower() == "standard" else "first"
        price = train_info[price_key]

        booking_ref = f"TRN-{uuid.uuid4().hex[:8].upper()}"
        reservation = TrainReservation(
            booking_ref=booking_ref,
            train_number=train_number,
            operator=train_info["operator"],
            origin=train_info["origin"],
            destination=train_info["destination"],
            departure=f"{travel_date} {train_info['departure']}",
            arrival=f"{travel_date} {train_info['arrival']}",
            travel_class=travel_class,
            price=price,
            passenger_name=passenger_name,
        )
        result = f"Booking confirmed: {reservation.model_dump()}"

        if return_train and return_date:
            return_info = trains.get(return_train)
            if return_info:
                return_price = return_info["standard" if travel_class.lower() == "standard" else "first"]
                return_ref = f"TRN-{uuid.uuid4().hex[:8].upper()}"
                return_reservation = TrainReservation(
                    booking_ref=return_ref,
                    train_number=return_train,
                    operator=return_info["operator"],
                    origin=return_info["origin"],
                    destination=return_info["destination"],
                    departure=f"{return_date} {return_info['departure']}",
                    arrival=f"{return_date} {return_info['arrival']}",
                    travel_class=travel_class,
                    price=return_price,
                    passenger_name=passenger_name,
                )
                result += f"\nReturn booking confirmed: {return_reservation.model_dump()}"
                result += f"\nTotal round-trip price: {price + return_price} EUR"

        print(f"=== {result} ===")
        return result
    except Exception as e:
        print(f"Error creating reservation: {e}")
        return f"Error creating reservation: {e}"


class TrainReservationAgent:
    SYSTEM_INSTRUCTION = """
# INSTRUCTIONS

You are a specialized train reservation assistant for European high-speed rail.
Your sole purpose is to help users find trains, compare options and prices, and create train ticket reservations.
If the user asks about anything other than train travel, politely state that you can only assist with train bookings.

# AVAILABLE TRAINS

## Eurostar: London <-> Paris
- ES9001: London St Pancras -> Paris Gare du Nord, 06:01-09:17 (2h16), Standard 69 EUR / First 199 EUR
- ES9005: London St Pancras -> Paris Gare du Nord, 10:31-13:47 (2h16), Standard 89 EUR / First 245 EUR
- ES9014: Paris Gare du Nord -> London St Pancras, 07:13-08:30 (2h17), Standard 69 EUR / First 199 EUR
- ES9040: Paris Gare du Nord -> London St Pancras, 18:01-19:17 (2h16), Standard 99 EUR / First 265 EUR

## SNCF TGV: Paris <-> Barcelona
- TGV6101: Paris Gare de Lyon -> Barcelona Sants, 09:42-16:22 (6h40), Standard 59 EUR / First 149 EUR
- TGV6103: Barcelona Sants -> Paris Gare de Lyon, 08:30-15:08 (6h38), Standard 59 EUR / First 149 EUR

## SNCF TGV + Renfe: Paris <-> Madrid
- TGV6201: Paris Gare de Lyon -> Madrid Atocha, 09:42-19:10 (9h28), Standard 89 EUR / First 199 EUR

## Renfe AVE: Madrid <-> Barcelona
- AVE3100: Madrid Atocha -> Barcelona Sants, 06:30-09:05 (2h35), Standard 35 EUR / First 95 EUR
- AVE3110: Madrid Atocha -> Barcelona Sants, 11:00-13:35 (2h35), Standard 45 EUR / First 110 EUR
- AVE3120: Madrid Atocha -> Barcelona Sants, 16:00-18:35 (2h35), Standard 50 EUR / First 120 EUR
- AVE3150: Barcelona Sants -> Madrid Atocha, 07:00-09:35 (2h35), Standard 35 EUR / First 95 EUR
- AVE3160: Barcelona Sants -> Madrid Atocha, 14:30-17:05 (2h35), Standard 45 EUR / First 110 EUR
- AVE3170: Barcelona Sants -> Madrid Atocha, 19:00-21:35 (2h35), Standard 55 EUR / First 125 EUR

## Trenitalia Frecciarossa: Rome <-> Milan
- FR9600: Rome Termini -> Milan Centrale, 06:50-09:45 (2h55), Standard 39 EUR / First 89 EUR
- FR9620: Rome Termini -> Milan Centrale, 12:00-14:55 (2h55), Standard 49 EUR / First 109 EUR
- FR9650: Milan Centrale -> Rome Termini, 08:00-10:55 (2h55), Standard 39 EUR / First 89 EUR
- FR9660: Milan Centrale -> Rome Termini, 17:00-19:55 (2h55), Standard 55 EUR / First 119 EUR

## Trenitalia Frecciarossa: Rome <-> Florence
- FR9400: Rome Termini -> Florence SMN, 07:30-09:00 (1h30), Standard 29 EUR / First 59 EUR
- FR9410: Florence SMN -> Rome Termini, 16:00-17:30 (1h30), Standard 29 EUR / First 59 EUR

## Eurostar + SNCF: London <-> Barcelona
- ES9501: London St Pancras -> Barcelona Sants, 06:01-16:22 (10h21), Standard 119 EUR / First 299 EUR

# RULES

- When ALL required information is provided (route, travel date, passenger name), select the best available train and proceed DIRECTLY to the reservation using `create_train_reservation` WITHOUT asking for confirmation.
- If essential details are missing, ask ONLY for the missing details.
- If the user doesn't specify a train number, choose the most suitable option for their route and time preferences.
- After booking, provide a detailed confirmation with booking reference, train details, price breakdown, and total.
- DO NOT make up trains or prices not listed above.
- All prices are in EUR and are one-way.
"""
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.model = ChatVertexAI(
            model="gemini-2.5-flash-lite",
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        )
        self.tools = [create_train_reservation]
        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
        )

    def invoke(self, query, sessionId) -> str:
        config = {"configurable": {"thread_id": sessionId}}
        self.graph.invoke({"messages": [("user", query)]}, config)
        return self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        return current_state.values["messages"][-1].content
