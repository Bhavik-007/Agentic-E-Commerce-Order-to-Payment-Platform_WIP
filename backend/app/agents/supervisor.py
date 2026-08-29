from dataclasses import dataclass
from enum import StrEnum


class AgentName(StrEnum):
    SHOPPING = "shopping"
    ORDER = "order"
    PAYMENT = "payment"
    SUPPORT = "support"
    REFUND = "refund"


@dataclass(frozen=True)
class RoutingDecision:
    agent: AgentName
    requires_human_approval: bool
    reason: str


def route_customer_message(message: str) -> RoutingDecision:
    """Deterministic guardrail before LangGraph invokes an agent or MCP tool."""
    text = message.casefold()
    if any(term in text for term in ("refund", "return money")):
        return RoutingDecision(AgentName.REFUND, True, "Refunds require human approval before any payment action.")
    if any(term in text for term in ("pay", "payment", "razorpay")):
        return RoutingDecision(AgentName.PAYMENT, True, "Payment actions require an authenticated checkout flow.")
    if any(term in text for term in ("cancel", "add to cart", "remove from cart", "checkout")):
        return RoutingDecision(AgentName.ORDER, False, "Order and cart request.")
    if any(term in text for term in ("where is", "track", "order status", "delivery")):
        return RoutingDecision(AgentName.SUPPORT, False, "Order support request.")
    return RoutingDecision(AgentName.SHOPPING, False, "Catalog discovery request.")
