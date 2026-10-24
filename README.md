# Deadlock Intelligent LLM Tutor

**Project Authors:** Ankit Ray (24BCI0233) & Dhruv Verma (24BCI0170)

## Overview
Deadlock Intelligent LLM Tutor is a domain-specialized, AI-powered pedagogical learning system designed for Operating Systems students. It addresses common student difficulties in understanding deadlock conditions, tracing the Banker's Algorithm, analyzing Resource Allocation Graphs (RAG), and comparing Prevention, Avoidance, Detection, and Recovery strategies.

## Key Features
1. **RAG-Grounded Concepts Tutor**: Course-grounded explanations with source citations and relevance scores covering the 4 Coffman conditions, Prevention, Avoidance, and Recovery.
2. **Banker's Algorithm Simulator & Verifier**:
   - Step-by-step trace of Dijkstra's Safety Algorithm.
   - Interactive verification of student-submitted safe sequences with exact error isolation.
   - Dynamic simulation of Resource-Request transactions ($Request \le Need$, $Request \le Available$, speculative safety rollback/commit).
3. **Resource Allocation Graph (RAG) Analyzer**:
   - Directed bipartite graph rendering of Processes and Resources using NetworkX & Matplotlib.
   - Automated cycle detection and single-instance vs. multi-instance deadlock theorem verification.
   - Multi-instance graph reduction algorithm with step-by-step process reduction order.
4. **Adaptive Practice Quiz & Viva**:
   - MCQs, Viva conceptual questions, and numerical problems.
   - Progressive 3-level hint delivery system.
   - Misconception diagnostics (e.g. confusing Prevention with Avoidance, equating Unsafe state to Deadlock).
5. **Student Profile & Mastery Analytics**:
   - SQLite-backed mastery tracking.
   - Adaptive Learning Planner recommending targeted re-learning activities based on weak areas.

## Quick Start
To launch the interactive Streamlit application:
```bash
streamlit run deadlock_tutor/app.py
```

## Running Unit Tests
```bash
python -m unittest deadlock_tutor.tests.test_deadlock_tutor
```
