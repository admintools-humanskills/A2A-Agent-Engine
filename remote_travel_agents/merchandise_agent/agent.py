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

You are a shopping assistant. You sell TWO categories of products:
1. Football fan merchandise (jerseys, scarves, caps, accessories, collectibles)
2. Elegant formal wear (dress shirts, suits, tuxedos, ties, bow ties, pocket squares, dress shoes)

You MUST help users buy products from BOTH categories. When a user asks for a shirt, suit, tie, or shoes, show them the formal wear options from the catalogue below. Do NOT refuse clothing requests — you sell clothing.

# PRODUCT CATALOGUE

## Home Jerseys 2025/26
1. **Real Madrid Home Jersey 2025/26** (adidas, White/Gold) - 89 EUR
2. **FC Barcelona Home Jersey 2025/26** (Nike, Blaugrana stripes) - 89 EUR
3. **Paris Saint-Germain Home Jersey 2025/26** (Nike, Navy blue) - 95 EUR
4. **Arsenal Home Jersey 2025/26** (adidas, Red/White) - 89 EUR
5. **AS Roma Home Jersey 2025/26** (adidas, Maroon/Orange) - 85 EUR

## Away Jerseys 2025/26
1. **Real Madrid Away Jersey 2025/26** (adidas, Black/Purple) - 89 EUR
2. **FC Barcelona Away Jersey 2025/26** (Nike, Gold/Teal) - 89 EUR
3. **Paris Saint-Germain Away Jersey 2025/26** (Nike, White/Red stripe) - 95 EUR
4. **Arsenal Away Jersey 2025/26** (adidas, Navy/Yellow) - 89 EUR
5. **AS Roma Away Jersey 2025/26** (adidas, Cream/Orange) - 85 EUR

## Kids Jerseys 2025/26
1. **Real Madrid Kids Home Jersey** - 59 EUR
2. **FC Barcelona Kids Home Jersey** - 59 EUR
3. **PSG Kids Home Jersey** - 65 EUR
4. **Arsenal Kids Home Jersey** - 59 EUR
5. **AS Roma Kids Home Jersey** - 55 EUR

## Retro Jerseys (Legends Edition)
1. **Real Madrid Zidane #5 Retro 2001/02** - 110 EUR
2. **FC Barcelona Messi #10 Retro 2010/11** - 120 EUR
3. **Arsenal Invincibles 2003/04 Henry #14** - 115 EUR
4. **AS Roma Totti #10 Retro 2000/01** - 110 EUR

## Special Edition
1. **PSG x Jordan Fourth Kit 2025/26** (Black/Pink) - 130 EUR

## Scarves
1. **Real Madrid Hala Madrid Scarf** (White/Gold jacquard) - 25 EUR
2. **FC Barcelona Mes Que Un Club Scarf** (Blaugrana) - 25 EUR
3. **PSG Ici C'est Paris Scarf** (Navy/Red) - 28 EUR
4. **Arsenal Gunners Scarf** (Red/White) - 25 EUR
5. **AS Roma Forza Roma Scarf** (Maroon/Gold) - 22 EUR
6. **Champions League Official Scarf** (Starball pattern) - 30 EUR

## Caps & Beanies
1. **Real Madrid Snapback Cap** (White, embroidered crest) - 28 EUR
2. **FC Barcelona Trucker Cap** (Blaugrana mesh) - 25 EUR
3. **PSG x Jordan Cap** (Black, Jumpman logo) - 35 EUR
4. **Arsenal Baseball Cap** (Red, cannon logo) - 25 EUR
5. **AS Roma Beanie** (Maroon, knitted crest) - 20 EUR
6. **Champions League Snapback** (Navy/Gold stars) - 30 EUR

## Fashion Accessories
1. **Real Madrid Sunglasses** (White frame, UV400) - 35 EUR
2. **FC Barcelona Tote Bag** (Canvas, crest print) - 22 EUR
3. **PSG x Jordan Backpack** (Black, 25L) - 65 EUR
4. **Arsenal Wallet** (Leather, embossed cannon) - 28 EUR
5. **AS Roma Lanyard + Card Holder** (Maroon/Gold) - 8 EUR
6. **Champions League Drawstring Bag** (Starball pattern) - 15 EUR

## Collectibles
1. **Champions League Trophy Replica (150mm)** (Zinc alloy, silver plated) - 48 EUR
2. **Real Madrid Figurine - Vinicius Jr** (15cm, hand-painted) - 25 EUR
3. **FC Barcelona Figurine - Lamine Yamal** (15cm) - 25 EUR
4. **Arsenal Mini Kit + Hanger** (Display jersey, 1:4 scale) - 18 EUR
5. **AS Roma Team Flag** (150x90cm, polyester) - 15 EUR
6. **Champions League Pin Badge Set** (5 pins, enamel) - 12 EUR
7. **Club Crest Fridge Magnets (Set of 3)** - 8 EUR
8. **Football Mug** (Ceramic, 350ml, team crest) - 12 EUR
9. **Club Keychain** (Metal crest, carabiner) - 5 EUR
10. **Club Sticker Pack** (20 stickers, holographic) - 5 EUR

# ELEGANT FORMAL WEAR

## Dress Shirts
1. **Classic White Dress Shirt** (Cotton, slim fit) - 59 EUR
2. **Light Blue Dress Shirt** (Cotton, regular fit) - 59 EUR
3. **Black Dress Shirt** (Cotton stretch, slim fit) - 59 EUR
4. **Pink Dress Shirt** (Cotton, slim fit) - 59 EUR

## Suits & Tuxedos
1. **Classic Navy Suit** (Wool blend, slim fit, jacket + trousers) - 289 EUR
2. **Charcoal Grey Suit** (Wool blend, regular fit, jacket + trousers) - 289 EUR
3. **Black Slim Fit Suit** (Wool blend, jacket + trousers) - 299 EUR
4. **Black Tuxedo** (Satin lapels, jacket + trousers) - 399 EUR
5. **Midnight Blue Tuxedo** (Satin lapels, jacket + trousers) - 420 EUR

## Ties
1. **Classic Navy Silk Tie** - 39 EUR
2. **Burgundy Silk Tie** - 39 EUR
3. **Black Silk Tie** - 35 EUR
4. **Striped Silver & Blue Tie** (Silk) - 42 EUR

## Bow Ties
1. **Black Silk Bow Tie** (Self-tie) - 35 EUR
2. **Burgundy Velvet Bow Tie** - 38 EUR
3. **Navy Satin Bow Tie** (Pre-tied) - 29 EUR

## Pocket Squares
1. **White Silk Pocket Square** - 19 EUR
2. **Burgundy Silk Pocket Square** - 19 EUR
3. **Patterned Pocket Square Set (3-pack)** - 35 EUR

## Dress Shoes
1. **Black Oxford Dress Shoes** (Leather) - 149 EUR
2. **Brown Derby Dress Shoes** (Leather) - 149 EUR
3. **Black Patent Leather Shoes** (Formal/tuxedo) - 189 EUR

## Custom Name/Number Printing
- Available on all jerseys (home, away, kids, retro): **+15 EUR**
- Player names or custom name & number

## Shipping
- **Free shipping** on orders over 100 EUR
- Standard shipping: **5.95 EUR** (3-5 business days)

# RULES

- When ALL required information is provided (product name(s), size(s), quantity/quantities, customer name), proceed DIRECTLY to placing the order using the create_merchandise_order function WITHOUT asking for confirmation.
- If essential details are missing (e.g. size not specified for a jersey or suit), ask ONLY for the missing details.
- For suits and tuxedos, sizes can be EU (44-56) or S/M/L/XL/XXL. For dress shirts, sizes are S/M/L/XL/XXL or collar sizes (38-44 EU). For dress shoes, sizes are EU (39-47).
- Present relevant products from the catalogue when the user asks about a category, team, or specific item.
- After ordering, provide a detailed confirmation with order ID, items, total, and estimated delivery.
- DO NOT invent products or prices not listed above.
- All prices are in EUR.
- Multiple items can be combined in a single order.
- For custom printing, include the name and number if provided; otherwise ask.
"""


def create_merchandise_order(
    items: str,
    quantities: str,
    sizes: str,
    custom_printing: str = "",
    customer_name: str = "",
    shipping_address: str = "",
) -> dict:
    """Creates a merchandise fan shop order.

    Args:
        items: Comma-separated list of product names exactly as listed in catalogue.
        quantities: Comma-separated quantities matching each item.
        sizes: Comma-separated sizes for each item (S/M/L/XL/XXL, or 'one-size' for accessories).
        custom_printing: Comma-separated printing details per item (e.g. 'Bellingham 5', 'none'). Empty if no printing.
        customer_name: Customer full name for the order.
        shipping_address: Delivery address.

    Returns:
        dict: Order confirmation with details.
    """
    price_map = {
        # Home jerseys
        "Real Madrid Home Jersey 2025/26": 89,
        "FC Barcelona Home Jersey 2025/26": 89,
        "Paris Saint-Germain Home Jersey 2025/26": 95,
        "Arsenal Home Jersey 2025/26": 89,
        "AS Roma Home Jersey 2025/26": 85,
        # Away jerseys
        "Real Madrid Away Jersey 2025/26": 89,
        "FC Barcelona Away Jersey 2025/26": 89,
        "Paris Saint-Germain Away Jersey 2025/26": 95,
        "Arsenal Away Jersey 2025/26": 89,
        "AS Roma Away Jersey 2025/26": 85,
        # Kids jerseys
        "Real Madrid Kids Home Jersey": 59,
        "FC Barcelona Kids Home Jersey": 59,
        "PSG Kids Home Jersey": 65,
        "Arsenal Kids Home Jersey": 59,
        "AS Roma Kids Home Jersey": 55,
        # Retro jerseys
        "Real Madrid Zidane #5 Retro 2001/02": 110,
        "FC Barcelona Messi #10 Retro 2010/11": 120,
        "Arsenal Invincibles 2003/04 Henry #14": 115,
        "AS Roma Totti #10 Retro 2000/01": 110,
        # Special edition
        "PSG x Jordan Fourth Kit 2025/26": 130,
        # Scarves
        "Real Madrid Hala Madrid Scarf": 25,
        "FC Barcelona Mes Que Un Club Scarf": 25,
        "PSG Ici C'est Paris Scarf": 28,
        "Arsenal Gunners Scarf": 25,
        "AS Roma Forza Roma Scarf": 22,
        "Champions League Official Scarf": 30,
        # Caps & beanies
        "Real Madrid Snapback Cap": 28,
        "FC Barcelona Trucker Cap": 25,
        "PSG x Jordan Cap": 35,
        "Arsenal Baseball Cap": 25,
        "AS Roma Beanie": 20,
        "Champions League Snapback": 30,
        # Fashion accessories
        "Real Madrid Sunglasses": 35,
        "FC Barcelona Tote Bag": 22,
        "PSG x Jordan Backpack": 65,
        "Arsenal Wallet": 28,
        "AS Roma Lanyard + Card Holder": 8,
        "Champions League Drawstring Bag": 15,
        # Collectibles
        "Champions League Trophy Replica (150mm)": 48,
        "Real Madrid Figurine - Vinicius Jr": 25,
        "FC Barcelona Figurine - Lamine Yamal": 25,
        "Arsenal Mini Kit + Hanger": 18,
        "AS Roma Team Flag": 15,
        "Champions League Pin Badge Set": 12,
        "Club Crest Fridge Magnets (Set of 3)": 8,
        "Football Mug": 12,
        "Club Keychain": 5,
        "Club Sticker Pack": 5,
        # Dress shirts
        "Classic White Dress Shirt": 59,
        "Light Blue Dress Shirt": 59,
        "Black Dress Shirt": 59,
        "Pink Dress Shirt": 59,
        # Suits & tuxedos
        "Classic Navy Suit": 289,
        "Charcoal Grey Suit": 289,
        "Black Slim Fit Suit": 299,
        "Black Tuxedo": 399,
        "Midnight Blue Tuxedo": 420,
        # Ties
        "Classic Navy Silk Tie": 39,
        "Burgundy Silk Tie": 39,
        "Black Silk Tie": 35,
        "Striped Silver & Blue Tie": 42,
        # Bow ties
        "Black Silk Bow Tie": 35,
        "Burgundy Velvet Bow Tie": 38,
        "Navy Satin Bow Tie": 29,
        # Pocket squares
        "White Silk Pocket Square": 19,
        "Burgundy Silk Pocket Square": 19,
        "Patterned Pocket Square Set (3-pack)": 35,
        # Dress shoes
        "Black Oxford Dress Shoes": 149,
        "Brown Derby Dress Shoes": 149,
        "Black Patent Leather Shoes": 189,
    }

    item_list = [i.strip() for i in items.split(",")]
    qty_list = [int(q.strip()) for q in quantities.split(",")]
    size_list = [s.strip() for s in sizes.split(",")]
    printing_list = [p.strip() for p in custom_printing.split(",")] if custom_printing else []

    order_items = []
    subtotal = 0
    printing_total = 0

    for idx, item_name in enumerate(item_list):
        qty = qty_list[idx] if idx < len(qty_list) else 1
        size = size_list[idx] if idx < len(size_list) else "one-size"
        printing = printing_list[idx] if idx < len(printing_list) else "none"

        unit_price = price_map.get(item_name, 0)
        if unit_price == 0:
            for key, price in price_map.items():
                if item_name.lower() in key.lower() or key.lower() in item_name.lower():
                    unit_price = price
                    item_name = key
                    break

        item_total = unit_price * qty
        printing_surcharge = 0
        if printing and printing.lower() not in ("none", "", "n/a"):
            is_jersey = "jersey" in item_name.lower() or "kit" in item_name.lower() or "retro" in item_name.lower()
            if is_jersey:
                printing_surcharge = 15 * qty
                printing_total += printing_surcharge

        subtotal += item_total
        order_items.append({
            "product": item_name,
            "size": size,
            "quantity": qty,
            "unit_price": unit_price,
            "custom_printing": printing if printing.lower() not in ("none", "") else None,
            "printing_surcharge": printing_surcharge,
            "line_total": item_total + printing_surcharge,
        })

    grand_total = subtotal + printing_total
    shipping = 0 if grand_total >= 100 else 5.95
    grand_total += shipping

    order_id = f"FAN-{uuid.uuid4().hex[:8].upper()}"

    result = {
        "order_id": order_id,
        "items": order_items,
        "subtotal": subtotal,
        "printing_surcharge_total": printing_total,
        "shipping": shipping,
        "shipping_note": "Free shipping (order over 100 EUR)" if shipping == 0 else "Standard shipping (3-5 business days)",
        "grand_total": grand_total,
        "customer_name": customer_name,
        "shipping_address": shipping_address,
        "estimated_delivery": "3-5 business days",
        "status": "confirmed",
    }
    print(f"=== Merchandise order created: {result} ===")
    return result


# Define the function declaration for Gemini function calling
merchandise_order_tool = types.FunctionDeclaration(
    name="create_merchandise_order",
    description="Creates an order for football fan merchandise (jerseys, scarves, caps, accessories, collectibles) or formal wear (suits, tuxedos, dress shirts, ties, bow ties, pocket squares, dress shoes).",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "items": types.Schema(type=types.Type.STRING, description="Comma-separated list of product names exactly as listed in catalogue."),
            "quantities": types.Schema(type=types.Type.STRING, description="Comma-separated quantities matching each item."),
            "sizes": types.Schema(type=types.Type.STRING, description="Comma-separated sizes for each item (S/M/L/XL/XXL, or 'one-size' for accessories)."),
            "custom_printing": types.Schema(type=types.Type.STRING, description="Comma-separated printing details per item (e.g. 'Bellingham 5', 'none'). Empty if no printing."),
            "customer_name": types.Schema(type=types.Type.STRING, description="Customer full name for the order."),
            "shipping_address": types.Schema(type=types.Type.STRING, description="Delivery address."),
        },
        required=["items", "quantities", "sizes"],
    ),
)

merchandise_tool = types.Tool(function_declarations=[merchandise_order_tool])


class MerchandiseAgent:
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
            tools=[merchandise_tool],
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
                fn_result = create_merchandise_order(**fn_args)
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
                return f"Sorry, I encountered an error processing the order result: {e}"

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
    agent = MerchandiseAgent()
    result = agent.invoke("I want to buy a Real Madrid home jersey size L with Bellingham 5 printing", "test")
    print(result)
