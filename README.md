# AI Operations Monitoring & Incident Analysis System

## Overview
This project simulates an operational monitoring system for an AI-driven healthcare platform.  
It focuses on identifying system failures, validating monitoring signals, and prioritizing incidents using cross-system analysis.

The emphasis is not on visualization alone, but on operational reasoning, anomaly detection, and actionable decision-making.

---

## Key Capabilities

### Cross-System Correlation
- Connects API performance, ingestion failures, and agent call outcomes
- Identifies cascading failures across system components

### Anomaly Detection
- Detects API degradation windows using time-series patterns
- Identifies silent failures (failures without alerts)
- Flags alert noise (alerts without real impact)
- Detects recurring failure clusters indicating incomplete resolution

### Customer-Level Impact Analysis
- Maps ingestion failures to downstream agent call failures
- Identifies high-risk customers impacted by upstream issues
- Analyzes failure diversity to detect systemic instability

### Monitoring System Evaluation
- Computes a Monitoring Confidence Score
- Highlights gaps in observability (false positives vs missed alerts)

### Incident Triage Engine
Automatically classifies issues into:
- **P1** — Critical system failures (e.g., API degradation)
- **P2** — Recurring instability patterns
- **P3** — Monitoring and alerting gaps

Each issue includes supporting evidence and recommended actions.

---

## Dashboard (Streamlit)

## Quick Start

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py

Dashboard Sections
Incident triage summary (prioritized view)
Ingestion health with validation layer insights
Agent outcomes and provider-level analysis
Alert summary with critical unacknowledged alerts
API vs failure correlation
Customer-level impact analysis
Approach

This solution is designed to answer core operational questions:

What is broken?
What is most urgent?
What action should be taken first?

To achieve this, the system:

Aligns all data sources into a unified time model
Applies statistical and rule-based anomaly detection
Validates monitoring signals against actual system behavior
Produces decision-oriented outputs instead of raw metrics
Key Insight

A major incident window was identified around Feb 13, where:

API error rates spiked significantly
Circuit breaker was triggered
Agent failure rates increased
No alerts were generated during the incident

This highlights a critical monitoring gap and delayed incident detection.

Tech Stack
Python (Pandas)
Streamlit
Time-series and anomaly detection logic
Conclusion

This project demonstrates how operational intelligence can be built from system logs by combining:

Cross-system correlation
Anomaly detection
Monitoring validation
Decision-focused outputs

The result is not just a dashboard, but a system that enables effective operational decision-making.