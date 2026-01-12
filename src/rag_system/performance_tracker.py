"""
Performance Tracker - Analyzes metrics and identifies improvement opportunities
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Tracks and analyzes agent performance metrics to identify
    areas for improvement and measure progress over time.
    """

    def __init__(self):
        self.session_metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.improvement_suggestions: List[Dict[str, Any]] = []

    def record_metric(
        self,
        session_id: str,
        metric_name: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Record a performance metric"""
        if session_id not in self.session_metrics:
            self.session_metrics[session_id] = []

        self.session_metrics[session_id].append(
            {
                "timestamp": datetime.now().isoformat(),
                "metric_name": metric_name,
                "metric_value": metric_value,
                "metadata": metadata or {},
            }
        )

    def analyze_response_times(
        self, conversations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze response time patterns.

        Returns insights about response time performance.
        """
        if not conversations:
            return {"status": "no_data"}

        response_times = [
            c["response_time_ms"]
            for c in conversations
            if c.get("response_time_ms") is not None
        ]

        if not response_times:
            return {"status": "no_data"}

        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)

        # Calculate percentiles
        sorted_times = sorted(response_times)
        p50 = sorted_times[len(sorted_times) // 2]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]

        analysis = {
            "status": "analyzed",
            "total_conversations": len(response_times),
            "avg_response_time_ms": round(avg_time, 2),
            "min_response_time_ms": round(min_time, 2),
            "max_response_time_ms": round(max_time, 2),
            "p50_response_time_ms": round(p50, 2),
            "p95_response_time_ms": round(p95, 2),
            "p99_response_time_ms": round(p99, 2),
        }

        # Generate suggestions
        if p95 > 5000:  # 5 seconds
            self.improvement_suggestions.append(
                {
                    "category": "response_time",
                    "severity": "high",
                    "suggestion": "95th percentile response time exceeds 5 seconds. Consider optimizing LLM parameters or using a faster model.",
                    "data": {"p95": p95},
                }
            )
        elif p95 > 3000:  # 3 seconds
            self.improvement_suggestions.append(
                {
                    "category": "response_time",
                    "severity": "medium",
                    "suggestion": "95th percentile response time exceeds 3 seconds. Monitor for user experience impact.",
                    "data": {"p95": p95},
                }
            )

        return analysis

    def analyze_error_patterns(
        self, conversations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze error patterns to identify common failure modes.
        """
        if not conversations:
            return {"status": "no_data"}

        total = len(conversations)
        errors = [c for c in conversations if not c.get("success", True)]
        error_rate = len(errors) / total if total > 0 else 0

        # Group errors by type
        error_types: Dict[str, int] = {}
        for error in errors:
            error_msg = error.get("error_message", "Unknown error")
            # Extract error type (first line or first 50 chars)
            error_type = error_msg.split("\n")[0][:50]
            error_types[error_type] = error_types.get(error_type, 0) + 1

        analysis = {
            "status": "analyzed",
            "total_conversations": total,
            "total_errors": len(errors),
            "error_rate": round(error_rate * 100, 2),
            "error_types": error_types,
        }

        # Generate suggestions
        if error_rate > 0.1:  # >10% error rate
            self.improvement_suggestions.append(
                {
                    "category": "error_rate",
                    "severity": "high",
                    "suggestion": f"Error rate is {error_rate*100:.1f}%. Investigate and fix common error patterns.",
                    "data": {"error_types": error_types},
                }
            )

        # Identify most common errors
        if error_types:
            most_common_error = max(error_types.items(), key=lambda x: x[1])
            if most_common_error[1] > 3:  # Error occurred more than 3 times
                self.improvement_suggestions.append(
                    {
                        "category": "recurring_error",
                        "severity": "medium",
                        "suggestion": f"Recurring error detected: '{most_common_error[0]}' occurred {most_common_error[1]} times.",
                        "data": {"error": most_common_error[0]},
                    }
                )

        return analysis

    def analyze_conversation_patterns(
        self, conversations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze conversation patterns to identify user behavior trends.
        """
        if not conversations:
            return {"status": "no_data"}

        # Analyze message lengths
        user_message_lengths = [
            len(c.get("user_message", ""))
            for c in conversations
            if c.get("user_message")
        ]
        agent_response_lengths = [
            len(c.get("agent_response", ""))
            for c in conversations
            if c.get("agent_response")
        ]

        analysis = {
            "status": "analyzed",
            "total_conversations": len(conversations),
        }

        if user_message_lengths:
            analysis["avg_user_message_length"] = round(
                sum(user_message_lengths) / len(user_message_lengths), 2
            )

        if agent_response_lengths:
            analysis["avg_agent_response_length"] = round(
                sum(agent_response_lengths) / len(agent_response_lengths), 2
            )

        # Check for very long responses (might indicate verbosity issues)
        if agent_response_lengths:
            long_responses = [l for l in agent_response_lengths if l > 500]
            if len(long_responses) / len(agent_response_lengths) > 0.3:
                self.improvement_suggestions.append(
                    {
                        "category": "response_length",
                        "severity": "low",
                        "suggestion": "More than 30% of responses are quite long (>500 chars). For voice interactions, consider making responses more concise.",
                        "data": {
                            "avg_length": sum(agent_response_lengths)
                            / len(agent_response_lengths)
                        },
                    }
                )

        return analysis

    def generate_improvement_report(
        self, conversations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive improvement report based on all analyses.
        """
        # Clear previous suggestions
        self.improvement_suggestions = []

        # Run all analyses
        response_time_analysis = self.analyze_response_times(conversations)
        error_analysis = self.analyze_error_patterns(conversations)
        conversation_analysis = self.analyze_conversation_patterns(conversations)

        report = {
            "timestamp": datetime.now().isoformat(),
            "analyses": {
                "response_times": response_time_analysis,
                "errors": error_analysis,
                "conversations": conversation_analysis,
            },
            "suggestions": self.improvement_suggestions,
            "summary": {
                "total_suggestions": len(self.improvement_suggestions),
                "high_priority": len(
                    [s for s in self.improvement_suggestions if s["severity"] == "high"]
                ),
                "medium_priority": len(
                    [
                        s
                        for s in self.improvement_suggestions
                        if s["severity"] == "medium"
                    ]
                ),
                "low_priority": len(
                    [s for s in self.improvement_suggestions if s["severity"] == "low"]
                ),
            },
        }

        logger.info(
            f"Generated improvement report: {report['summary']['total_suggestions']} suggestions"
        )

        return report

    def compare_time_periods(
        self,
        recent_conversations: List[Dict[str, Any]],
        historical_conversations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Compare recent performance against historical baseline to measure improvement.
        """
        recent_analysis = self.analyze_response_times(recent_conversations)
        historical_analysis = self.analyze_response_times(historical_conversations)

        if (
            recent_analysis.get("status") != "analyzed"
            or historical_analysis.get("status") != "analyzed"
        ):
            return {"status": "insufficient_data"}

        # Calculate improvements
        avg_improvement = (
            historical_analysis["avg_response_time_ms"]
            - recent_analysis["avg_response_time_ms"]
        ) / historical_analysis["avg_response_time_ms"]

        recent_errors = sum(1 for c in recent_conversations if not c.get("success", True))
        historical_errors = sum(
            1 for c in historical_conversations if not c.get("success", True)
        )

        recent_error_rate = (
            recent_errors / len(recent_conversations) if recent_conversations else 0
        )
        historical_error_rate = (
            historical_errors / len(historical_conversations)
            if historical_conversations
            else 0
        )

        comparison = {
            "status": "compared",
            "recent_period": {
                "conversations": len(recent_conversations),
                "avg_response_time": recent_analysis["avg_response_time_ms"],
                "error_rate": round(recent_error_rate * 100, 2),
            },
            "historical_period": {
                "conversations": len(historical_conversations),
                "avg_response_time": historical_analysis["avg_response_time_ms"],
                "error_rate": round(historical_error_rate * 100, 2),
            },
            "improvement": {
                "response_time_improvement_pct": round(avg_improvement * 100, 2),
                "error_rate_change_pct": round(
                    (recent_error_rate - historical_error_rate) * 100, 2
                ),
            },
        }

        return comparison

    def get_suggestions(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get improvement suggestions, optionally filtered by severity"""
        if severity:
            return [s for s in self.improvement_suggestions if s["severity"] == severity]
        return self.improvement_suggestions
