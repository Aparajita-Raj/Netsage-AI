# Netsage-AI
NetSage AI is an evidence-first AI-assisted network troubleshooting platform for Cisco/Packet Tracer labs, combining deterministic rule-based checks, Gemini-powered diagnosis, confidence scoring, human verification, instructor approval, and analytics.

## Key Features

- Evidence-based network troubleshooting
- Deterministic Python rule engine for parsing and validating Cisco CLI output
- AI-assisted fault diagnosis using Gemini
- Ranked hypotheses with confidence and supporting evidence
- Suggested next diagnostic commands
- Mandatory human verification before accepting a diagnosis
- Instructor approval for higher-risk fixes
- Audit-friendly troubleshooting workflow
- Analytics for fault patterns and AI-human agreement
- 35-case troubleshooting dataset
- Responsible AI documentation and corrected-diagnosis examples
- Next.js/React frontend with FastAPI backend

## Workflow

Student 101
→ Create troubleshooting case
→ Submit Cisco evidence
→ Deterministic rule checks
→ Gemini diagnosis
→ Human verification
→ Propose fix

Instructor 900
→ Review fix
→ Approve / Reject

Student 101
→ Apply approved fix
→ Submit fresh evidence
→ Verify result

## Technology Stack

- Frontend: Next.js, React, TypeScript
- Backend: Python, FastAPI
- AI: Google Gemini
- Validation: Python rule engine
- Database: SQLAlchemy / PostgreSQL-compatible persistence
- Testing: Pytest
- Migration: Alembic
- Development: Visual Studio Code

## Project Purpose

The project addresses a common networking-learning problem: students may know individual Cisco commands but struggle to connect network symptoms with the actual root cause. NetSage AI combines deterministic network evidence with AI reasoning while keeping humans responsible for diagnosis confirmation and fix approval.

## Safety and Responsible AI

NetSage AI does not automatically apply Cisco configuration changes. Fixes are proposed for review, and higher-risk changes require instructor approval. The system keeps the AI reasoning separate from deterministic evidence extraction so that unsupported facts are not treated as verified network evidence.
