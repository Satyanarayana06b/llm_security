# Corp AI Assistant

A **secure RAG-powered internal chatbot** for a fictional company that demonstrates **9 critical LLM security layers**. Built as a teaching tool — each security feature is isolated, testable, and accompanied by realistic attack scenarios.

---

## Table of Contents

- [Corp AI Assistant](#corp-ai-assistant)
  - [Table of Contents](#table-of-contents)
  - [Architecture Overview](#architecture-overview)
  - [The 9 Security Features](#the-9-security-features)
  - [Tech Stack](#tech-stack)
  - [Run the application](#run-the-application)

---

## Architecture Overview

```
┌──────────┐    ┌──────────────┐    ┌────────────────┐    ┌─────────────┐
│  Client   │───►│  FastAPI App  │───►│ Security Pipeline│───►│  OpenAI LLM  │
│ (HTTP/JS) │◄───│  (uvicorn)    │◄───│  (9 layers)     │◄───│  (GPT-4o)    │
└──────────┘    └──────────────┘    └────────────────┘    └─────────────┘
                       │                                          │
                ┌──────┴──────┐                           ┌───────┴───────┐
                │    Redis     │                           │   ChromaDB    │
                │ (Rate Limit, │                           │  (Vector DB   │
                │ Token Budget)│                           │  for RAG)     │
                └─────────────┘                           └───────────────┘
```

---

## The 9 Security Features

| # | Feature | File | What It Blocks |
|---|---------|------|----------------|
| 1 | **Input Validation** | `app/models/request.py` | Oversized payloads, regex-based injection patterns, empty/malformed input |
| 2 | **LLM Guard** | `app/security/input_guard.py` | Semantic prompt injection, toxicity, banned topics (via `llm-guard`) |
| 3 | **Hardened System Prompt** | `app/security/system_prompt.py` | Prompt leakage, instruction override, role-switching attacks |
| 4 | **Auth + Rate Limiting** | `app/middleware/auth.py`, `rate_limiter.py` | Unauthenticated access, brute-force, request flooding |
| 5 | **Input Restructuring** | `app/security/input_restructuring.py` | Token-bombing with 128k-token inputs; truncates or summarizes |
| 6 | **Token Budgets** | `app/security/token_budget.py` | Per-user daily token spend limits (cost control) |
| 7 | **Content Moderation** | `app/security/content_moderation.py` | Harmful input AND jailbroken output (both sides, not just input) |
| 8 | **RAG Spotlighting** | `app/rag/spotlighting.py` | Indirect prompt injection through retrieved documents |
| 9 | **Output Validation** | `app/security/output_validator.py` | Malformed/unstructured LLM responses (Pydantic schema + retry) |

---

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | >= 3.12 |
| Web Framework | FastAPI | >= 0.115 |
| ASGI Server | Uvicorn | >= 0.34 |
| Input/Output Validation | Pydantic v2 | >= 2.10 |
| Settings Management | pydantic-settings | >= 2.7 |
| LLM Security Scanners | llm-guard (by Protect AI) | >= 0.3.16 |
| LLM Provider | OpenAI API (GPT-4o-mini) | >= 1.60 |
| Caching / Rate Limiting | Redis | >= 5.2 |
| Vector Database (RAG) | ChromaDB | >= 0.5 |
| Token Counting | tiktoken | >= 0.9 |
| Authentication | PyJWT | >= 2.10 |
| Testing | pytest | >= 8.0 |
| Containerization | Docker + docker-compose | - |

## Run the application
docker build -t llm_security .
docker compose up -d redis && uv run python main.py
