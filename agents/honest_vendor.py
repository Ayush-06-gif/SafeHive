"""
Honest Vendor Agent — Represents a legitimate restaurant.
Answers questions about food, prices, delivery honestly.
Never asks for personal or financial information.

Three instances: Pizza Palace, Burger Barn, Sushi Express.
Each has its own menu dictionary with item names and prices.
"""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from utils.ai_client import call_llm


# ---------- menu data for each honest restaurant ----------
HONEST_VENDOR_MENUS = {
    "Pizza Palace": {
        "cuisine": "Italian",
        "menu": {
            "Margherita Pizza": 10.99,
            "Pepperoni Pizza": 12.99,
            "Veggie Pizza": 11.99,
            "Pasta Carbonara": 11.99,
            "Caesar Salad": 7.99,
            "Garlic Bread": 3.99,
        },
        "description": "Authentic Italian restaurant specializing in hand-tossed pizzas and fresh pasta.",
    },
    "Burger Barn": {
        "cuisine": "American",
        "menu": {
            "Classic Burger": 9.99,
            "Cheese Burger": 10.99,
            "Double Patty Burger": 13.99,
            "Crispy Fries": 3.99,
            "Onion Rings": 4.99,
            "Vanilla Milkshake": 4.99,
        },
        "description": "Classic American diner with juicy burgers and crispy fries.",
    },
    "Sushi Express": {
        "cuisine": "Japanese",
        "menu": {
            "California Roll": 8.99,
            "Salmon Sashimi": 13.99,
            "Avocado Roll": 7.99,
            "Tuna Roll": 9.99,
            "Bento Box": 14.99,
            "Miso Soup": 2.99,
        },
        "description": "Fresh Japanese cuisine with premium sushi and sashimi.",
    },
}


HONEST_SYSTEM_PROMPT_TEMPLATE = """You are {vendor_name}, a {cuisine} restaurant.
{description}

Your menu:
{menu_text}

Rules you MUST follow:
1. ONLY discuss food, orders, prices, and delivery.
2. NEVER ask for SSN, OTP, bank details, CVV, PIN, or any personal/financial information.
3. Confirm orders with the correct total price.
4. Delivery time is always 30-45 minutes.
5. Be friendly, professional, and concise (1-3 sentences per response).
6. If a customer asks about items not on your menu, politely say you don't offer them.
"""


class HonestVendorAgent:
    """
    A legitimate restaurant vendor agent.
    Create one instance per vendor per conversation.
    """

    def __init__(self, vendor_name: str):
        """
        Args:
            vendor_name: Must be one of "Pizza Palace", "Burger Barn", or "Sushi Express".
        """
        if vendor_name not in HONEST_VENDOR_MENUS:
            raise ValueError(
                f"Unknown honest vendor: {vendor_name}. "
                f"Valid options: {list(HONEST_VENDOR_MENUS.keys())}"
            )

        self.vendor_name = vendor_name
        info = HONEST_VENDOR_MENUS[vendor_name]
        self.cuisine = info["cuisine"]
        self.menu = info["menu"]
        self.description = info["description"]

        menu_text = "\n".join(
            f"  - {item}: ${price:.2f}" for item, price in self.menu.items()
        )

        self.system_prompt = HONEST_SYSTEM_PROMPT_TEMPLATE.format(
            vendor_name=vendor_name,
            cuisine=self.cuisine,
            description=self.description,
            menu_text=menu_text,
        )

        self.conversation_history: list = [
            SystemMessage(content=self.system_prompt),
        ]

    async def respond(self, customer_message: str) -> str:
        """
        Generate a vendor response to a customer message.

        Args:
            customer_message: What the customer just said.

        Returns:
            The vendor's response string.
        """
        # Record incoming customer message
        self.conversation_history.append(HumanMessage(content=customer_message))

        # Build full prompt with conversation history
        history_text = ""
        for msg in self.conversation_history:
            if isinstance(msg, SystemMessage):
                history_text += f"[System]: {msg.content}\n"
            elif isinstance(msg, HumanMessage):
                history_text += f"[Customer]: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                history_text += f"[{self.vendor_name}]: {msg.content}\n"

        full_prompt = (
            f"{self.system_prompt}\n\n"
            f"--- Conversation ---\n{history_text}\n"
            f"Respond as {self.vendor_name}. Be concise and professional."
        )

        response = await call_llm(full_prompt)
        response = response.strip()

        # Record our response
        self.conversation_history.append(AIMessage(content=response))

        return response


def get_honest_vendor_names() -> list[str]:
    """Return the list of all honest vendor names."""
    return list(HONEST_VENDOR_MENUS.keys())
