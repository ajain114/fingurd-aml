"""
Base agent class — implements the tool-use agentic loop.

Maps to Bedrock AgentCore concepts:
  - system_prompt   → Agent Instructions
  - tools           → Action Group definitions
  - _execute_tool() → Lambda function backing an Action Group
  - run()           → InvokeAgent API call
  - The while loop  → Bedrock's internal orchestration loop (hidden in managed service)
"""

import json
from typing import Callable, Optional
import anthropic


class BaseAgent:
    """
    Implements an agentic loop: LLM decides which tool to call,
    we execute the tool, feed the result back, and repeat until
    the LLM produces a final answer (stop_reason == 'end_turn').
    """

    def __init__(
        self,
        client: anthropic.Anthropic,
        model: str,
        name: str,
        system_prompt: str,
        tools: list,
        tool_registry: dict,
        on_tool_call: Optional[Callable] = None,
        on_tool_result: Optional[Callable] = None,
    ):
        self.client = client
        self.model = model
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.tool_registry = tool_registry  # name → callable
        self.on_tool_call = on_tool_call     # callback for UI streaming
        self.on_tool_result = on_tool_result

    def run(self, user_message: str, context: str = "") -> dict:
        """
        Execute the agentic loop for this agent.
        Returns: {"findings": str, "tool_calls": list, "raw_messages": list}
        """
        full_prompt = user_message
        if context:
            full_prompt = f"Context from prior agents:\n{context}\n\n---\n\n{user_message}"

        messages = [{"role": "user", "content": full_prompt}]
        tool_call_log = []
        max_iterations = 8  # guard against infinite loops

        for _ in range(max_iterations):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=self.system_prompt,
                tools=self.tools,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text
                return {
                    "agent": self.name,
                    "findings": final_text.strip(),
                    "tool_calls": tool_call_log,
                }

            # Process tool use blocks
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                tool_name = block.name
                tool_input = block.input

                if self.on_tool_call:
                    self.on_tool_call(tool_name, tool_input)

                # Execute the tool
                handler = self.tool_registry.get(tool_name)
                if handler:
                    try:
                        result = handler(**tool_input)
                    except Exception as e:
                        result = {"error": str(e)}
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                result_str = json.dumps(result, default=str)

                if self.on_tool_result:
                    self.on_tool_result(tool_name, result)

                tool_call_log.append({
                    "tool": tool_name,
                    "input": tool_input,
                    "output_summary": result_str[:200] + "..." if len(result_str) > 200 else result_str,
                })

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_str,
                })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        return {
            "agent": self.name,
            "findings": "Max iterations reached — partial findings may be incomplete.",
            "tool_calls": tool_call_log,
        }
