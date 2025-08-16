# bot/agents.py
import os
import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.schema import HumanMessage
from .rag import retrieve_docs

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- LLM setup ---
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not set in environment")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=gemini_api_key
)

# ======================================================
# 1. Query Classifier (Direct LLM, no ReAct)
# ======================================================
classifier_prompt = PromptTemplate.from_template("""
You are a query classification agent for workplace questions.
Classify the query into one of the following categories:

- RAG_AGENT → HR, Company Policy, Employee Handbook, internal documents
- WEBSEARCH_AGENT → general company/employee info not in internal docs
- OTHER → greetings, chit-chat, or unclear queries

Output format (strict JSON):
{{
  "route": "<RAG_AGENT | WEBSEARCH_AGENT | IT_SUPPORT | OTHER>",
  "reply": "<if OTHER, provide a friendly direct reply, else empty>"
}}

Query: {query}
""")

def run_classifier(query: str) -> dict:
    """Run classifier directly via LLM (no tools)."""
    try:
        logger.info(f"[Classifier] Query: {query}")
        resp = llm.invoke([HumanMessage(content=classifier_prompt.format(query=query))])
        data = json.loads(resp.content)
        logger.info(f"[Classifier] Result: {data}")
        return data
    except Exception as e:
        logger.error(f"[Classifier] Error: {e}")
        return {"route": "OTHER", "reply": "Sorry, I didn’t understand. Can you rephrase?"}

# ======================================================
# 2. RAG AgentExecutor
# ======================================================
def retrieve_tool_func(query):
    docs = retrieve_docs(query, k=3)
    if not docs:
        return "No relevant documents found."
    return "\n\n".join([doc.page_content for doc in docs])

rag_tools = [
    Tool(
        name="retrieve_documents",
        func=retrieve_tool_func,
        description="Retrieve relevant company documents for the query."
    )
]

rag_prompt = PromptTemplate.from_template("""
You are a helpful assistant answering workplace questions using company documents.

You have access to the following tools:
{tools}

Tool names: {tool_names}

Always first use the `retrieve_documents` tool to fetch relevant context.

Format strictly:
Thought: ...
Action: <tool name>
Action Input: <tool input>
Observation: <tool output>
... repeat as needed
Thought: I now know the final answer
Final Answer: <the user-facing answer>

Question: {input}
{agent_scratchpad}
""")

rag_agent = create_react_agent(llm, rag_tools, rag_prompt)

rag_executor = AgentExecutor.from_agent_and_tools(
    agent=rag_agent,
    tools=rag_tools,
    verbose=True,
    handle_parsing_errors=True,
)

# ======================================================
# 3. Web Search Agent (placeholder)
# ======================================================
def websearch_agent(query: str) -> str:
    return "Web search agent not implemented yet. (Planned Tavily/SerpAPI integration)."

# ======================================================
# Unified Orchestration
# ======================================================
def agent_response(query: str) -> dict:
    """Main entry point: classify → route → execute."""
    decision = run_classifier(query)
    route = decision.get("route", "OTHER")

    if route == "OTHER":
        return {"reply": decision.get("reply", "Hello!"), "category": "OTHER"}
    elif route == "RAG_AGENT":
        resp = rag_executor.invoke({"input": query})
        return {"reply": resp.get("output", "No answer generated."), "category": "RAG_AGENT"}
    elif route == "WEBSEARCH_AGENT":
        return {"reply": websearch_agent(query), "category": "WEBSEARCH_AGENT"}
    elif route == "IT_SUPPORT":
        return {"reply": "Routing to IT Support. Please provide more details.", "category": "IT_SUPPORT"}
    else:
        return {"reply": "Sorry, I couldn’t classify your question.", "category": "UNKNOWN"}
