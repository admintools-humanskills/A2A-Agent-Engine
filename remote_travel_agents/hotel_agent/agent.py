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


class HotelReservation(BaseModel):
    reservation_id: str
    hotel_name: str
    room_type: str
    check_in: str
    check_out: str
    total_nights: int
    price_per_night: float
    total_price: float
    guest_name: str


@tool
def create_hotel_reservation(
    hotel_name: str,
    room_type: str,
    check_in_date: str,
    check_out_date: str,
    guest_name: str,
    num_guests: int,
) -> str:
    """Creates a hotel room reservation.

    Args:
        hotel_name: Name of the hotel.
        room_type: Type of room (e.g. Standard, Superior, Suite).
        check_in_date: Check-in date (YYYY-MM-DD).
        check_out_date: Check-out date (YYYY-MM-DD).
        guest_name: Name of the guest.
        num_guests: Number of guests.

    Returns:
        str: Confirmation message with reservation details.
    """
    try:
        from datetime import datetime

        d_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        d_out = datetime.strptime(check_out_date, "%Y-%m-%d")
        total_nights = (d_out - d_in).days
        if total_nights <= 0:
            return "Error: check-out date must be after check-in date."

        # Price lookup (simplified)
        price_map = {
            # Madrid
            "Hotel Ritz Madrid": {"Standard": 280, "Superior": 380, "Suite": 650, "Royal Suite": 1200},
            "Hotel Puerta del Sol": {"Standard": 95, "Superior": 140, "Suite": 220},
            "NH Collection Madrid Gran Via": {"Standard": 130, "Superior": 180, "Junior Suite": 290},
            "Hostal Madrid Centro": {"Standard": 55, "Double Superior": 75},
            # Barcelona
            "Hotel Arts Barcelona": {"Standard": 250, "Superior": 350, "Suite": 580, "Penthouse": 1100},
            "Hotel Casa Fuster": {"Standard": 180, "Superior": 260, "Suite": 420},
            "Generator Barcelona": {"Standard": 60, "Superior": 85},
            "Hotel 1898 Barcelona": {"Standard": 150, "Superior": 210, "Suite": 350},
            # Paris
            "Hotel Le Marais": {"Standard": 160, "Superior": 230, "Suite": 400},
            "Hotel Plaza Athenee": {"Standard": 450, "Superior": 650, "Suite": 1100, "Royal Suite": 2500},
            "Ibis Paris Montmartre": {"Standard": 85, "Superior": 110},
            "Hotel des Grands Boulevards": {"Standard": 140, "Superior": 200, "Suite": 320},
            # London
            "The Savoy London": {"Standard": 380, "Superior": 520, "Suite": 900, "Royal Suite": 2000},
            "Premier Inn London City": {"Standard": 90, "Superior": 120},
            "The Hoxton Shoreditch": {"Standard": 150, "Superior": 210, "Suite": 340},
            "Hub by Premier Inn Westminster": {"Standard": 75, "Double": 95},
            # Rome
            "Hotel de Russie Rome": {"Standard": 320, "Superior": 450, "Suite": 750},
            "Hotel Colosseum Roma": {"Standard": 100, "Superior": 145, "Suite": 230},
            "Hotel Raphael Rome": {"Standard": 220, "Superior": 310, "Suite": 500},
            "Generator Rome": {"Standard": 55, "Superior": 80},
        }

        hotel_prices = price_map.get(hotel_name, {})
        price_per_night = hotel_prices.get(room_type, 150)
        total_price = price_per_night * total_nights

        reservation_id = f"HTL-{uuid.uuid4().hex[:8].upper()}"
        reservation = HotelReservation(
            reservation_id=reservation_id,
            hotel_name=hotel_name,
            room_type=room_type,
            check_in=check_in_date,
            check_out=check_out_date,
            total_nights=total_nights,
            price_per_night=price_per_night,
            total_price=total_price,
            guest_name=guest_name,
        )
        print(f"=== Hotel reservation created: {reservation} ===")
    except Exception as e:
        print(f"Error creating reservation: {e}")
        return f"Error creating reservation: {e}"
    return f"Reservation confirmed: {reservation.model_dump()}"


class HotelReservationAgent:
    SYSTEM_INSTRUCTION = """
# INSTRUCTIONS

You are a specialized hotel reservation assistant for major European cities.
Your sole purpose is to help users find hotels, compare room types and prices, and create reservations.
If the user asks about anything other than hotel availability, pricing, or reservations, politely state that you can only assist with hotel bookings.

# AVAILABLE HOTELS

## Madrid
1. **Hotel Ritz Madrid** (5-star, Luxury) - Paseo del Prado
   - Standard Room: 280 EUR/night | Superior Room: 380 EUR/night | Suite: 650 EUR/night | Royal Suite: 1200 EUR/night
   - Amenities: Spa, rooftop terrace, Michelin restaurant, concierge

2. **NH Collection Madrid Gran Via** (4-star, Upscale) - Gran Via
   - Standard Room: 130 EUR/night | Superior Room: 180 EUR/night | Junior Suite: 290 EUR/night
   - Amenities: Rooftop pool, gym, restaurant

3. **Hotel Puerta del Sol** (3-star, Mid-range) - Sol district
   - Standard Room: 95 EUR/night | Superior Room: 140 EUR/night | Suite: 220 EUR/night
   - Amenities: Free WiFi, breakfast included, central location

4. **Hostal Madrid Centro** (2-star, Budget) - Centro
   - Standard Room: 55 EUR/night | Double Superior: 75 EUR/night
   - Amenities: Free WiFi, shared lounge

## Barcelona
1. **Hotel Arts Barcelona** (5-star, Luxury) - Port Olimpic
   - Standard Room: 250 EUR/night | Superior Room: 350 EUR/night | Suite: 580 EUR/night | Penthouse: 1100 EUR/night
   - Amenities: Private beach, spa, 2 Michelin-star restaurant, infinity pool

2. **Hotel Casa Fuster** (4-star, Upscale) - Passeig de Gracia
   - Standard Room: 180 EUR/night | Superior Room: 260 EUR/night | Suite: 420 EUR/night
   - Amenities: Rooftop pool, jazz bar, modernist building

3. **Hotel 1898 Barcelona** (4-star, Upscale) - La Rambla
   - Standard Room: 150 EUR/night | Superior Room: 210 EUR/night | Suite: 350 EUR/night
   - Amenities: Rooftop pool, colonial-style decor

4. **Generator Barcelona** (2-star, Budget) - Gracia
   - Standard Room: 60 EUR/night | Superior Room: 85 EUR/night
   - Amenities: Social spaces, terrace, bar

## Paris
1. **Hotel Plaza Athenee** (5-star Palace, Luxury) - Avenue Montaigne
   - Standard Room: 450 EUR/night | Superior Room: 650 EUR/night | Suite: 1100 EUR/night | Royal Suite: 2500 EUR/night
   - Amenities: Alain Ducasse restaurant, Dior spa, Eiffel Tower views

2. **Hotel des Grands Boulevards** (4-star, Upscale) - 2nd arrondissement
   - Standard Room: 140 EUR/night | Superior Room: 200 EUR/night | Suite: 320 EUR/night
   - Amenities: Rooftop bar, Italian restaurant, garden courtyard

3. **Hotel Le Marais** (3-star, Mid-range) - Le Marais
   - Standard Room: 160 EUR/night | Superior Room: 230 EUR/night | Suite: 400 EUR/night
   - Amenities: Central location, breakfast, concierge

4. **Ibis Paris Montmartre** (2-star, Budget) - Montmartre
   - Standard Room: 85 EUR/night | Superior Room: 110 EUR/night
   - Amenities: 24h reception, near Sacre-Coeur

## London
1. **The Savoy London** (5-star, Luxury) - Strand
   - Standard Room: 380 EUR/night | Superior Room: 520 EUR/night | Suite: 900 EUR/night | Royal Suite: 2000 EUR/night
   - Amenities: Thames views, Kaspar's restaurant, spa, butler service

2. **The Hoxton Shoreditch** (4-star, Boutique) - Shoreditch
   - Standard Room: 150 EUR/night | Superior Room: 210 EUR/night | Suite: 340 EUR/night
   - Amenities: Lobby restaurant, rooftop, co-working space

3. **Premier Inn London City** (3-star, Mid-range) - City of London
   - Standard Room: 90 EUR/night | Superior Room: 120 EUR/night
   - Amenities: Restaurant, free WiFi, near Tower Bridge

4. **Hub by Premier Inn Westminster** (2-star, Budget) - Westminster
   - Standard Room: 75 EUR/night | Double: 95 EUR/night
   - Amenities: Compact rooms, app-controlled, central location

## Rome
1. **Hotel de Russie Rome** (5-star, Luxury) - Piazza del Popolo
   - Standard Room: 320 EUR/night | Superior Room: 450 EUR/night | Suite: 750 EUR/night
   - Amenities: Secret garden, spa, Le Jardin restaurant, Piazza del Popolo views

2. **Hotel Raphael Rome** (4-star, Upscale) - Piazza Navona
   - Standard Room: 220 EUR/night | Superior Room: 310 EUR/night | Suite: 500 EUR/night
   - Amenities: Rooftop terrace with Pantheon views, art collection

3. **Hotel Colosseum Roma** (3-star, Mid-range) - Near Colosseum
   - Standard Room: 100 EUR/night | Superior Room: 145 EUR/night | Suite: 230 EUR/night
   - Amenities: Colosseum views, breakfast terrace, free WiFi

4. **Generator Rome** (2-star, Budget) - Termini
   - Standard Room: 55 EUR/night | Superior Room: 80 EUR/night
   - Amenities: Social spaces, bar, tours desk

# RULES

- When ALL required information is provided (hotel name, room type, check-in date, check-out date, guest name, number of guests), proceed DIRECTLY to the reservation using `create_hotel_reservation` WITHOUT asking for confirmation.
- If essential details are missing, ask ONLY for the missing details.
- If the user doesn't specify a hotel, suggest options for the requested city with prices, then book once they choose.
- After booking, provide a detailed confirmation with reservation ID, hotel, room type, dates, number of nights, price breakdown, and total.
- DO NOT invent hotels or prices not listed above.
- Prices are per night in EUR.
"""
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.model = ChatVertexAI(
            model="gemini-2.5-flash-lite",
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        )
        self.tools = [create_hotel_reservation]
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
