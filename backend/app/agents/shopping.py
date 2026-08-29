"""LangGraph shopping assistant backed by a local Ollama model."""

from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

from ..core.config import get_settings
from ..mcp_server import search_catalog

settings = get_settings()


class ShoppingState(TypedDict):
    message: str
    products: list[dict[str, object]]
    response: str


def catalog_tool(state: ShoppingState) -> dict[str, object]:
    products = search_catalog(state["message"], limit=5)
    # Natural-language prompts often contain a use case rather than an exact
    # product name. Fall back to the current catalog, never fabricated data.
    return {"products": products or search_catalog("", limit=5)}


def respond(state: ShoppingState) -> dict[str, str]:
    products = state["products"]
    if not products:
        return {"response": "I couldn't find a matching product in the current catalog. Try a broader search."}
    facts = "\n".join(f"- {item['name']} | {item['price']} {item['currency']} | rating {item['rating']} | {item['description']}" for item in products)
    prompt = "You are ShopPilot AI, a concise shopping assistant. Use only the catalog facts below. Do not invent stock, price, features, policies, or availability. Give a brief helpful recommendation.\n\n" + f"Customer question: {state['message']}\n\nCatalog facts:\n{facts}"
    try:
        llm = ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url, temperature=0.2)
        answer = llm.invoke(prompt).content
        return {"response": answer if isinstance(answer, str) else str(answer)}
    except Exception:
        names = ", ".join(str(item["name"]) for item in products[:3])
        return {"response": f"I found these catalog matches: {names}. Start the Ollama service for an AI-written comparison."}


workflow = StateGraph(ShoppingState)
workflow.add_node("catalog_tool", catalog_tool)
workflow.add_node("respond", respond)
workflow.add_edge(START, "catalog_tool")
workflow.add_edge("catalog_tool", "respond")
workflow.add_edge("respond", END)
shopping_graph = workflow.compile()


def answer_shopping_question(message: str) -> dict[str, object]:
    return shopping_graph.invoke({"message": message, "products": [], "response": ""})
