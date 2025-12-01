# Agent Architecture

This directory contains the agent implementations for The Argonauts Trip Planner.

## Structure

```
src/agents/
├── orchestrator_capstone.py    # Main coordinator (loads appropriate agents)
├── exploration_agent.py        # Exploration mode agent
│
├── lite_agents/                # Optimized for gemini-2.5-flash-lite
│   ├── __init__.py
│   ├── research_agent.py       # Simple prompts, concrete examples
│   ├── planning_agent.py       # BAD vs GOOD examples
│   └── review_agent.py         # 7/10 approval threshold
│
└── pro_agents/                 # Optimized for advanced models
    ├── __init__.py
    ├── research_agent.py       # Detailed prompts, abstract reasoning
    ├── planning_agent.py       # Sophisticated instructions
    └── review_agent.py         # 8/10 approval threshold
```

## How It Works

The **orchestrator** automatically detects your model and loads the appropriate agents:

- If `MODEL_NAME` contains "lite" → loads agents from `lite_agents/`
- Otherwise → loads agents from `pro_agents/`

This ensures optimal performance for every model!

## Agent Files

### Active Files (Used by System)

- `orchestrator_capstone.py` - Coordinates the multi-agent workflow
- `exploration_agent.py` - Provides preliminary exploration mode
- `lite_agents/*` - All agents optimized for lite model
- `pro_agents/*` - All agents optimized for pro models

### Legacy Files (Not Used)

Files prefixed with `_backup_*` are old versions kept for reference:
- `_backup_planning_agent_capstone.py`
- `_backup_research_agent_capstone.py`
- `_backup_review_agent_capstone.py`

These were replaced by the lite/pro branching system and can be deleted.

## Adding New Agents

To add a new agent tier:

1. Create new folder (e.g., `ultra_agents/`)
2. Implement agents with appropriate optimizations
3. Update `Config.get_model_tier()` to detect the new tier
4. Update `load_agents_for_model()` in orchestrator to load from new folder

See `MODEL_BRANCHING.md` for detailed instructions.

