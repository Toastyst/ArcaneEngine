# Arcane Engine Master Outline
**Last updated:** April 2026  
**Status:** Bridge proven. Phase 1 scoped and ready for next development cycle.
**Git Repo:** https://github.com/Toastyst/ArcaneEngine

## North Star
A local Ollama-powered agent that acts as a real co-pilot inside World of Warcraft.  
It has deep read/write access to addon databases (TSM, Altoholic, Zygor later, quest log, etc.) and provides natural-language plans, auction house advice, and configuration changes.

## Why Phase 1 is TSM + Altoholic Only
- TSM + Altoholic represent the most complex and highest-value dataset.
- Directly solves the core pain point: data overload + difficulty sticking to a plan.
- Proves the full pipeline (Runtime Bridge + RAG + safe backend writes).
- Keeps scope tight. Every future module (Zygor, alts, quests, etc.) will slot in via the same Data Provider pattern with no core refactoring.

## Current Architecture
**Outbound (WoW → Runtime Bridge)**  
1. Player uses `/arcane` command or macro.  
2. Addon gathers selective context and copies a JSON payload with the `[[ARCANE_REQUEST]]` marker to the clipboard.  
3. Runtime Bridge detects the payload via clipboard watcher.  
4. Bridge processes the request (RAG + Ollama) and returns the result.

**Inbound (Runtime Bridge → Player)**  
- Primary: Transparent always-on-top Overlay UI (no reload required).  
- Fallback: Write to SavedVariables → player performs `/reload`.

**Backend Writes**  
The Runtime Bridge can directly edit `TradeSkillMaster.lua` on disk (groups, operations, sniper settings, etc.). Player reloads to apply changes. Import-string fallback remains available.

## Major Decisions Already Locked In
- Clipboard is the only reliable real-time pipe (all log-based methods failed due to buffering).
- Local-first with Ollama (default to fast models like gemma4:e2b).
- Aggressive summarization + RAG from day one to control token usage.
- Function calling / structured actions required — the model never hallucinates prices or performs raw math.
- 100% ToS safe (no memory reading, no automation).
- Cline/MCP tools are dev-only and not part of the final Runtime Bridge.

## Runtime Bridge Architecture (Python Side)
The Runtime Bridge is a clean, standalone Python application.

**Core Components**
1. Clipboard Watcher (100 ms poll)
2. Payload Parser
3. Modular Data Providers + RAG Layer
4. Prompt Builder (system + memory + RAG + tools)
5. Ollama Client (streaming + function calling)
6. Response Handler
7. Transparent Overlay UI (main user interface)

**Key Features**
- Persistent user memory (small JSON file)
- Robust RAG with smart chunking of TSM data (price velocity, ROI deltas, volume trends, region vs realm awareness)
- Tool calling support (calculator, TSM actions, etc.)
- Lightweight, always-on-top, click-through overlay
- Configurable model selection and paths
- Full modularity for future expansion (Zygor, alts, quests, etc.)

## Phase 1 Deliverables (Next Focus)
1. Real TSM context in payload (selective, efficient)
2. First Data Provider + RAG integration
3. Improved Prompt Builder with strong system instructions
4. Basic tool calling (calculator + structured actions)
5. Reliable responses via the Overlay UI
6. Safe TSM SavedVariables write-back capability

## Future Phases (No Refactor Needed)
- Phase 2: Zygor provider + plan coaching
- Phase 3: Alt orchestration + full completionist features
- Phase 4: Voice input, second-monitor web UI, optional SaaS fallback

This document is the single source of truth for the Arcane Engine project.