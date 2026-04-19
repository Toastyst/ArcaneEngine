# ArcaneEngine

A WoW addon and Python bridge for AI-powered gameplay assistance.

## Components

- **ArcaneEngine/**: WoW addon for sending requests via clipboard.
- **runtime_bridge/**: Python app that watches clipboard, queries Ollama AI, displays responses in overlay.

## Features
- Clipboard-based WoW addon to Python bridge.
- Ollama AI integration with tool calling (calculator).
- TSM data provider (groups, inventory, market data).
- RAG with ChromaDB for relevant data retrieval.
- Transparent overlay UI.
- Detailed logging for data flow.

## Setup

1. Install ArcaneEngine addon to WoW AddOns folder.
2. Install Python deps: `pip install pyperclip ollama`
3. Run `python runtime_bridge/main.py`
4. In WoW, `/arcane ping` to test.

## Requirements

- Python 3.8+
- Ollama running locally
- World of Warcraft