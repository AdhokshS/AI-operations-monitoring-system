import pandas as pd


class Preprocessor:
    def __init__(self, data: dict):
        self.ingestion = data["ingestion"]
        self.agent_calls = data["agent_calls"]
        self.api_metrics = data["api_metrics"]
        self.alerts = data["alerts"]

    def normalize_timestamps(self):
        """
        Round timestamps to nearest 5 minutes for alignment
        """
        for df in [self.ingestion, self.agent_calls, self.api_metrics, self.alerts]:
            if "timestamp" in df.columns:
                df["time_bucket"] = df["timestamp"].dt.floor("5min")

    def handle_missing_values(self):
        """
        Basic missing value handling
        """
        self.ingestion.fillna({"customer_id": "UNKNOWN"}, inplace=True)
        self.agent_calls.fillna({"customer_id": "UNKNOWN"}, inplace=True)
        self.alerts.fillna({"customer_id": "UNKNOWN"}, inplace=True)

    def create_status_flags(self):
        """
        Create flags for easier analysis
        """
        # Ingestion success flag
        self.ingestion["is_success"] = self.ingestion["status"] == "SUCCESS"

        # Agent failure flag
        self.agent_calls["is_failure"] = self.agent_calls["outcome"].isin(
            ["CALL_FAILED", "TOOL_ERROR", "TIMEOUT"]
        )

        # API circuit breaker flag
        self.api_metrics["is_circuit_open"] = (
            self.api_metrics["circuit_breaker_status"] == "OPEN"
        )

        # Alert critical flag
        self.alerts["is_critical"] = self.alerts["severity"] == "CRITICAL"

    def aggregate_metrics(self):
        """
        Create aggregated views for correlation
        """
        # Agent failures per time bucket
        self.agent_failures_ts = (
            self.agent_calls.groupby("time_bucket")["is_failure"]
            .mean()
            .reset_index(name="failure_rate")
        )

        # API error rate per time bucket
        self.api_errors_ts = (
            self.api_metrics.groupby("time_bucket")["error_rate_pct"]
            .mean()
            .reset_index()
        )

        # Circuit breaker events
        self.circuit_breaker_ts = (
            self.api_metrics.groupby("time_bucket")["is_circuit_open"]
            .max()
            .reset_index()
        )

        # Alerts count
        self.alerts_ts = (
            self.alerts.groupby("time_bucket")["alert_id"]
            .count()
            .reset_index(name="alert_count")
        )

    def process(self):
        """
        Run full preprocessing pipeline
        """
        self.normalize_timestamps()
        self.handle_missing_values()
        self.create_status_flags()
        self.aggregate_metrics()

        return {
            "ingestion": self.ingestion,
            "agent_calls": self.agent_calls,
            "api_metrics": self.api_metrics,
            "alerts": self.alerts,
            "agent_failures_ts": self.agent_failures_ts,
            "api_errors_ts": self.api_errors_ts,
            "circuit_breaker_ts": self.circuit_breaker_ts,
            "alerts_ts": self.alerts_ts,
        }