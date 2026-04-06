import pandas as pd


class AnomalyDetector:
    def __init__(self, system_df: pd.DataFrame):
        self.df = system_df.copy()

    def detect_failure_spikes(self):
        """
        Detect abnormal spikes in failure rate using rolling statistics
        """
        df = self.df.copy()

        df["rolling_mean"] = df["failure_rate"].rolling(window=10, min_periods=1).mean()
        df["rolling_std"] = df["failure_rate"].rolling(window=10, min_periods=1).std()

        df["failure_spike"] = df["failure_rate"] > (
            df["rolling_mean"] + 2 * df["rolling_std"]
        )

        return df

    def detect_recurring_failures(self):
        """
        Detect recurring failure patterns using time-window clustering
        """
        df = self.df.copy()

        df["failure_flag"] = df["failure_rate"] > 0.3

        # Keep only failure rows
        failures = df[df["failure_flag"]].copy()

        # Sort by time
        failures = failures.sort_values("time_bucket")

        # Compute time difference between events
        failures["time_diff"] = failures["time_bucket"].diff().dt.total_seconds() / 60

        # New group when gap > 15 minutes
        failures["new_group"] = (failures["time_diff"] > 15) | (failures["time_diff"].isna())
        failures["group_id"] = failures["new_group"].cumsum()

        # Aggregate groups
        recurring = failures.groupby("group_id").agg(
            start_time=("time_bucket", "min"),
            end_time=("time_bucket", "max"),
            duration=("time_bucket", "count"),
            avg_failure_rate=("failure_rate", "mean")
        )

        # Mark significant recurring issues
        recurring["is_recurring"] = recurring["duration"] >= 3

        return recurring.reset_index()

    def detect_partial_resolution(self):
        """
        Detect recurring clusters that reappear after gaps (true partial resolution)
        """
        recurring_df = self.detect_recurring_failures()

        recurring_df = recurring_df[recurring_df["is_recurring"] == True].copy()

        recurring_df = recurring_df.sort_values("start_time")

        recurring_df["time_gap"] = recurring_df["start_time"].diff().dt.total_seconds() / 60

        # Reappearance if gap exists between clusters
        recurring_df["reappeared"] = recurring_df["time_gap"] > 30

        return recurring_df

    def run_all(self):
        return {
            "spikes": self.detect_failure_spikes(),
            "recurring": self.detect_recurring_failures(),
            "partial_resolution_count": self.detect_partial_resolution(),
        }