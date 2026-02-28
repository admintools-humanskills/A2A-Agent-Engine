from pydantic import BaseModel
import uuid
from crewai import Agent, Crew, LLM, Task, Process
from crewai.tools import tool
from dotenv import load_dotenv
import litellm
import os

load_dotenv()

litellm.vertex_project = os.getenv("GOOGLE_CLOUD_PROJECT")
litellm.vertex_location = os.getenv("GOOGLE_CLOUD_LOCATION")


class FlightReservation(BaseModel):
    booking_ref: str
    flight_number: str
    airline: str
    origin: str
    destination: str
    departure: str
    arrival: str
    cabin_class: str
    price: float
    passenger_name: str


@tool("create_flight_reservation")
def create_flight_reservation(
    flight_number: str,
    cabin_class: str,
    departure_date: str,
    passenger_name: str,
    return_flight_number: str = "",
    return_date: str = "",
) -> str:
    """Creates a flight reservation.

    Args:
        flight_number: The flight number to book (e.g. AF1000).
        cabin_class: Economy or Business.
        departure_date: Departure date (YYYY-MM-DD).
        passenger_name: Full name of the passenger.
        return_flight_number: Optional return flight number for round trips.
        return_date: Optional return date (YYYY-MM-DD).

    Returns:
        str: Confirmation message with booking details.
    """
    try:
        # Flight catalog lookup
        flights = {
            # Paris <-> Madrid
            "AF1000": {"airline": "Air France", "origin": "Paris CDG", "destination": "Madrid MAD", "departure": "07:30", "arrival": "09:45", "economy": 120, "business": 340},
            "AF1001": {"airline": "Air France", "origin": "Paris CDG", "destination": "Madrid MAD", "departure": "14:15", "arrival": "16:30", "economy": 135, "business": 365},
            "IB3401": {"airline": "Iberia", "origin": "Madrid MAD", "destination": "Paris CDG", "departure": "08:00", "arrival": "10:20", "economy": 110, "business": 320},
            "IB3403": {"airline": "Iberia", "origin": "Madrid MAD", "destination": "Paris CDG", "departure": "17:30", "arrival": "19:50", "economy": 125, "business": 350},
            # Paris <-> London
            "AF1680": {"airline": "Air France", "origin": "Paris CDG", "destination": "London LHR", "departure": "09:00", "arrival": "09:20", "economy": 95, "business": 280},
            "BA303": {"airline": "British Airways", "origin": "London LHR", "destination": "Paris CDG", "departure": "10:30", "arrival": "12:45", "economy": 100, "business": 295},
            "BA307": {"airline": "British Airways", "origin": "London LHR", "destination": "Paris CDG", "departure": "18:00", "arrival": "20:15", "economy": 110, "business": 310},
            # Paris <-> Barcelona
            "VY8001": {"airline": "Vueling", "origin": "Paris ORY", "destination": "Barcelona BCN", "departure": "06:45", "arrival": "08:40", "economy": 65, "business": 180},
            "AF1148": {"airline": "Air France", "origin": "Paris CDG", "destination": "Barcelona BCN", "departure": "11:00", "arrival": "12:55", "economy": 110, "business": 300},
            "VY8002": {"airline": "Vueling", "origin": "Barcelona BCN", "destination": "Paris ORY", "departure": "19:30", "arrival": "21:25", "economy": 70, "business": 190},
            # Paris <-> Rome
            "AF1404": {"airline": "Air France", "origin": "Paris CDG", "destination": "Rome FCO", "departure": "08:30", "arrival": "10:40", "economy": 105, "business": 310},
            "AZ319": {"airline": "ITA Airways", "origin": "Rome FCO", "destination": "Paris CDG", "departure": "13:00", "arrival": "15:15", "economy": 100, "business": 290},
            # Madrid <-> Barcelona
            "IB2101": {"airline": "Iberia", "origin": "Madrid MAD", "destination": "Barcelona BCN", "departure": "07:00", "arrival": "08:15", "economy": 55, "business": 150},
            "VY1001": {"airline": "Vueling", "origin": "Madrid MAD", "destination": "Barcelona BCN", "departure": "12:30", "arrival": "13:45", "economy": 45, "business": 130},
            "IB2106": {"airline": "Iberia", "origin": "Barcelona BCN", "destination": "Madrid MAD", "departure": "20:00", "arrival": "21:15", "economy": 60, "business": 160},
            # Madrid <-> London
            "IB3160": {"airline": "Iberia", "origin": "Madrid MAD", "destination": "London LHR", "departure": "09:30", "arrival": "11:00", "economy": 95, "business": 280},
            "BA460": {"airline": "British Airways", "origin": "London LHR", "destination": "Madrid MAD", "departure": "08:15", "arrival": "11:45", "economy": 100, "business": 300},
            # Madrid <-> Rome
            "IB3240": {"airline": "Iberia", "origin": "Madrid MAD", "destination": "Rome FCO", "departure": "10:00", "arrival": "13:00", "economy": 90, "business": 260},
            "AZ67": {"airline": "ITA Airways", "origin": "Rome FCO", "destination": "Madrid MAD", "departure": "15:30", "arrival": "18:00", "economy": 85, "business": 250},
            # London <-> Barcelona
            "VY7821": {"airline": "Vueling", "origin": "London LGW", "destination": "Barcelona BCN", "departure": "07:15", "arrival": "10:30", "economy": 70, "business": 195},
            "BA478": {"airline": "British Airways", "origin": "London LHR", "destination": "Barcelona BCN", "departure": "14:00", "arrival": "17:10", "economy": 105, "business": 305},
            # London <-> Rome
            "BA550": {"airline": "British Airways", "origin": "London LHR", "destination": "Rome FCO", "departure": "09:45", "arrival": "13:30", "economy": 110, "business": 320},
            "AZ201": {"airline": "ITA Airways", "origin": "Rome FCO", "destination": "London LHR", "departure": "16:00", "arrival": "17:45", "economy": 95, "business": 285},
            # Barcelona <-> Rome
            "VY6100": {"airline": "Vueling", "origin": "Barcelona BCN", "destination": "Rome FCO", "departure": "08:00", "arrival": "10:15", "economy": 60, "business": 170},
            "AZ77": {"airline": "ITA Airways", "origin": "Rome FCO", "destination": "Barcelona BCN", "departure": "12:30", "arrival": "14:40", "economy": 65, "business": 180},
        }

        flight_info = flights.get(flight_number)
        if not flight_info:
            return f"Error: Flight {flight_number} not found in our catalog."

        price_key = "economy" if cabin_class.lower() == "economy" else "business"
        price = flight_info[price_key]

        booking_ref = f"FLT-{uuid.uuid4().hex[:8].upper()}"
        reservation = FlightReservation(
            booking_ref=booking_ref,
            flight_number=flight_number,
            airline=flight_info["airline"],
            origin=flight_info["origin"],
            destination=flight_info["destination"],
            departure=f"{departure_date} {flight_info['departure']}",
            arrival=f"{departure_date} {flight_info['arrival']}",
            cabin_class=cabin_class,
            price=price,
            passenger_name=passenger_name,
        )
        result = f"Booking confirmed: {reservation.model_dump()}"

        # Handle return flight
        if return_flight_number and return_date:
            return_info = flights.get(return_flight_number)
            if return_info:
                return_price = return_info["economy" if cabin_class.lower() == "economy" else "business"]
                return_ref = f"FLT-{uuid.uuid4().hex[:8].upper()}"
                return_reservation = FlightReservation(
                    booking_ref=return_ref,
                    flight_number=return_flight_number,
                    airline=return_info["airline"],
                    origin=return_info["origin"],
                    destination=return_info["destination"],
                    departure=f"{return_date} {return_info['departure']}",
                    arrival=f"{return_date} {return_info['arrival']}",
                    cabin_class=cabin_class,
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


class FlightReservationAgent:
    TaskInstruction = """
# INSTRUCTIONS

You are a specialized flight reservation assistant for European routes.
Your sole purpose is to help users find flights, compare options and prices, and create flight reservations.
If the user asks about anything other than flights, politely state that you can only assist with flight bookings.

# CONTEXT

Received user query: {user_prompt}
Session ID: {session_id}

# AVAILABLE FLIGHTS

## Paris <-> Madrid
- AF1000: Air France, Paris CDG -> Madrid MAD, 07:30-09:45, Economy 120 EUR / Business 340 EUR
- AF1001: Air France, Paris CDG -> Madrid MAD, 14:15-16:30, Economy 135 EUR / Business 365 EUR
- IB3401: Iberia, Madrid MAD -> Paris CDG, 08:00-10:20, Economy 110 EUR / Business 320 EUR
- IB3403: Iberia, Madrid MAD -> Paris CDG, 17:30-19:50, Economy 125 EUR / Business 350 EUR

## Paris <-> London
- AF1680: Air France, Paris CDG -> London LHR, 09:00-09:20, Economy 95 EUR / Business 280 EUR
- BA303: British Airways, London LHR -> Paris CDG, 10:30-12:45, Economy 100 EUR / Business 295 EUR
- BA307: British Airways, London LHR -> Paris CDG, 18:00-20:15, Economy 110 EUR / Business 310 EUR

## Paris <-> Barcelona
- VY8001: Vueling, Paris ORY -> Barcelona BCN, 06:45-08:40, Economy 65 EUR / Business 180 EUR
- AF1148: Air France, Paris CDG -> Barcelona BCN, 11:00-12:55, Economy 110 EUR / Business 300 EUR
- VY8002: Vueling, Barcelona BCN -> Paris ORY, 19:30-21:25, Economy 70 EUR / Business 190 EUR

## Paris <-> Rome
- AF1404: Air France, Paris CDG -> Rome FCO, 08:30-10:40, Economy 105 EUR / Business 310 EUR
- AZ319: ITA Airways, Rome FCO -> Paris CDG, 13:00-15:15, Economy 100 EUR / Business 290 EUR

## Madrid <-> Barcelona
- IB2101: Iberia, Madrid MAD -> Barcelona BCN, 07:00-08:15, Economy 55 EUR / Business 150 EUR
- VY1001: Vueling, Madrid MAD -> Barcelona BCN, 12:30-13:45, Economy 45 EUR / Business 130 EUR
- IB2106: Iberia, Barcelona BCN -> Madrid MAD, 20:00-21:15, Economy 60 EUR / Business 160 EUR

## Madrid <-> London
- IB3160: Iberia, Madrid MAD -> London LHR, 09:30-11:00, Economy 95 EUR / Business 280 EUR
- BA460: British Airways, London LHR -> Madrid MAD, 08:15-11:45, Economy 100 EUR / Business 300 EUR

## Madrid <-> Rome
- IB3240: Iberia, Madrid MAD -> Rome FCO, 10:00-13:00, Economy 90 EUR / Business 260 EUR
- AZ67: ITA Airways, Rome FCO -> Madrid MAD, 15:30-18:00, Economy 85 EUR / Business 250 EUR

## London <-> Barcelona
- VY7821: Vueling, London LGW -> Barcelona BCN, 07:15-10:30, Economy 70 EUR / Business 195 EUR
- BA478: British Airways, London LHR -> Barcelona BCN, 14:00-17:10, Economy 105 EUR / Business 305 EUR

## London <-> Rome
- BA550: British Airways, London LHR -> Rome FCO, 09:45-13:30, Economy 110 EUR / Business 320 EUR
- AZ201: ITA Airways, Rome FCO -> London LHR, 16:00-17:45, Economy 95 EUR / Business 285 EUR

## Barcelona <-> Rome
- VY6100: Vueling, Barcelona BCN -> Rome FCO, 08:00-10:15, Economy 60 EUR / Business 170 EUR
- AZ77: ITA Airways, Rome FCO -> Barcelona BCN, 12:30-14:40, Economy 65 EUR / Business 180 EUR

# RULES

- Present available flights for the requested route with prices before booking.
- If the user wants to book, follow this order:
    1. Confirm flight number, cabin class, departure date, passenger name, and optional return details.
    2. Use `create_flight_reservation` tool to create the reservation.
    3. Provide a detailed confirmation with booking reference, flight details, price breakdown, and total.
- Set response status to input_required if asking for user confirmation.
- Set response status to error if there is an error while processing the request.
- Set response status to completed if the request is complete.
- DO NOT make up flights or prices not listed above.
- All prices are in EUR and are one-way.
"""
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def invoke(self, query, sessionId) -> str:
        model = LLM(
            model="vertex_ai/gemini-2.5-flash-lite",
        )
        flight_agent = Agent(
            role="Flight Reservation Agent",
            goal=(
                "Help user to find and book flights between major European cities."
            ),
            backstory=("You are an expert flight reservation agent specializing in European routes."),
            verbose=False,
            allow_delegation=False,
            tools=[create_flight_reservation],
            llm=model,
        )

        agent_task = Task(
            description=self.TaskInstruction,
            agent=flight_agent,
            expected_output="Response to the user with flight options or booking confirmation",
        )

        crew = Crew(
            tasks=[agent_task],
            agents=[flight_agent],
            verbose=False,
            process=Process.sequential,
        )

        inputs = {"user_prompt": query, "session_id": sessionId}
        response = crew.kickoff(inputs)
        return response


if __name__ == "__main__":
    agent = FlightReservationAgent()
    result = agent.invoke("I need a flight from Paris to Madrid next Monday", "default_session")
    print(result)
