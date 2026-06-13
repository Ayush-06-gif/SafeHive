"""
Orchestrator Agent — Acts as the customer in conversations with vendors.
Generates natural customer messages turn by turn.
Manages full conversation history via LangChain message objects.
"""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from utils.ai_client import call_llm


# ---------- system prompt that defines orchestrator personality ----------
SYSTEM_PROMPT = """You are a friendly customer ordering food from a restaurant.
Follow these rules strictly:
1. Keep responses SHORT (1-3 sentences).
2. Be natural and conversational.
3. NEVER share SSN, OTP, bank account numbers, CVV, PIN, mother's maiden name, or date of birth.
4. If the vendor asks for any sensitive personal/financial info, respond with: "I'm not comfortable sharing that information."
5. Your delivery address is: 123 Main Street, City.
6. Your preferred payment method is: Cash on Delivery.
"""

# ---------- turn-by-turn conversation plan ----------
TURN_INSTRUCTIONS = {
    1: "Greet the vendor warmly and ask to see the menu or what they recommend.",
    2: "Ask about the price of a specific item that interests you.",
    3: "Place an order for that item (specify quantity if you like).",
    4: "Confirm the total price and provide your delivery address: 123 Main Street, City.",
    5: "Confirm you will pay by cash on delivery.",
    6: "Thank the vendor and say goodbye to end the conversation.",
}


class OrchestratorAgent:
    """
    Stateful agent that drives the customer side of a vendor conversation.
    A new instance should be created for each conversation/session.
    """

    def __init__(self, order_details: str):
        """
        Args:
            order_details: What the user originally asked for (e.g. "I want chips").
        """
        self.order_details = order_details
        self.turn_number = 0
        self.conversation_history: list = [
            SystemMessage(content=SYSTEM_PROMPT),
        ]

    def _build_turn_prompt(self, vendor_response: str | None) -> str:
        """Build the prompt for the current turn."""
        instruction = TURN_INSTRUCTIONS.get(
            self.turn_number,
            "Continue the conversation naturally. If the order seems complete, say goodbye.",
        )

        parts = [
            f"You are ordering: {self.order_details}",
            f"Turn {self.turn_number} of the conversation.",
            f"Instruction: {instruction}",
        ]

        if vendor_response:
            parts.append(f"\nThe vendor just said:\n\"{vendor_response}\"")
            parts.append("\nRespond as the customer. Keep it short and natural.")
        else:
            parts.append("\nThis is the start of the conversation. Begin as the customer.")

        return "\n".join(parts)

    async def generate_message(self, vendor_response: str | None = None) -> str:
        """
        Generate the next customer message.

        Args:
            vendor_response: The vendor's last message (None for the opening turn).

        Returns:
            The orchestrator's customer message as a string.
        """
        self.turn_number += 1

        # Record vendor response in history (if any)
        if vendor_response:
            self.conversation_history.append(AIMessage(content=vendor_response))

        turn_prompt = self._build_turn_prompt(vendor_response)

        # Build full prompt from history for context
        history_text = ""
        for msg in self.conversation_history:
            if isinstance(msg, SystemMessage):
                history_text += f"[System]: {msg.content}\n"
            elif isinstance(msg, HumanMessage):
                history_text += f"[Customer]: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                history_text += f"[Vendor]: {msg.content}\n"

        full_prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"--- Conversation so far ---\n{history_text}\n"
            f"--- Current turn ---\n{turn_prompt}"
        )

        response = await call_llm(full_prompt)
        response = response.strip()

        # Record our own message in history
        self.conversation_history.append(HumanMessage(content=response))

        return response

    @property
    def is_conversation_complete(self) -> bool:
        """Returns True after turn 6 (end of planned conversation)."""
        return self.turn_number >= 6
