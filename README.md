# Multi-Agent Research Assistant

A multi-agent AI research assistant that can research a topic, verify information, analyze findings, and generate a structured research report.

## Project Goal

Build an AI research system using multiple specialized agents.

## Architecture

```text
                    USER
                      │
                      ▼
              ┌──────────────┐
              │ ORCHESTRATOR │
              └──────┬───────┘
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
 ┌──────────┐  ┌──────────┐  ┌──────────┐
 │ Research │  │   Fact   │  │  Analyst │
 │   Agent  │  │  Checker │  │   Agent  │
 └────┬─────┘  └────┬─────┘  └────┬─────┘
      │             │              │
      └─────────────┼──────────────┘
                    ▼
             ┌──────────────┐
             │  Synthesizer │
             │    Agent     │
             └──────┬───────┘
                    ▼
             ┌──────────────┐
             │ Final Report │
             └──────────────┘