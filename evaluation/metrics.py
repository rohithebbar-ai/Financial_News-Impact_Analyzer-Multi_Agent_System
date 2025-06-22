# evaluation/metrics.py
from typing import List, Dict, Tuple
import numpy as np
from datetime import datetime
from models.data_models import (
    TestCaseResult, EvaluationResult, ConsensusAnalysis, 
    AgentAnalysis, SentimentSignal
)

class MetricsCalculator:
    """Calculate comprehensive evaluation metrics for the multi-agent system"""
    
    def __init__(self):
        self.results: List[TestCaseResult] = []
        
    def add_result(self, result: TestCaseResult):
        """Add a test case result for metric calculation"""
        self.results.append(result)
    
    def calculate_all_metrics(self) -> Dict[str, EvaluationResult]:
        """Calculate all evaluation metrics"""
        
        if not self.results:
            raise ValueError("No results to evaluate")
        
        metrics = {
            "consensus_alignment": self._calculate_consensus_alignment(),
            "decision_confidence": self._calculate_decision_confidence(),
            "processing_efficiency": self._calculate_processing_efficiency(),
            "disagreement_analysis": self._calculate_disagreement_patterns(),
            "sentiment_stability": self._calculate_sentiment_stability(),
            "risk_detection_rate": self._calculate_risk_detection(),
            "agent_specialization": self._calculate_agent_specialization()
        }
        
        return metrics
    
    def _calculate_consensus_alignment(self) -> EvaluationResult:
        """Measure how often agents reach consensus"""
        consensus_scores = [r.consensus_analysis.consensus_score for r in self.results]
        avg_consensus = np.mean(consensus_scores)
        std_consensus = np.std(consensus_scores)
        
        # Identify which articles had lowest consensus
        low_consensus_articles = [
            r.article_id for r in self.results 
            if r.consensus_analysis.consensus_score < 0.5
        ]
        
        interpretation = f"Average consensus: {avg_consensus:.2%} (std: {std_consensus:.2%})"
        if low_consensus_articles:
            interpretation += f". Low consensus on: {', '.join(low_consensus_articles)}"
        
        return EvaluationResult(
            metric_name="Consensus Alignment",
            value=avg_consensus,
            interpretation=interpretation,
            details={
                "mean": avg_consensus,
                "std": std_consensus,
                "min": min(consensus_scores),
                "max": max(consensus_scores),
                "low_consensus_articles": low_consensus_articles
            }
        )
    
    def _calculate_decision_confidence(self) -> EvaluationResult:
        """Measure confidence in recommendations"""
        confidences = [r.consensus_analysis.action_confidence for r in self.results]
        avg_confidence = np.mean(confidences)
        
        # Check if confidence correlates with consensus
        consensus_scores = [r.consensus_analysis.consensus_score for r in self.results]
        correlation = np.corrcoef(confidences, consensus_scores)[0, 1]
        
        interpretation = (
            f"Average decision confidence: {avg_confidence:.2%}. "
            f"Correlation with consensus: {correlation:.2f}"
        )
        
        return EvaluationResult(
            metric_name="Decision Confidence", 
            value=avg_confidence,
            interpretation=interpretation,
            details={
                "mean": avg_confidence,
                "correlation_with_consensus": correlation,
                "high_confidence_decisions": sum(1 for c in confidences if c > 0.7)
            }
        )
    
    def _calculate_processing_efficiency(self) -> EvaluationResult:
        """Measure processing speed"""
        processing_times = [r.processing_time_seconds for r in self.results]
        avg_time = np.mean(processing_times)
        
        interpretation = f"Average processing time: {avg_time:.2f}s"
        if avg_time > 5:
            interpretation += " (Consider optimization for production)"
        
        return EvaluationResult(
            metric_name="Processing Efficiency",
            value=avg_time,
            interpretation=interpretation,
            details={
                "mean": avg_time,
                "max": max(processing_times),
                "min": min(processing_times)
            }
        )
    
    def _calculate_disagreement_patterns(self) -> EvaluationResult:
        """Analyze patterns in agent disagreements"""
        total_conflicts = sum(
            len(r.consensus_analysis.conflicting_views) for r in self.results
        )
        avg_conflicts = total_conflicts / len(self.results)
        
        # Categorize conflict types
        conflict_types = {}
        for result in self.results:
            for conflict in result.consensus_analysis.conflicting_views:
                conflict_type = conflict.get("type", "unknown")
                conflict_types[conflict_type] = conflict_types.get(conflict_type, 0) + 1
        
        interpretation = f"Average {avg_conflicts:.1f} conflicts per analysis. "
        if conflict_types:
            main_conflict = max(conflict_types, key=conflict_types.get)
            interpretation += f"Most common: {main_conflict}"
        
        return EvaluationResult(
            metric_name="Disagreement Analysis",
            value=avg_conflicts,
            interpretation=interpretation,
            details={
                "total_conflicts": total_conflicts,
                "conflict_types": conflict_types,
                "articles_with_conflicts": sum(1 for r in self.results 
                                             if r.consensus_analysis.conflicting_views)
            }
        )
    
    def _calculate_sentiment_stability(self) -> EvaluationResult:
        """Measure consistency of sentiment analysis across similar contexts"""
        # Group by sentiment signal
        sentiment_groups = {}
        for result in self.results:
            sentiment = result.consensus_analysis.overall_sentiment
            if sentiment not in sentiment_groups:
                sentiment_groups[sentiment] = []
            sentiment_groups[sentiment].append(result.article_id)
        
        # Calculate how well sentiment aligns with expected outcomes
        # (In real implementation, you'd compare against historical data)
        stability_score = len(sentiment_groups) / len(SentimentSignal)
        
        interpretation = f"Sentiment distribution across {len(sentiment_groups)} categories"
        
        return EvaluationResult(
            metric_name="Sentiment Stability",
            value=stability_score,
            interpretation=interpretation,
            details={
                "sentiment_distribution": {
                    k.value: v for k, v in sentiment_groups.items()
                }
            }
        )
    
    def _calculate_risk_detection(self) -> EvaluationResult:
        """Measure system's ability to identify risks"""
        total_risks = sum(
            len(r.consensus_analysis.key_risks) for r in self.results
        )
        avg_risks_identified = total_risks / len(self.results)
        
        # Check if high volatility articles had more risks identified
        high_volatility_results = [
            r for r in self.results 
            if len(r.consensus_analysis.conflicting_views) >= 1
        ]
       
        if high_volatility_results:
            high_vol_avg_risks = sum(
                len(r.consensus_analysis.key_risks) for r in high_volatility_results
            ) / len(high_volatility_results)
        else:
            high_vol_avg_risks = 0
        
        interpretation = (
            f"Average {avg_risks_identified:.1f} risks identified per article. "
            f"High volatility articles: {high_vol_avg_risks:.1f} risks"
        )
        
        return EvaluationResult(
            metric_name="Risk Detection Rate",
            value=avg_risks_identified,
            interpretation=interpretation,
            details={
                "total_risks_identified": total_risks,
                "high_volatility_risk_avg": high_vol_avg_risks
            }
        )
    
    def _calculate_agent_specialization(self) -> EvaluationResult:
        """Measure how well agents maintain their specialized perspectives"""
        specialization_scores = []
        
        for result in self.results:
            # Check if each agent provided unique insights
            agent_insights = {}
            for agent_name, analysis in result.consensus_analysis.agent_analyses.items():
                # Count unique factors mentioned by this agent
                unique_factors = set(analysis.primary_factors)
                other_factors = set()
                for other_agent, other_analysis in result.consensus_analysis.agent_analyses.items():
                    if other_agent != agent_name:
                        other_factors.update(other_analysis.primary_factors)
                
                unique_to_agent = unique_factors - other_factors
                specialization = len(unique_to_agent) / max(len(unique_factors), 1)
                agent_insights[agent_name] = specialization
            
            avg_specialization = np.mean(list(agent_insights.values()))
            specialization_scores.append(avg_specialization)
        
        overall_specialization = np.mean(specialization_scores)
        
        interpretation = (
            f"Agents maintain {overall_specialization:.1%} unique perspectives. "
            f"Higher is better - shows true complementary analysis"
        )
        
        return EvaluationResult(
            metric_name="Agent Specialization",
            value=overall_specialization,
            interpretation=interpretation,
            details={
                "mean_specialization": overall_specialization,
                "per_article_scores": {
                    r.article_id: score 
                    for r, score in zip(self.results, specialization_scores)
                }
            }
        )
    
    def generate_summary_report(self) -> str:
        """Generate a human-readable summary of all metrics"""
        metrics = self.calculate_all_metrics()
        
        report_lines = [
            "=" * 60,
            "MULTI-AGENT SYSTEM EVALUATION REPORT",
            "=" * 60,
            f"Total test cases evaluated: {len(self.results)}",
            "",
            "KEY METRICS:",
            "-" * 40
        ]
        
        for metric_name, result in metrics.items():
            report_lines.extend([
                f"\n{result.metric_name}:",
                f"  Score: {result.value:.3f}",
                f"  {result.interpretation}",
            ])
        
        # Add recommendations
        report_lines.extend([
            "",
            "SYSTEM ASSESSMENT:",
            "-" * 40
        ])
        
        consensus_score = metrics["consensus_alignment"].value
        specialization_score = metrics["agent_specialization"].value
        
        if consensus_score < 0.5:
            report_lines.append("⚠️  Low consensus - agents frequently disagree")
        else:
            report_lines.append("✓ Good consensus - agents generally align")
        
        if specialization_score > 0.3:
            report_lines.append("✓ Strong specialization - agents provide unique perspectives")
        else:
            report_lines.append("⚠️  Low specialization - agents may be too similar")
        
        avg_conflicts = metrics["disagreement_analysis"].value
        if avg_conflicts > 2:
            report_lines.append("✓ Healthy disagreement - captures market uncertainty")
        else:
            report_lines.append("⚠️  Limited disagreement - may miss nuanced views")
        
        report_lines.extend(["", "=" * 60])
        
        return "\n".join(report_lines)