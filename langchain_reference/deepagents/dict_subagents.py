from __future__ import annotations

from typing import Any

from deepagents import create_deep_agent
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Overwrite
from src.config import get_chat_model
import sys


def pretty_stream_chunk(chunk: Any) -> None:
    # stream_mode="messages" can yield (message, metadata)
    if isinstance(chunk, tuple) and len(chunk) == 2 and isinstance(chunk[0], BaseMessage):
        msg, meta = chunk
        print(f"[message] meta={meta}")
        msg.pretty_print()
        if isinstance(msg, AIMessage):
            for tc in (msg.tool_calls or []):
                print(f"  tool_call name={tc.get('name')} id={tc.get('id')} args={tc.get('args')}")
        if isinstance(msg, ToolMessage):
            print(f"  tool_result id={msg.tool_call_id} name={getattr(msg, 'name', None)}")
        return

    # interrupt payloads
    if isinstance(chunk, dict) and "__interrupt__" in chunk:
        print("[interrupt]")
        for intr in chunk["__interrupt__"]:
            print("  value:", getattr(intr, "value", intr))
            print("  id:", getattr(intr, "id", None))
        return

    # stream_mode="updates": dict of node->update
    if isinstance(chunk, dict):
        for node_name, update in chunk.items():
            if isinstance(update, dict) and "messages" in update:
                print(f"[{node_name}]")
                messages = update["messages"]
                if isinstance(messages, Overwrite):
                    messages = messages.value
                if not isinstance(messages, list):
                    print(f"  messages={messages!r}")
                    continue
                for msg in messages:
                    if hasattr(msg, "pretty_print"):
                        msg.pretty_print()
                    else:
                        print(msg)

                    if isinstance(msg, AIMessage):
                        for tc in (msg.tool_calls or []):
                            print(f"  tool_call name={tc.get('name')} id={tc.get('id')} args={tc.get('args')}")
                    if isinstance(msg, ToolMessage):
                        print(f"  tool_result id={msg.tool_call_id} name={getattr(msg, 'name', None)}")
            else:
                print(f"[{node_name}] {update!r}")
        return

    print(repr(chunk))



def main():
    model = get_chat_model()
    ckpt = MemorySaver()

    # Dict-based subagent. Fields required: name, description, system_prompt, tools 
    profiler_subagent = {
        "name": "profile-agent",
        "description": "Does detailed EDA profiling and returns a concise executive summary + recommendations.",
        "system_prompt": (
            "You are an EDA profiling specialist.\n"
            "Given a dataset description, produce:\n"
            "1) A concise summary (<= 2 bullets)\n"
            "2) 2 recommended next analyses\n"
            "Do NOT include long intermediate notes.\n"
        ),
        "tools": [],  # keep minimal; required key 
    }

    agent = create_deep_agent(
        model=model,
        checkpointer=ckpt,
        subagents=[profiler_subagent], # type: ignore
        name="main-agent",
    )

    prompt = (
        "We have a multivariate time-series dataset sampled every minute with sensors S1..S4.\n"
        "Delegate to the profile-agent to propose the best EDA.\n"
        "Then, as the main agent, give me the final cleaned result. In not more than 2 sentences.\n"
        "IMPORTANT: Use task(name='profile-agent', task='...')."
    )

    # out = agent.invoke(
    #     {"messages": [{"role": "user", "content": prompt}]},
    #     config={"configurable": {"thread_id": "DA5"}},
    # )

    # print("\n=== FINAL ===\n")
    # print(out["messages"][-1].content)

    for chunk in agent.stream({"messages": [{"role": "user", "content": prompt}]},
        config={"configurable": {"thread_id": "DA5"}},):
        # chunks.append(chunk)
        # sys.stdout.write(chunk) #type:ignore
        # sys.stdout.flush()
        pretty_stream_chunk(chunk)


if __name__ == "__main__":
    main()
