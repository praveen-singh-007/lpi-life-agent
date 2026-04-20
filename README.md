# Deployment Strategy Agent (Level 3)

## Overview

This project implements a Level 3 decision-making agent using the Life Programmable Interface (LPI).

The agent generates **constraint-aware deployment strategies** for digital twin systems by combining multiple LPI tools and producing structured, consultant-style outputs.

Unlike basic agents, this system:
- makes decisions (not just explanations)
- respects real-world constraints
- uses multi-source reasoning (SMILE + insights + case studies + knowledge)

---

## Features

* Multi-tool usage:
  * `smile_overview`
  * `get_insights`
  * `get_case_studies`
  * `query_knowledge`
* JSON-RPC communication with LPI sandbox
* Constraint-aware reasoning (team, time, infrastructure)
* Relevance filtering (avoids cross-domain errors)
* Hallucination control (no invented tech/tools)
* Structured deployment strategy output:
  * Architecture
  * SMILE phases
  * Risks
  * What to avoid
  * First actions
  * Decision reasoning

---

## Tech Stack

* Python (agent logic)
* Node.js (LPI sandbox)
* Subprocess + JSON-RPC communication
* Ollama (local LLM - Qwen2.5)

---

# Setup

### 1. Clone LPI Developer Kit
```bash
git clone https://github.com/iamaryan07/lpi-developer-kit
git cd lpi-developer-kit
git install
git run build
```

### 2. Install Python dependencies 
```bash
pip install -r requirements.txt 
```

### 3. Run Ollama (Local LLM)
```bash
nollama pull qwen2.5:5b 
nollama serve 
```

## Run the Agent 
From the root directory:
```bash
python agent.py 
```

## Example Input 
**Use case:** real-time patient monitoring digital twin in ICU 
**Constraints:** 2 developers, 3 months, no cloud 

## Example Output (Simplified) 
**Recommended Architecture:**
Minimal viable twin using existing hospital systems...

**SMILE Phases:**
- Reality Emulation
- Concurrent Engineering 

**Key Risks:**
- Data compatibility 
- Limited dev capacity 

**What to Avoid:**
eOver-engineering early 
eComplex integrations 
fFirst Actions:
f1. Map current systems f2. Prototype minimal twin f3. Validate with stakeholders 

decision Reasoning:
based on SMILE + healthcare case insights...
how It Works:
takes user input (use case + constraints) calls multiple LPI tools: SMILE methodology insights case studies knowledge processes and filters relevant data builds structured prompt sends to LLM (Qwen2.5 via Ollama) generates deployment strategy.

## Project Structure
lpi-life-agent/ |
      
      ├── agent.py
      
      ├── agent.json
      
      ├── README.md
      
      ├── HOW_I_DID_IT.md
