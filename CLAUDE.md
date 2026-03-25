# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@AGENTS.md

## Project Overview

AI Ops team built on [LangChain Deep Agents](https://github.com/langchain-ai/deepagents). An `ops_manager` orchestrator triages incidents and delegates to specialized SRE subagents (`sre_linux`, `sre_kubernetes`, `sre_networking`) which each use domain-specific skills.

## Commands

```bash
# Install dependencies
uv sync

# Run the ops manager
uv run python ops_manager.py "describe the incident here"

# Run tests
uv run pytest

# Lint
uv run ruff check .
uv run ruff format --check .
```

## Architecture

**Deep Agents pattern**: The framework uses filesystem-based configuration:
- `AGENTS.md` -- loaded as persistent memory (system prompt) for the ops_manager via `MemoryMiddleware`
- `skills/<domain>/` -- per-subagent skill directories loaded via `SkillsMiddleware`; each subagent declares its `skills:` paths in `subagents.yaml`
- `skills/common/` -- shared skills referenced by all subagents
- `subagents.yaml` -- defines SRE specialists; loaded by `load_subagents()` helper (not native to deepagents)
- `ops_manager.py` -- wires everything together via `create_deep_agent()`

**Agent delegation flow**:
1. ops_manager receives an incident description
2. Classifies the domain and delegates to the right subagent via the built-in `task` tool
3. Subagents use skills (SKILL.md workflows) and tools (web_search) to investigate
4. Subagents write findings to `investigations/<slug>/`
5. ops_manager synthesizes findings into a unified diagnosis

**Subagent configuration** (`subagents.yaml`): Each entry has `description`, `model`, `system_prompt`, `tools`, and `skills`. The `load_subagents()` function resolves tool name strings to actual `@tool` decorated functions and passes `skills` paths through to the `SubAgent` TypedDict.

**Skills are per-subagent and shareable**: Each subagent declares `skills:` as an array of path strings to skill source directories (e.g., `["./skills/linux/", "./skills/common/"]`). Each source directory contains skill subdirectories with `SKILL.md` files. Multiple subagents can reference the same source (e.g., all include `./skills/common/`).

**Built-in tools from deepagents**: `write_file`, `read_file`, `edit_file`, `ls`, `glob`, `grep`, `execute`, `task` (for subagent delegation), `write_todos`.

## Adding a New Subagent

1. Add an entry to `subagents.yaml` with description, model, system_prompt, tools, skills
2. Add any new tools as `@tool` decorated functions in `ops_manager.py`
3. Register tool names in the `available_tools` dict inside `load_subagents()`
4. Create a skill source directory `skills/<domain>/` with skill subdirectories containing `SKILL.md` files
5. Update `AGENTS.md` domain awareness section to include the new subagent

## Adding a New Skill

1. Create `skills/<domain>/<skill-name>/SKILL.md` with workflow steps and diagnostic commands
2. Skills are auto-discovered by `SkillsMiddleware` within the source directory -- no code registration needed
3. Add the source path to the subagent's `skills:` array in `subagents.yaml`
4. Skills shared across domains go in `skills/common/` (already referenced by all subagents)

## Future: Channel Adapter Pattern (post-0.0.1)

A `log_to_channel` subagent will take investigation findings (`error.md`) and reformat for output channels using channel-specific skills (`output-to-jira/SKILL.md`, `output-to-slack/SKILL.md`). Each skill defines the target format, required fields, and API interaction pattern.

## Key Conventions

- Python 3.13 -- always use `uv`, never `pip`
- Always use Pydantic V2 for structured outputs with OpenAI API
- Env var `TAVILY_API_KEY` required for web search tool
- Subagent models default to `anthropic:claude-sonnet-4-20250514`
- Investigation outputs go to `investigations/<incident-slug>/`
