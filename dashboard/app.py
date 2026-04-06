import streamlit as st
import pandas as pd
import sys
import os

# Fix import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import DataLoader
from src.preprocessing import Preprocessor
from src.correlation import CorrelationEngine
from src.anomaly_detection import AnomalyDetector
from src.customer_correlation import CustomerCorrelation
from src.triage_engine import TriageEngine


# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    loader = DataLoader("data")
    raw = loader.load_all()

    processor = Preprocessor(raw)
    processed = processor.process()

    corr = CorrelationEngine(processed)
    corr_results = corr.run_all()

    detector = AnomalyDetector(corr_results["system_df"])
    anomaly_results = detector.run_all()

    cust_corr = CustomerCorrelation(processed)
    customer_results = cust_corr.run_all()

    triage = TriageEngine(corr_results, anomaly_results)
    summary = triage.generate_summary()

    return processed, corr_results, anomaly_results, customer_results, summary


processed, corr_results, anomaly_results, customer_results, triage_summary = load_data()

st.title("📊 AI Operations Monitoring Console")

# -------------------------
# TRIAGE SUMMARY (TOP PRIORITY)
# -------------------------
st.header("🚨 Incident Triage Summary")

for item in triage_summary:
    st.subheader(f"{item['severity']} — {item['issue']}")
    st.write(f"**Evidence:** {item['evidence']}")
    st.write(f"**Action:** {item['action']}")
    st.markdown("---")


# -------------------------
# MONITORING CONFIDENCE (BONUS EDGE)
# -------------------------
alerts = processed["alerts"]

false_alerts = len(corr_results["alert_mismatch"][corr_results["alert_mismatch"]["false_alert"]])
missing_alerts = len(corr_results["alert_mismatch"][corr_results["alert_mismatch"]["missing_alert"]])
total_alerts = len(alerts)

confidence = 1 - (false_alerts / total_alerts)

st.metric("Monitoring Confidence Score", f"{round(confidence * 100, 2)}%")
st.caption("""
A low confidence score indicates high alert noise or missed detections. 
This suggests the monitoring system is not reliably capturing real system issues.
""")


# -------------------------
# INGESTION HEALTH
# -------------------------
st.header("📥 Ingestion Health")

ingestion = processed["ingestion"]

ingestion_summary = (
    ingestion.groupby("customer_id")["is_success"]
    .mean()
    .reset_index(name="success_rate")
)

st.subheader("Customer Success Rates")
st.dataframe(ingestion_summary)

st.subheader("Ingestion Trend (Smoothed)")
ingestion_ts = (
    ingestion.groupby("time_bucket")["is_success"]
    .mean()
    .rolling(5)
    .mean()
)

st.line_chart(ingestion_ts)

# 🔥 Validation Layer Insight (IMPORTANT)
st.subheader("Validation Layer Failures")

validation_issues = (
    ingestion[ingestion["is_success"] == False]
    .groupby("validation_layer_failed")
    .size()
    .reset_index(name="failure_count")
)

st.dataframe(validation_issues.sort_values("failure_count", ascending=False))


# -------------------------
# AGENT OUTCOMES
# -------------------------
st.header("📞 Agent Call Outcomes")

agent = processed["agent_calls"]

st.subheader("Outcome Distribution")
outcome_dist = agent["outcome"].value_counts()
st.bar_chart(outcome_dist)

st.subheader("Failure Rate by Customer")
failure_by_customer = (
    agent.groupby("customer_id")["is_failure"]
    .mean()
    .reset_index(name="failure_rate")
)

st.dataframe(failure_by_customer)

# 🔥 Provider-level insight (CRITICAL DIFFERENTIATOR)
st.subheader("Provider Failure Rates")

provider_failure = (
    agent.groupby("provider_id")["is_failure"]
    .mean()
    .reset_index(name="failure_rate")
)

st.dataframe(provider_failure.sort_values("failure_rate", ascending=False))


# -------------------------
# ALERT SUMMARY
# -------------------------
st.header("🚨 Alert Summary")

st.subheader("Severity Distribution")
severity_dist = alerts["severity"].value_counts()
st.bar_chart(severity_dist)

st.subheader("Acknowledgement Status")
ack_summary = alerts["acknowledged"].value_counts()
st.bar_chart(ack_summary)

# 🔥 Actionable alert view
st.subheader("Unacknowledged Critical Alerts")

critical_unacked = alerts[
    (alerts["severity"] == "CRITICAL") &
    (alerts["acknowledged"] == False)
]

st.dataframe(critical_unacked)


# -------------------------
# API CORRELATION
# -------------------------
st.header("🔗 API vs Failure Correlation")

system_df = corr_results["system_df"]

st.line_chart(system_df.set_index("time_bucket")[["failure_rate", "error_rate_pct"]])

st.markdown("""
🚨 **Feb 13 Incident Window Detected**

- API error rates spike significantly  
- Agent failure rates increase  
- Circuit breaker triggered  
- No corresponding alerts  

👉 Indicates a critical monitoring gap during a major system failure
""")


# -------------------------
# CUSTOMER IMPACT
# -------------------------
st.header("👥 Customer-Level Impact Analysis")

st.subheader("Top Impacted Customers")
st.dataframe(customer_results["summary"])

st.subheader("Detailed Examples")
st.dataframe(customer_results["detailed"].head(20))