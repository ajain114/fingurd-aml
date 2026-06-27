"""
Base agent class — implements the tool-use agentic loop.

Supports two providers:
  "anthropic" → Anthropic SDK (same model as Amazon Bedrock)
  "groq"      → Groq SDK (OpenAI-compatible, free tier)

Bedrock in production uses the Anthropic path — just swap the client init.
"""

import json
from typing import Callable, Optional


def _to_openai_tools(anthropic_tools: list) -> list:
    """Convert Anthropic tool schema → OpenAI/Groq format."""
    result = []
    for t in anthropic_tools:
        schema = dict(t["input_schema"])
        # Remove any keys Groq doesn't accept
        schema.pop("additionalProperties", None)
        result.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": schema,
            },
        })
    return result


class BaseAgent:
    def __init__(
        self,
        client,
        model: str,
        name: str,
        system_prompt: str,
        tools: list,
        tool_registry: dict,
        provider: str = "anthropic",
        on_tool_call: Optional[Callable] = None,
        on_tool_result: Optional[Callable] = None,
    ):
        self.client = client
        self.model = model
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.tool_registry = tool_registry
        self.provider = provider
        self.on_tool_call = on_tool_call
        self.on_tool_result = on_tool_result

    def run(self, user_message: str, context: str = "") -> dict:
        if self.provider == "groq":
            return self._run_groq(user_message, context)
        return self._run_anthropic(user_message, context)

    # ── Anthropic path ────────────────────────────────────────────────────────

    def _run_anthropic(self, user_message: str, context: str) -> dict:
        full_prompt = f"Context from prior agents:\n{context}\n\n---\n\n{user_message}" if context else user_message
        messages = [{"role": "user", "content": full_prompt}]
        tool_call_log = []

        for _ in range(8):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=self.system_prompt,
                tools=self.tools if self.tools else [],
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                final_text = "".join(b.text for b in response.content if hasattr(b, "text"))
                return {"agent": self.name, "findings": final_text.strip(), "tool_calls": tool_call_log}

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                tool_name, tool_input = block.name, block.input
                if self.on_tool_call:
                    self.on_tool_call(tool_name, tool_input)
                handler = self.tool_registry.get(tool_name)
                result = handler(**tool_input) if handler else {"error": f"Unknown tool: {tool_name}"}
                if self.on_tool_result:
                    self.on_tool_result(tool_name, result)
                tool_call_log.append({"tool": tool_name, "input": tool_input})
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result, default=str)})

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        return {"agent": self.name, "findings": "Max iterations reached.", "tool_calls": tool_call_log}

    # ── Groq path (OpenAI-compatible) ─────────────────────────────────────────

    def _run_groq(self, user_message: str, context: str) -> dict:
        system = self.system_prompt
        if context:
            system += f"\n\nContext from prior agents:\n{context}"

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ]
        openai_tools = _to_openai_tools(self.tools) if self.tools else None
        tool_call_log = []

        for _ in range(8):
            kwargs = {"model": self.model, "messages": messages, "max_tokens": 2048}
            if openai_tools:
                kwargs["tools"] = openai_tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            msg = choice.message

            # No tool calls — final answer
            if not msg.tool_calls:
                return {"agent": self.name, "findings": msg.content or "", "tool_calls": tool_call_log}

            # Add assistant message (with tool_calls) to history
            messages.append(msg)

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_input = json.loads(tc.function.arguments)
                except Exception:
                    tool_input = {}

                if self.on_tool_call:
                    self.on_tool_call(tool_name, tool_input)

                handler = self.tool_registry.get(tool_name)
                result = handler(**tool_input) if handler else {"error": f"Unknown tool: {tool_name}"}

                if self.on_tool_result:
                    self.on_tool_result(tool_name, result)

                tool_call_log.append({"tool": tool_name, "input": tool_input})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, default=str),
                })

        return {"agent": self.name, "findings": "Max iterations reached.", "tool_calls": tool_call_log}
