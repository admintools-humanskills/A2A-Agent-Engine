from google import genai
from google.genai import types
from pydantic import BaseModel
import uuid
import json
from dotenv import load_dotenv
import os

load_dotenv()

SYSTEM_INSTRUCTION = """
# INSTRUCTIONS

You are a specialized restaurant reservation assistant for major European cities.
Your sole purpose is to help users find restaurants, compare options, and create reservations.
If the user asks about anything other than restaurant availability or reservations, politely state that you can only assist with restaurant bookings.

# AVAILABLE RESTAURANTS

## Madrid
1. **DiverXO** (3 Michelin stars, Creative/Avant-garde) - Calle Padre Damian
   - Average price: 250 EUR/person | Dress code: Smart casual
   - Chef: Dabiz Munoz | Capacity: 40 seats | Hours: 13:30-15:30, 21:00-23:00

2. **Sobrino de Botin** (Traditional Castilian) - Calle Cuchilleros
   - Average price: 45 EUR/person | Dress code: Casual
   - World's oldest restaurant (1725) | Capacity: 120 seats | Hours: 13:00-16:00, 20:00-23:30

3. **Mercado de San Miguel** (Tapas Market) - Plaza de San Miguel
   - Average price: 25 EUR/person | Dress code: Casual
   - Gourmet food hall | Capacity: 200 seats | Hours: 10:00-24:00

4. **StreetXO** (Asian-Mediterranean Fusion) - Calle Serrano
   - Average price: 35 EUR/person | Dress code: Casual
   - By Dabiz Munoz | Capacity: 60 seats | Hours: 12:30-16:00, 20:00-23:30

5. **La Barraca** (Valencian/Paella) - Calle Reina
   - Average price: 40 EUR/person | Dress code: Casual
   - Paella specialists since 1935 | Capacity: 150 seats | Hours: 13:00-16:00, 20:30-23:30

## Barcelona
1. **El Celler de Can Roca** (3 Michelin stars, Creative Catalan) - Girona (near Barcelona)
   - Average price: 220 EUR/person | Dress code: Smart casual
   - Roca brothers | Capacity: 50 seats | Hours: 13:00-15:30, 20:30-23:00

2. **Tickets Bar** (Tapas/Molecular) - Avinguda del Parallel
   - Average price: 60 EUR/person | Dress code: Casual
   - By Albert Adria | Capacity: 80 seats | Hours: 19:00-23:30

3. **7 Portes** (Traditional Catalan) - Passeig Isabel II
   - Average price: 45 EUR/person | Dress code: Smart casual
   - Since 1836, famous paellas | Capacity: 300 seats | Hours: 13:00-01:00

4. **La Boqueria Market Restaurants** (Tapas/Seafood) - La Rambla
   - Average price: 20 EUR/person | Dress code: Casual
   - Multiple stalls | Capacity: 100+ seats | Hours: 08:00-20:30

## Paris
1. **Le Jules Verne** (1 Michelin star, French Gastronomy) - Eiffel Tower
   - Average price: 180 EUR/person | Dress code: Formal
   - Chef Frederic Anton | Capacity: 120 seats | Hours: 12:00-14:30, 19:00-22:30

2. **Le Comptoir du Pantheon** (French Bistro) - Rue Soufflot
   - Average price: 30 EUR/person | Dress code: Casual
   - Classic Parisian bistro | Capacity: 80 seats | Hours: 12:00-23:00

3. **L'Ambroisie** (3 Michelin stars, French Haute Cuisine) - Place des Vosges
   - Average price: 300 EUR/person | Dress code: Formal
   - Chef Bernard Pacaud | Capacity: 40 seats | Hours: 12:00-14:00, 20:00-22:00

4. **Chez Janou** (Provencal) - Rue Roger Verlomme
   - Average price: 35 EUR/person | Dress code: Casual
   - Famous chocolate mousse | Capacity: 100 seats | Hours: 12:00-15:00, 19:30-23:00

5. **Pink Mamma** (Italian) - Rue de Douai
   - Average price: 25 EUR/person | Dress code: Casual
   - Trendy Italian, 4 floors | Capacity: 250 seats | Hours: 12:00-23:30

## London
1. **The Ledbury** (2 Michelin stars, Modern British) - Notting Hill
   - Average price: 160 EUR/person | Dress code: Smart casual
   - Chef Brett Graham | Capacity: 55 seats | Hours: 12:00-14:00, 18:30-21:30

2. **Dishoom** (Indian/Bombay cafe) - Multiple locations
   - Average price: 30 EUR/person | Dress code: Casual
   - Bombay-style cafe | Capacity: 200 seats | Hours: 08:00-23:00

3. **Sketch** (European/Afternoon Tea) - Mayfair
   - Average price: 70 EUR/person | Dress code: Smart casual
   - Iconic pink room | Capacity: 120 seats | Hours: 12:00-14:30, 18:30-23:00

4. **Borough Market Restaurants** (Various) - Southwark
   - Average price: 20 EUR/person | Dress code: Casual
   - Food market since 1756 | Capacity: 300+ seats | Hours: 10:00-17:00

## Rome
1. **La Pergola** (3 Michelin stars, Italian Haute Cuisine) - Monte Mario
   - Average price: 250 EUR/person | Dress code: Formal
   - Chef Heinz Beck | Capacity: 60 seats | Hours: 19:30-23:00

2. **Roscioli** (Roman/Deli) - Via dei Giubbonari
   - Average price: 50 EUR/person | Dress code: Casual
   - Famous carbonara, wine cellar | Capacity: 50 seats | Hours: 12:30-15:30, 19:00-23:00

3. **Trattoria Da Enzo** (Traditional Roman) - Trastevere
   - Average price: 25 EUR/person | Dress code: Casual
   - Authentic cacio e pepe | Capacity: 40 seats | Hours: 12:30-15:00, 19:30-23:00

4. **Antico Arco** (Modern Roman) - Gianicolo Hill
   - Average price: 55 EUR/person | Dress code: Smart casual
   - Panoramic views | Capacity: 70 seats | Hours: 19:30-23:30

# RULES

- When ALL required information is provided (restaurant name, city, date, time, party size, guest name), proceed DIRECTLY to the reservation using the create_restaurant_reservation function WITHOUT asking for confirmation.
- If essential details are missing, ask ONLY for the missing details.
- If the user doesn't specify a restaurant, suggest options for the requested city with cuisine types and average prices, then book once they choose.
- After booking, provide a detailed confirmation with reservation ID, restaurant, date/time, party size, and estimated total.
- DO NOT invent restaurants or prices not listed above.
- All prices are in EUR per person.
"""


def create_restaurant_reservation(
    restaurant_name: str,
    city: str,
    date: str,
    time: str,
    party_size: int,
    guest_name: str,
    special_requests: str = "",
) -> dict:
    """Creates a restaurant table reservation.

    Args:
        restaurant_name: Name of the restaurant exactly as listed.
        city: City where the restaurant is located.
        date: Reservation date (YYYY-MM-DD).
        time: Reservation time (HH:MM).
        party_size: Number of guests.
        guest_name: Name for the reservation.
        special_requests: Any special requests (allergies, occasion, etc.).

    Returns:
        dict: Confirmation with reservation details.
    """
    price_map = {
        "DiverXO": 250, "Sobrino de Botin": 45, "Mercado de San Miguel": 25,
        "StreetXO": 35, "La Barraca": 40,
        "El Celler de Can Roca": 220, "Tickets Bar": 60, "7 Portes": 45,
        "La Boqueria Market Restaurants": 20,
        "Le Jules Verne": 180, "Le Comptoir du Pantheon": 30,
        "L'Ambroisie": 300, "Chez Janou": 35, "Pink Mamma": 25,
        "The Ledbury": 160, "Dishoom": 30, "Sketch": 70,
        "Borough Market Restaurants": 20,
        "La Pergola": 250, "Roscioli": 50, "Trattoria Da Enzo": 25,
        "Antico Arco": 55,
    }

    avg_price = price_map.get(restaurant_name, 40)
    estimated_total = avg_price * party_size
    reservation_id = f"RST-{uuid.uuid4().hex[:8].upper()}"

    result = {
        "reservation_id": reservation_id,
        "restaurant_name": restaurant_name,
        "city": city,
        "date": date,
        "time": time,
        "party_size": party_size,
        "guest_name": guest_name,
        "special_requests": special_requests,
        "estimated_price_per_person": avg_price,
        "estimated_total": estimated_total,
        "status": "confirmed",
    }
    print(f"=== Restaurant reservation created: {result} ===")
    return result


# Define the function declaration for Gemini function calling
restaurant_reservation_tool = types.FunctionDeclaration(
    name="create_restaurant_reservation",
    description="Creates a restaurant table reservation.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "restaurant_name": types.Schema(type=types.Type.STRING, description="Name of the restaurant exactly as listed."),
            "city": types.Schema(type=types.Type.STRING, description="City where the restaurant is located."),
            "date": types.Schema(type=types.Type.STRING, description="Reservation date (YYYY-MM-DD)."),
            "time": types.Schema(type=types.Type.STRING, description="Reservation time (HH:MM)."),
            "party_size": types.Schema(type=types.Type.INTEGER, description="Number of guests."),
            "guest_name": types.Schema(type=types.Type.STRING, description="Name for the reservation."),
            "special_requests": types.Schema(type=types.Type.STRING, description="Any special requests (allergies, occasion, etc.)."),
        },
        required=["restaurant_name", "city", "date", "time", "party_size", "guest_name"],
    ),
)

restaurant_tool = types.Tool(function_declarations=[restaurant_reservation_tool])


class RestaurantReservationAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.client = genai.Client(vertexai=True)
        self.model_id = "gemini-2.5-flash-lite"
        self.sessions: dict[str, list] = {}

    def invoke(self, query, sessionId) -> str:
        history = self.sessions.get(sessionId, [])
        history.append(types.Content(role="user", parts=[types.Part.from_text(text=query)]))

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[restaurant_tool],
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=history,
                config=config,
            )
        except Exception as e:
            print(f"Error calling GenAI: {e}")
            return f"Sorry, I encountered an error processing your request: {e}"

        max_iterations = 5
        for _ in range(max_iterations):
            if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
                break

            function_call_part = None
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_call_part = part
                    break

            if not function_call_part:
                break

            # Add assistant response to history
            history.append(response.candidates[0].content)

            fn_call = function_call_part.function_call
            fn_args = dict(fn_call.args) if fn_call.args else {}

            try:
                fn_result = create_restaurant_reservation(**fn_args)
            except Exception as e:
                print(f"Error executing function: {e}")
                fn_result = {"error": str(e)}

            # Add function response to history
            history.append(types.Content(
                role="user",
                parts=[types.Part.from_function_response(name=fn_call.name, response=fn_result)],
            ))

            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=history,
                    config=config,
                )
            except Exception as e:
                print(f"Error calling GenAI after function call: {e}")
                return f"Sorry, I encountered an error processing the reservation result: {e}"

        # Add final assistant response to history
        if response.candidates and response.candidates[0].content:
            history.append(response.candidates[0].content)

        self.sessions[sessionId] = history

        # Extract text safely
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            text_parts = [p.text for p in response.candidates[0].content.parts if p.text]
            if text_parts:
                return "\n".join(text_parts)

        return "Sorry, I could not generate a response. Please try again with more details."


if __name__ == "__main__":
    agent = RestaurantReservationAgent()
    result = agent.invoke("I want to book a table at Sobrino de Botin in Madrid for 2 people tomorrow at 20:00", "test")
    print(result)
