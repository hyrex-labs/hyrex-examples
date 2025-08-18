# Deep Research Demo with Hyrex

## Project Overview
This project demonstrates a deep research system using Hyrex for task orchestration. The system performs multi-stage research tasks with parallel processing and result aggregation.

## Architecture
- **Hyrex**: Task orchestration framework for managing complex research workflows
- **Task Types**: Research gathering, analysis, synthesis, and reporting
- **Parallelization**: Concurrent execution of independent research tasks

## Development Guidelines
- Use Hyrex decorators for task definitions
- Implement proper error handling and retries
- Log all significant operations for debugging
- Ensure tasks are idempotent where possible
- Update project-notes.md with each change to the codebase

## Dependencies
- Hyrex for task orchestration
- Additional libraries as needed for research operations