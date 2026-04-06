class TriageEngine:
    def __init__(self, corr_results, anomaly_results):
        self.system_df = corr_results["system_df"]
        self.api_impact = corr_results["api_impact"]
        self.alert_mismatch = corr_results["alert_mismatch"]
        self.recurring = anomaly_results["recurring"]
        self.partial = anomaly_results["partial_resolution_count"]

    def identify_p1_issues(self):
        """
        Critical system-wide failures
        """
        p1 = self.api_impact[self.api_impact["api_causing_failures"] == True]

        if not p1.empty:
            return {
                "issue": "API degradation causing agent failures",
                "severity": "P1",
                "evidence": f"{len(p1)} time windows affected",
                "action": "Immediate escalation to API / Platform team"
            }
        return None

    def identify_p2_issues(self):
        """
        Recurring instability
        """
        recurring_issues = self.recurring[self.recurring["is_recurring"] == True]

        if not recurring_issues.empty:
            return {
                "issue": "Recurring system instability detected",
                "severity": "P2",
                "evidence": f"{len(recurring_issues)} recurring clusters",
                "action": "Investigate root cause — likely incomplete fixes or systemic issues"
            }
        return None

    def identify_p3_issues(self):
        """
        Monitoring issues
        """
        false_alerts = self.alert_mismatch[self.alert_mismatch["false_alert"] == True]
        missing_alerts = self.alert_mismatch[self.alert_mismatch["missing_alert"] == True]

        return {
            "issue": "Monitoring system gaps",
            "severity": "P3",
            "evidence": f"{len(false_alerts)} false alerts, {len(missing_alerts)} missing alerts",
            "action": "Tune alert thresholds and improve observability coverage"
        }

    def generate_summary(self):
        """
        Final triage summary
        """
        summary = []

        p1 = self.identify_p1_issues()
        p2 = self.identify_p2_issues()
        p3 = self.identify_p3_issues()

        for item in [p1, p2, p3]:
            if item:
                summary.append(item)

        return summary