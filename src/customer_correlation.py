import pandas as pd


class CustomerCorrelation:
    def __init__(self, processed_data: dict):
        self.ingestion = processed_data["ingestion"]
        self.agent_calls = processed_data["agent_calls"]

    def prepare_data(self):
        """
        Filter relevant data
        """
        # Only failed ingestion
        self.ingestion_failures = self.ingestion[
            self.ingestion["is_success"] == False
        ].copy()

        # Only agent failures
        self.agent_failures = self.agent_calls[
            self.agent_calls["is_failure"] == True
        ].copy()

    def correlate_failures(self):
        """
        Link ingestion failures to agent failures within time window
        """
        results = []

        for _, row in self.ingestion_failures.iterrows():
            customer = row["customer_id"]
            time = row["time_bucket"]

            # Look for agent failures within +/- 10 minutes
            window_start = time - pd.Timedelta(minutes=10)
            window_end = time + pd.Timedelta(minutes=10)

            related_calls = self.agent_failures[
                (self.agent_failures["customer_id"] == customer)
                & (self.agent_failures["time_bucket"] >= window_start)
                & (self.agent_failures["time_bucket"] <= window_end)
            ]

            if not related_calls.empty:
                results.append({
                    "customer_id": customer,
                    "ingestion_time": time,
                    "related_failures": len(related_calls),
                    "failure_types": related_calls["outcome"].unique().tolist(),
                    "unique_failure_count": related_calls["outcome"].nunique()
                })

        return pd.DataFrame(results)

    def summarize_by_customer(self, correlation_df):
        if correlation_df.empty:
            return pd.DataFrame()

        summary = correlation_df.groupby("customer_id").agg(
            total_incidents=("related_failures", "count"),
            total_failures=("related_failures", "sum"),
            avg_failure_per_incident=("related_failures", "mean"),
            avg_failure_type_diversity=("unique_failure_count", "mean")
        ).reset_index()

        return summary.sort_values("total_failures", ascending=False)

    def run_all(self):
        self.prepare_data()
        corr_df = self.correlate_failures()
        summary = self.summarize_by_customer(corr_df)

        return {
            "detailed": corr_df,
            "summary": summary
        }