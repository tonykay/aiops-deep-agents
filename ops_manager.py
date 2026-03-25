#!/usr/bin/env python3
import warnings

warnings.filterwarnings("ignore", message="Core Pydantic V1 functionality")

"""
AI Ops Manager - Deep Agents AI Operations Team

An ops manager agent configured entirely through files on disk:
- AGENTS.md defines the ops manager persona and triage protocol
- skills/ provides diagnostic workflows shared across subagents
- subagents.yaml defines SRE specialists (linux, kubernetes, networking)

Usage:
    uv run python ops_manager.py "Pod crashlooping in production namespace"
    uv run python ops_manager.py "High CPU on web-server-03"
    uv run python ops_manager.py "Intermittent DNS resolution failures"
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Literal

import yaml
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

PROJECT_DIR = Path(__file__).parent
console = Console()


# Web search tool available to subagents for looking up docs, CVEs, etc.
@tool
def web_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news"] = "general",
) -> dict:
    """Search the web for current information about infrastructure issues,
    documentation, CVEs, or best practices.

    Args:
        query: The search query (be specific and detailed)
        max_results: Number of results to return (default: 5)
        topic: "general" for docs/guides, "news" for recent incidents/CVEs

    Returns:
        Search results with titles, URLs, and content excerpts.
    """
    try:
        from tavily import TavilyClient

        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return {"error": "TAVILY_API_KEY not set"}

        client = TavilyClient(api_key=api_key)
        return client.search(query, max_results=max_results, topic=topic)
    except Exception as e:
        return {"error": f"Search failed: {e}"}


def load_subagents(config_path: Path) -> list:
    """Load subagent definitions from YAML and wire up tools.

    Externalizes subagent config to YAML following the content-builder-agent
    pattern. Each subagent gets a name, description, model, system_prompt,
    and resolved tool references.
    """
    available_tools = {
        "web_search": web_search,
    }

    with open(config_path) as f:
        config = yaml.safe_load(f)

    subagents = []
    for name, spec in config.items():
        subagent = {
            "name": name,
            "description": spec["description"],
            "system_prompt": spec["system_prompt"],
        }
        if "model" in spec:
            subagent["model"] = spec["model"]
        if "tools" in spec:
            subagent["tools"] = [available_tools[t] for t in spec["tools"]]
        if "skills" in spec:
            subagent["skills"] = spec["skills"]
        subagents.append(subagent)

    return subagents


def create_ops_manager():
    """Create the ops manager agent configured by filesystem files."""
    return create_deep_agent(
        memory=["./AGENTS.md"],
        tools=[],
        subagents=load_subagents(PROJECT_DIR / "subagents.yaml"),
        backend=FilesystemBackend(root_dir=PROJECT_DIR),
    )


class OpsDisplay:
    """Terminal display for ops manager progress."""

    def __init__(self):
        self.printed_count = 0
        self.spinner = Spinner("dots", text="Analyzing...")

    def update_status(self, status: str):
        self.spinner = Spinner("dots", text=status)

    def print_message(self, msg):
        if isinstance(msg, HumanMessage):
            console.print(
                Panel(str(msg.content), title="Incident", border_style="red")
            )

        elif isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, list):
                text_parts = [
                    p.get("text", "")
                    for p in content
                    if isinstance(p, dict) and p.get("type") == "text"
                ]
                content = "\n".join(text_parts)

            if content and content.strip():
                console.print(
                    Panel(Markdown(content), title="Ops Manager", border_style="green")
                )

            if msg.tool_calls:
                for tc in msg.tool_calls:
                    name = tc.get("name", "unknown")
                    args = tc.get("args", {})

                    if name == "task":
                        desc = args.get("description", "investigating...")
                        subagent = args.get("subagent_type", "unknown")
                        console.print(
                            f"  [bold magenta]>> Delegating to {subagent}:[/] "
                            f"{desc[:70]}..."
                        )
                        self.update_status(f"{subagent}: {desc[:40]}...")
                    elif name == "web_search":
                        query = args.get("query", "")
                        console.print(
                            f"  [bold blue]>> Searching:[/] {query[:50]}..."
                        )
                    elif name == "write_file":
                        path = args.get("file_path", "file")
                        console.print(f"  [bold yellow]>> Writing:[/] {path}")

        elif isinstance(msg, ToolMessage):
            name = getattr(msg, "name", "")
            if name == "task":
                console.print(f"  [green]>> Investigation complete[/]")
            elif name == "write_file":
                console.print(f"  [green]>> File written[/]")


async def main():
    if len(sys.argv) > 1:
        incident = " ".join(sys.argv[1:])
    else:
        incident = (
            "Pods in the 'api' namespace are CrashLoopBackOff. "
            "Started after last deployment. "
            "Users report 502 errors on the /v2/health endpoint."
        )

    console.print()
    console.print("[bold red]AI Ops Manager[/]")
    console.print(f"[dim]Incident: {incident}[/]")
    console.print()

    agent = create_ops_manager()
    display = OpsDisplay()

    with Live(
        display.spinner, console=console, refresh_per_second=10, transient=True
    ) as live:
        async for chunk in agent.astream(
            {"messages": [("user", incident)]},
            config={"configurable": {"thread_id": "ops-session"}},
            stream_mode="values",
        ):
            if "messages" in chunk:
                messages = chunk["messages"]
                if len(messages) > display.printed_count:
                    live.stop()
                    for msg in messages[display.printed_count :]:
                        display.print_message(msg)
                    display.printed_count = len(messages)
                    live.start()
                    live.update(display.spinner)

    console.print()
    console.print("[bold green]>> Investigation complete[/]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/]")
