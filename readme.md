# Multi-Agent TRPG App

A hardcore text-based RPG built with large language models, designed for deep immersion, logical consistency, and long-term memory. Through multi-agent collaboration and a deterministic computation engine, it addresses common LLM pain points in long-form text scenarios: forgetting, hallucination, and runaway numerical inflation.

## Core System Architecture

The system follows a layered architecture: **Brain (LLM) + Spinal Cord (LangGraph) + Memory (RAG/DB) + Skeleton (Combat Engine)**.

### Multi-Agent Collaboration

| Agent | Responsibilities |
| ----- | ---------------- |
| **Logic Prosecutor** | **Input validation**: Checks whether player intent is logically plausible.<br>**Output review**: Ensures the Director Agent's descriptions align with established history.<br>**State triggers**: Determines whether player actions trigger combat, quest completion, or plot twists. |
| **World State Manager** | **Data read/write**: Parses narrative and updates structured data.<br>**Attribute tracking**: Manages rank, hunger, ammunition, health, and NPC affinity. |
| **Director Agent** | **Immersive narration**: Receives state data and RAG materials to produce highly literary sensory descriptions.<br>**Pacing control**: Uses a plot-depth model to decide when to present decision points. |

### Layered Memory System

| Layer | Description |
| ----- | ----------- |
| **Short-term memory** | Retains the last 5–10 turns of dialogue verbatim to maintain conversational flow. |
| **Structured state** | JSON objects stored in SQLite representing the current "save point." |
| **Plot summaries** | Automatically generated every X turns by the State Manager to record major turning points. |
| **Knowledge base** | Stores historical facts, weapon specs, and tactical manuals for on-demand retrieval to enrich detail. |

## Core Mechanism Design

### Combat Engine

When the Logic Prosecutor determines "enter combat," the system switches from **free narrative mode** to **numerical resolution mode**:

- **Formula**: `Result = (Base Combat Power + Terrain Modifier + Weather Modifier + Tactical Bonus) × Random Dice`
- **Result feedback**: The computed result is sent back to the State Manager to update attributes, then translated into narrative by the Director Agent.

  > Example: Result is "crushing defeat" → Narration: _Your squad suffers heavy losses under machine-gun fire; the snow is stained red with blood._

### Logic Loop Handling

- **Anti-cheat**: If a player inputs "I teleport to Berlin," the Logic Prosecutor returns "illegal action," and the system displays a prompt.
- **Command set management**: Predefined templates for combat, march, rest, and dialogue—each with distinct prompt preferences.

## Tech Stack

| Category | Choice |
| -------- | ------ |
| Backend | [FastAPI](https://fastapi.tiangolo.com/) |
| Agent orchestration | [LangGraph](https://langchain-ai.github.io/langgraph/) |
| Language model | DeepSeek-V4 Flash |
| Relational database | SQLite |
| Vector database | ChromaDB |
| Frontend | React |
