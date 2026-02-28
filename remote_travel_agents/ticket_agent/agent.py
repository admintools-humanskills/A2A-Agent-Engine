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


class TicketReservation(BaseModel):
    booking_ref: str
    event_name: str
    event_date: str
    venue: str
    city: str
    seat_category: str
    num_tickets: int
    price_per_ticket: float
    total_price: float
    attendee_name: str


@tool("create_ticket_reservation")
def create_ticket_reservation(
    event_name: str,
    event_date: str,
    seat_category: str,
    num_tickets: int,
    attendee_name: str,
) -> str:
    """Creates an event ticket reservation.

    Args:
        event_name: Name of the event exactly as listed in the catalog.
        event_date: Date of the event (YYYY-MM-DD).
        seat_category: Seating category (Tier 3, Tier 2, Tier 1, or VIP).
        num_tickets: Number of tickets to book.
        attendee_name: Full name of the main attendee.

    Returns:
        str: Confirmation message with ticket details.
    """
    try:
        events = {
            # Football - Real Madrid
            "Real Madrid vs FC Barcelona - La Liga": {"venue": "Santiago Bernabeu", "city": "Madrid", "tier3": 85, "tier2": 150, "tier1": 280, "vip": 550},
            "Real Madrid vs Atletico Madrid - La Liga": {"venue": "Santiago Bernabeu", "city": "Madrid", "tier3": 75, "tier2": 130, "tier1": 240, "vip": 480},
            "Real Madrid vs Bayern Munich - Champions League": {"venue": "Santiago Bernabeu", "city": "Madrid", "tier3": 120, "tier2": 220, "tier1": 400, "vip": 800},
            "Real Madrid vs Manchester City - Champions League": {"venue": "Santiago Bernabeu", "city": "Madrid", "tier3": 130, "tier2": 240, "tier1": 420, "vip": 850},
            # Football - FC Barcelona
            "FC Barcelona vs Real Madrid - La Liga": {"venue": "Spotify Camp Nou", "city": "Barcelona", "tier3": 90, "tier2": 160, "tier1": 290, "vip": 580},
            "FC Barcelona vs PSG - Champions League": {"venue": "Spotify Camp Nou", "city": "Barcelona", "tier3": 100, "tier2": 190, "tier1": 350, "vip": 700},
            # Football - Other
            "PSG vs Olympique de Marseille - Ligue 1": {"venue": "Parc des Princes", "city": "Paris", "tier3": 70, "tier2": 120, "tier1": 220, "vip": 450},
            "AS Roma vs Lazio - Serie A": {"venue": "Stadio Olimpico", "city": "Rome", "tier3": 55, "tier2": 95, "tier1": 180, "vip": 360},
            "Arsenal vs Chelsea - Premier League": {"venue": "Emirates Stadium", "city": "London", "tier3": 80, "tier2": 145, "tier1": 260, "vip": 520},
            # Concerts
            "Coldplay - Music of the Spheres World Tour": {"venue": "Estadio Metropolitano", "city": "Madrid", "tier3": 65, "tier2": 110, "tier1": 185, "vip": 350},
            "Taylor Swift - The Eras Tour": {"venue": "Stade de France", "city": "Paris", "tier3": 90, "tier2": 160, "tier1": 280, "vip": 550},
            "Bad Bunny - Most Wanted Tour": {"venue": "Palau Sant Jordi", "city": "Barcelona", "tier3": 55, "tier2": 95, "tier1": 165, "vip": 320},
            "Rosalia - Motomami World Tour": {"venue": "WiZink Center", "city": "Madrid", "tier3": 45, "tier2": 80, "tier1": 140, "vip": 280},
            "Stromae - Multitude Tour": {"venue": "Accor Arena", "city": "Paris", "tier3": 50, "tier2": 85, "tier1": 150, "vip": 300},
            "Ed Sheeran - Mathematics Tour": {"venue": "Wembley Stadium", "city": "London", "tier3": 70, "tier2": 120, "tier1": 200, "vip": 400},
            # Theatre / Opera
            "La Traviata - Opera": {"venue": "Teatro Real", "city": "Madrid", "tier3": 35, "tier2": 70, "tier1": 130, "vip": 250},
            "Carmen - Opera": {"venue": "Palau de la Musica", "city": "Barcelona", "tier3": 30, "tier2": 60, "tier1": 110, "vip": 220},
            "The Phantom of the Opera": {"venue": "Her Majesty's Theatre", "city": "London", "tier3": 40, "tier2": 75, "tier1": 140, "vip": 270},
            "Le Lac des Cygnes - Ballet": {"venue": "Opera Garnier", "city": "Paris", "tier3": 45, "tier2": 85, "tier1": 160, "vip": 310},
            # Tennis
            "Madrid Open - Quarter Finals": {"venue": "Caja Magica", "city": "Madrid", "tier3": 40, "tier2": 80, "tier1": 150, "vip": 300},
            "Madrid Open - Final": {"venue": "Caja Magica", "city": "Madrid", "tier3": 75, "tier2": 140, "tier1": 260, "vip": 500},
            "Roland Garros - Quarter Finals": {"venue": "Stade Roland Garros", "city": "Paris", "tier3": 55, "tier2": 100, "tier1": 190, "vip": 380},
            # Basketball
            "Real Madrid vs FC Barcelona - ACB Liga": {"venue": "WiZink Center", "city": "Madrid", "tier3": 35, "tier2": 65, "tier1": 120, "vip": 240},
            "NBA Global Games London": {"venue": "The O2 Arena", "city": "London", "tier3": 60, "tier2": 110, "tier1": 200, "vip": 400},
        }

        event_info = events.get(event_name)
        if not event_info:
            return f"Error: Event '{event_name}' not found in our catalog."

        category_key = seat_category.lower().replace(" ", "")
        price_map = {"tier3": "tier3", "tier2": "tier2", "tier1": "tier1", "vip": "vip"}
        price_key = price_map.get(category_key)
        if not price_key:
            return f"Error: Invalid seat category '{seat_category}'. Choose from: Tier 3, Tier 2, Tier 1, VIP."

        price_per_ticket = event_info[price_key]
        total_price = price_per_ticket * num_tickets

        booking_ref = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        reservation = TicketReservation(
            booking_ref=booking_ref,
            event_name=event_name,
            event_date=event_date,
            venue=event_info["venue"],
            city=event_info["city"],
            seat_category=seat_category,
            num_tickets=num_tickets,
            price_per_ticket=price_per_ticket,
            total_price=total_price,
            attendee_name=attendee_name,
        )
        print(f"=== Ticket reservation created: {reservation} ===")
        return f"Booking confirmed: {reservation.model_dump()}"
    except Exception as e:
        print(f"Error creating reservation: {e}")
        return f"Error creating reservation: {e}"


class TicketReservationAgent:
    TaskInstruction = """
# INSTRUCTIONS

You are a specialized event ticket reservation assistant.
Your sole purpose is to help users find events, compare ticket categories and prices, and create ticket reservations.
If the user asks about anything other than events or tickets, politely state that you can only assist with event ticket bookings.

# CONTEXT

Received user query: {user_prompt}
Session ID: {session_id}

# AVAILABLE EVENTS

## Football

### Madrid
- **Real Madrid vs FC Barcelona - La Liga** @ Santiago Bernabeu
  Tier 3: 85 EUR | Tier 2: 150 EUR | Tier 1: 280 EUR | VIP: 550 EUR
- **Real Madrid vs Atletico Madrid - La Liga** @ Santiago Bernabeu
  Tier 3: 75 EUR | Tier 2: 130 EUR | Tier 1: 240 EUR | VIP: 480 EUR
- **Real Madrid vs Bayern Munich - Champions League** @ Santiago Bernabeu
  Tier 3: 120 EUR | Tier 2: 220 EUR | Tier 1: 400 EUR | VIP: 800 EUR
- **Real Madrid vs Manchester City - Champions League** @ Santiago Bernabeu
  Tier 3: 130 EUR | Tier 2: 240 EUR | Tier 1: 420 EUR | VIP: 850 EUR

### Barcelona
- **FC Barcelona vs Real Madrid - La Liga** @ Spotify Camp Nou
  Tier 3: 90 EUR | Tier 2: 160 EUR | Tier 1: 290 EUR | VIP: 580 EUR
- **FC Barcelona vs PSG - Champions League** @ Spotify Camp Nou
  Tier 3: 100 EUR | Tier 2: 190 EUR | Tier 1: 350 EUR | VIP: 700 EUR

### Paris
- **PSG vs Olympique de Marseille - Ligue 1** @ Parc des Princes
  Tier 3: 70 EUR | Tier 2: 120 EUR | Tier 1: 220 EUR | VIP: 450 EUR

### Rome
- **AS Roma vs Lazio - Serie A** @ Stadio Olimpico
  Tier 3: 55 EUR | Tier 2: 95 EUR | Tier 1: 180 EUR | VIP: 360 EUR

### London
- **Arsenal vs Chelsea - Premier League** @ Emirates Stadium
  Tier 3: 80 EUR | Tier 2: 145 EUR | Tier 1: 260 EUR | VIP: 520 EUR

## Concerts

- **Coldplay - Music of the Spheres World Tour** @ Estadio Metropolitano, Madrid
  Tier 3: 65 EUR | Tier 2: 110 EUR | Tier 1: 185 EUR | VIP: 350 EUR
- **Taylor Swift - The Eras Tour** @ Stade de France, Paris
  Tier 3: 90 EUR | Tier 2: 160 EUR | Tier 1: 280 EUR | VIP: 550 EUR
- **Bad Bunny - Most Wanted Tour** @ Palau Sant Jordi, Barcelona
  Tier 3: 55 EUR | Tier 2: 95 EUR | Tier 1: 165 EUR | VIP: 320 EUR
- **Rosalia - Motomami World Tour** @ WiZink Center, Madrid
  Tier 3: 45 EUR | Tier 2: 80 EUR | Tier 1: 140 EUR | VIP: 280 EUR
- **Stromae - Multitude Tour** @ Accor Arena, Paris
  Tier 3: 50 EUR | Tier 2: 85 EUR | Tier 1: 150 EUR | VIP: 300 EUR
- **Ed Sheeran - Mathematics Tour** @ Wembley Stadium, London
  Tier 3: 70 EUR | Tier 2: 120 EUR | Tier 1: 200 EUR | VIP: 400 EUR

## Theatre / Opera

- **La Traviata - Opera** @ Teatro Real, Madrid
  Tier 3: 35 EUR | Tier 2: 70 EUR | Tier 1: 130 EUR | VIP: 250 EUR
- **Carmen - Opera** @ Palau de la Musica, Barcelona
  Tier 3: 30 EUR | Tier 2: 60 EUR | Tier 1: 110 EUR | VIP: 220 EUR
- **The Phantom of the Opera** @ Her Majesty's Theatre, London
  Tier 3: 40 EUR | Tier 2: 75 EUR | Tier 1: 140 EUR | VIP: 270 EUR
- **Le Lac des Cygnes - Ballet** @ Opera Garnier, Paris
  Tier 3: 45 EUR | Tier 2: 85 EUR | Tier 1: 160 EUR | VIP: 310 EUR

## Tennis

- **Madrid Open - Quarter Finals** @ Caja Magica, Madrid
  Tier 3: 40 EUR | Tier 2: 80 EUR | Tier 1: 150 EUR | VIP: 300 EUR
- **Madrid Open - Final** @ Caja Magica, Madrid
  Tier 3: 75 EUR | Tier 2: 140 EUR | Tier 1: 260 EUR | VIP: 500 EUR
- **Roland Garros - Quarter Finals** @ Stade Roland Garros, Paris
  Tier 3: 55 EUR | Tier 2: 100 EUR | Tier 1: 190 EUR | VIP: 380 EUR

## Basketball

- **Real Madrid vs FC Barcelona - ACB Liga** @ WiZink Center, Madrid
  Tier 3: 35 EUR | Tier 2: 65 EUR | Tier 1: 120 EUR | VIP: 240 EUR
- **NBA Global Games London** @ The O2 Arena, London
  Tier 3: 60 EUR | Tier 2: 110 EUR | Tier 1: 200 EUR | VIP: 400 EUR

# RULES

- Present available events for the requested city or type with prices before booking.
- If the user wants to book, follow this order:
    1. Confirm event name, date, seat category, number of tickets, and attendee name.
    2. Use `create_ticket_reservation` tool to create the reservation.
    3. Provide a detailed confirmation with booking reference, event, venue, category, price breakdown, and total.
- Set response status to input_required if asking for user confirmation.
- Set response status to error if there is an error while processing the request.
- Set response status to completed if the request is complete.
- DO NOT make up events or prices not listed above.
- All prices are in EUR per ticket.
"""
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def invoke(self, query, sessionId) -> str:
        model = LLM(
            model="vertex_ai/gemini-2.5-flash-lite",
        )
        ticket_agent = Agent(
            role="Ticket Reservation Agent",
            goal=(
                "Help user to find and book tickets for sports events, concerts, theatre, opera and other events in Europe."
            ),
            backstory=("You are an expert event ticket reservation agent specializing in European events."),
            verbose=False,
            allow_delegation=False,
            tools=[create_ticket_reservation],
            llm=model,
        )

        agent_task = Task(
            description=self.TaskInstruction,
            agent=ticket_agent,
            expected_output="Response to the user with event options or booking confirmation",
        )

        crew = Crew(
            tasks=[agent_task],
            agents=[ticket_agent],
            verbose=False,
            process=Process.sequential,
        )

        inputs = {"user_prompt": query, "session_id": sessionId}
        response = crew.kickoff(inputs)
        return response


if __name__ == "__main__":
    agent = TicketReservationAgent()
    result = agent.invoke("I want 2 tickets for Real Madrid vs Barcelona", "default_session")
    print(result)
