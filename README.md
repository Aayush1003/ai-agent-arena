<div align="center">
  <h1>🎮 Agent Arena</h1>
  <p><b>Multi-Agent LLM Strategy Game with MCP, RAG, and Long-Term Memory</b></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![LangGraph Orchestration](https://img.shields.io/badge/Orchestrator-LangGraph-green)](https://python.langchain.com/v0.1/docs/langgraph/)
  [![MCP Ready](https://img.shields.io/badge/Tools-MCP_Enabled-purple)](https://modelcontextprotocol.io/)
  [![Vector DB](https://img.shields.io/badge/Memory-ChromaDB-blue)](#)
</div>

<br/>

## 📖 Overview

**Agent Arena** is an advanced AI simulation environment where multiple specialized autonomous agents collaborate, negotiate, and strategize to complete complex world-building missions. 

This project goes beyond simple chat interfaces to demonstrate a production-ready **Agentic Architecture**. It integrates Large Language Models (LLMs) with the **Model Context Protocol (MCP)** for external tool usage, **Retrieval-Augmented Generation (RAG)** for world knowledge, and **Vector Databases** for persistent agent memory.

### 🌟 Key Concepts Demonstrated
- **Multi-Agent Orchestration:** Specialized agents (Planner, Researcher, Coder, Critic) working in a LangGraph state machine.
- **MCP Tool Calling:** Standardized tool execution for interacting with the file system, web search, and simulated game APIs.
- **Persistent Memory:** Episodic and semantic memory using ChromaDB allowing agents to learn from past game loops.
- **Reflection & Self-Correction:** Built-in critique loops where agents evaluate their own performance before acting.
- **LLM Agnostic:** Seamlessly switch between OpenAI, Anthropic (Claude), and local Ollama models.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User([User / Game Master]) --> Orchestrator[LangGraph Orchestrator]
    Orchestrator --> State[Shared Game State]
    
    subgraph Multi-Agent System
        Planner[Planner Agent]
        Researcher[Researcher Agent]
        Executor[Executor Agent]
        Critic[Critic Agent]
    end
    
    Orchestrator --> Planner
    Orchestrator --> Researcher
    Orchestrator --> Executor
    Orchestrator --> Critic
    
    subgraph External Context & Tools
        Mem[(ChromaDB Memory)]
        RAG[RAG World Docs]
        MCP[MCP Tool Servers]
    end
    
    Multi-Agent System <--> Mem
    Multi-Agent System <--> RAG
    Multi-Agent System <--> MCP
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- OpenAI API Key (or alternative LLM provider)

### 2. Installation
Clone the repository and install the dependencies:

```bash
git clone https://github.com/yourusername/agent-arena.git
cd agent-arena
python -m venv venv
# On Windows use: venv\Scripts\activate OR source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file (copy from `.env.example`):

```bash
copy .env.example .env
```
Ensure you set:
`OPENAI_API_KEY=sk-your-key-here`

### 4. Run the Arena
Start the CLI simulation:

```bash
python main.py --mission "Build a self-sustaining tech startup in 30 turns"
```

---

## 📂 Project Structure

```text
agent-arena/
├── agents/             # Individual agent definitions & prompts
├── workflows/          # LangGraph state machine nodes and edges
├── memory/             # Vector store routing and episodic/semantic memory
├── rag/                # Document loaders and retrievers for environment rules
├── tools/              # MCP client implementations and custom python tools
├── data/               # Local persistence (ChromaDB, JSON states)
├── main.py             # Entry point
└── requirements.txt    # Project dependencies
```

---

## 🧪 Evaluation & Tracing

This project uses modern LLM observability. By default, prompt tracking and agent trajectories can be monitored using **LangSmith**.
To enable tracing, add your LangSmith API key to the `.env` file:
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
