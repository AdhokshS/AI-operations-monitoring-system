import pandas as pd
import json
from pathlib import Path


class DataLoader:
    def __init__(self, data_path: str):
        """
        Initialize DataLoader with base data directory
        """
        self.data_path = Path(data_path)

    def load_ingestion_logs(self) -> pd.DataFrame:
        file_path = self.data_path / "ingestion_logs.csv"
        df = pd.read_csv(file_path)

        # Standardize timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df

    def load_agent_calls(self) -> pd.DataFrame:
        file_path = self.data_path / "agent_call_outcomes.csv"
        df = pd.read_csv(file_path)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df

    def load_api_metrics(self) -> pd.DataFrame:
        file_path = self.data_path / "api_health_metrics.csv"
        df = pd.read_csv(file_path)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df

    def load_system_alerts(self) -> pd.DataFrame:
        file_path = self.data_path / "system_alerts.json"

        with open(file_path, "r") as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df

    def load_all(self) -> dict:
        """
        Load all datasets and return as dictionary
        """
        return {
            "ingestion": self.load_ingestion_logs(),
            "agent_calls": self.load_agent_calls(),
            "api_metrics": self.load_api_metrics(),
            "alerts": self.load_system_alerts(),
        }


if __name__ == "__main__":
    # Test run
    loader = DataLoader(data_path="../data")
    data = loader.load_all()

    for name, df in data.items():
        print(f"\n{name.upper()} DATA")
        print(df.head())
        print(f"Shape: {df.shape}")