from fastapi import APIRouter
from pydantic import BaseModel, Field

from ...agents.shopping import answer_shopping_question
from ...agents.supervisor import AgentName, route_customer_message

router = APIRouter()


class AssistantMessage(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class AssistantReply(BaseModel):
    agent: str
    response: str
    products: list[dict[str, object]]


@router.post("/route")
def route_message(payload: AssistantMessage) -> dict[str, object]:
    """Route requests safely before the LangGraph agent layer calls MCP tools."""
    decision = route_customer_message(payload.message)
    return {
        "agent": decision.agent,
        "requires_human_approval": decision.requires_human_approval,
        "reason": decision.reason,
    }


@router.post("/chat", response_model=AssistantReply)
def chat(payload: AssistantMessage) -> AssistantReply:
    decision = route_customer_message(payload.message)
    if decision.agent is not AgentName.SHOPPING:
        return AssistantReply(agent=decision.agent, response=decision.reason, products=[])
    result = answer_shopping_question(payload.message)
    return AssistantReply(agent=AgentName.SHOPPING, response=str(result["response"]), products=result["products"])
