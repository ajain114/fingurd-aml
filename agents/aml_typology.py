"""
AML Typology Agent — Specialist Agent #3 (RAG Agent)
Bedrock equivalent: Agent Collaborator backed by a Bedrock Knowledge Base
                    using RetrieveAndGenerate with Titan Embeddings
"""

from .base_agent import BaseAgent
from knowledge_base.loader import search_typologies

SYSTEM_PROMPT = """You are an AML Typology Specialist with 15 years of experience in financial crime
pattern recognition, FATF typology analysis, and FinCEN guidance interpretation.

Your role:
- Match the observed transaction and entity patterns to known AML typologies
- Search the knowledge base for the closest matching money laundering methods
- Provide regulatory citations and red flag alignment
- Assess the confidence level of each typology match

Process:
1. Review the transaction and entity findings provided
2. Formulate 2-3 targeted search queries based on the key risk indicators
3. Search the typology knowledge base for each query
4. Rank the matches by relevance
5. Explain which specific red flags from the typology align with the observed activity

Output format (always follow this):
AML TYPOLOGY ANALYSIS:
- Primary Typology Match: [typology name] (Confidence: HIGH/MEDIUM/LOW)
  - Matching Red Flags: [list specific matching indicators]
  - Regulatory Reference: [FinCEN/FATF citation]

- Secondary Typology Match: [typology name] (Confidence: HIGH/MEDIUM/LOW)
  - Matching Red Flags: [list specific matching indicators]

- Typology Alignment Score: [0-100]
- SAR Narrative Hook: [1-2 sentences describing the scheme in plain language for the SAR narrative]

Ground your analysis in the knowledge base results. Quote specific language from typology documents."""


TOOLS = [
    {
        "name": "search_typologies",
        "description": (
            "Semantic search over the AML typology knowledge base containing FATF reports, "
            "FinCEN advisories, and Egmont Group typology documents. "
            "Returns the most relevant typology chunks with relevance scores. "
            "Run multiple targeted searches to cover different aspects of the pattern."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Natural language search query describing the pattern to match. "
                        "Examples: 'wire transfers structured below CTR threshold', "
                        "'cross-border layering UAE Jordan', 'smurfing P2P deposits aggregation'"
                    ),
                },
                "n_results": {
                    "type": "integer",
                    "description": "Number of results to return (1-5, default 3)",
                    "default": 3,
                },
            },
            "required": ["query"],
        },
    },
]

TOOL_REGISTRY = {
    "search_typologies": search_typologies,
}


def build(client, model, on_tool_call=None, on_tool_result=None, provider="anthropic") -> BaseAgent:
    return BaseAgent(
        client=client,
        model=model,
        name="AML Typology Agent",
        system_prompt=SYSTEM_PROMPT,
        tools=TOOLS,
        tool_registry=TOOL_REGISTRY,
        provider=provider,
        on_tool_call=on_tool_call,
        on_tool_result=on_tool_result,
    )
