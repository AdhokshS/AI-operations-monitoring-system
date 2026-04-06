import pandas as pd


class CorrelationEngine:
    def __init__(self, processed_data: dict):
        self.agent_failures = processed_data["agent_failures_ts"]
        self.api_errors = processed_data["api_errors_ts"]
        self.circuit_breaker = processed_data["circuit_breaker_ts"]
        self.alerts = processed_data["alerts_ts"]

    def merge_system_signals(self):
        """
        Merge all system-level signals on time_bucket
        """
        df = self.agent_failures.merge(
            self.api_errors, on="time_bucket", how="outer"
        )

        df = df.merge(
            self.circuit_breaker, on="time_bucket", how="outer"
        )

        df = df.merge(
            self.alerts, on="time_bucket", how="outer"
        )

        # Fill missing values
        df.fillna(
            {
                "failure_rate": 0,
                "error_rate_pct": 0,
                "is_circuit_open": False,
                "alert_count": 0,
            },
            inplace=True,
        )

        self.system_df = df.sort_values("time_bucket")

        return self.system_df

    def detect_api_impact_on_calls(self):
        """
        Check if API issues correlate with agent failures
        """
        df = self.system_df.copy()

        # Dynamic thresholds
        api_threshold = df["error_rate_pct"].mean() + 2 * df["error_rate_pct"].std()
        failure_threshold = df["failure_rate"].mean() + 2 * df["failure_rate"].std()

        df["high_api_error"] = df["error_rate_pct"] > api_threshold
        df["high_failure"] = df["failure_rate"] > failure_threshold

        # Correlation flag
        df["api_causing_failures"] = df["high_api_error"] & df["high_failure"]

        return df

    def detect_circuit_breaker_impact(self):
        """
        Identify when circuit breaker leads to failures
        """
        df = self.system_df.copy()

        df["cb_failure"] = df["is_circuit_open"] & (df["failure_rate"] > 0.2)

        return df

    def detect_alert_mismatch(self):
        """
        Identify mismatch between alerts and actual failures
        """
        df = self.system_df.copy()

        # Case 1: Alerts exist but no failure
        df["false_alert"] = (df["alert_count"] > 0) & (df["failure_rate"] == 0)

        # Case 2: Failures exist but no alerts
        df["missing_alert"] = (df["failure_rate"] > 0.3) & (df["alert_count"] == 0)

        return df

    def run_all(self):
        """
        Run full correlation analysis
        """
        self.merge_system_signals()

        return {
            "system_df": self.system_df,
            "api_impact": self.detect_api_impact_on_calls(),
            "circuit_impact": self.detect_circuit_breaker_impact(),
            "alert_mismatch": self.detect_alert_mismatch(),
        }