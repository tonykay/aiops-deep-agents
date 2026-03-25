# AI Ops Deep Agents

An AI-powered operations team built on [LangChain Deep Agents](https://github.com/langchain-ai/deepagents). An `ops_manager` orchestrator triages incidents and delegates to specialized SRE subagents, each equipped with domain-specific diagnostic skills.

## Architecture

```
ops_manager (Deep Agent)
├── sre_linux        - Host/OS diagnostics, systemd, performance
├── sre_kubernetes   - Cluster ops, workloads, RBAC, Helm
└── sre_networking   - L2/L3, DNS, routing protocols, firewalls
```

**How it works:**

1. `ops_manager` receives an incident description
2. Classifies the domain and delegates to the right subagent via the `task` tool
3. Subagents apply skill workflows (SKILL.md) and use tools to investigate
4. Findings are written to `investigations/<incident-slug>/`
5. `ops_manager` synthesizes a unified diagnosis with remediation steps

**Deep Agents pattern** -- everything is configured through files on disk:

| File | Purpose |
|------|---------|
| `AGENTS.md` | Ops manager persona and triage protocol (loaded as memory) |
| `subagents.yaml` | SRE specialist definitions with model, prompt, tools, and skills |
| `skills/<domain>/*/SKILL.md` | Per-subagent diagnostic workflows, declared via `skills:` paths in subagents.yaml |
| `skills/common/*/SKILL.md` | Shared skills referenced by all subagents |
| `ops_manager.py` | Wires it all together via `create_deep_agent()` |

## Skills

Each subagent declares its `skills:` as an array of source directory paths in `subagents.yaml`. Multiple subagents can reference the same source (e.g., `./skills/common/`).

```
skills/
├── linux/          # sre_linux skills
│   └── diagnostics/SKILL.md
├── kubernetes/     # sre_kubernetes skills
│   └── troubleshooting/SKILL.md
├── networking/     # sre_networking skills
│   ├── layer2/SKILL.md
│   ├── layer3/SKILL.md
│   └── dns/SKILL.md
└── common/         # Shared by all subagents
    └── log-analysis/SKILL.md
```

## Quick Start

```bash
# Requires Python 3.13+ and uv
uv sync

# Set up API keys
export TAVILY_API_KEY=your-key-here

# Run with an incident description
uv run python ops_manager.py "Pods in api namespace CrashLoopBackOff after deployment"
uv run python ops_manager.py "High CPU on web-server-03, load average 48"
uv run python ops_manager.py "Intermittent DNS failures resolving internal services"
```

## Extending

**Add a subagent** -- e.g., `sre_database`, `sre_cloud`:

1. Add entry to `subagents.yaml` (with `skills:` paths)
2. Create `skills/<domain>/` with skill subdirectories containing `SKILL.md`
3. Register any new tools in `ops_manager.py`
4. Update domain awareness in `AGENTS.md`

**Add a skill** -- create `skills/<domain>/<skill-name>/SKILL.md` and reference the source directory in the subagent's `skills:` array. For shared skills, add to `skills/common/`.

## Future: Channel Adapters (post-0.0.1)

A `log_to_channel` subagent will reformat investigation findings for output channels (Jira, Slack) using channel-specific skills.

## License

MIT
