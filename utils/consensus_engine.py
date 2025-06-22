# utils/consensus_engine.py
from typing import Dict, List, Tuple
import numpy as np
from models.data_models import (
    AgentAnalysis, ConsensusAnalysis, SentimentSignal, 
    MarketImpact, NewsArticle
)

class ConsensusEngine:
    """
    Synthesizes multiple agent analyses into consensus view.
    Handles disagreements intelligently based on context.
    """
    
    def __init__(self):
        self.weight_profiles = {
            "balanced": {"sentiment": 0.33, "fundamental": 0.34, "market_dynamics": 0.33},
            "earnings_focused": {"sentiment": 0.2, "fundamental": 0.6, "market_dynamics": 0.2},
            "momentum_driven": {"sentiment": 0.4, "fundamental": 0.2, "market_dynamics": 0.4},
            "uncertainty_high": {"sentiment": 0.3, "fundamental": 0.3, "market_dynamics": 0.4}
        }
    
    def synthesize(self, 
                   article: NewsArticle,
                   analyses: Dict[str, AgentAnalysis]) -> ConsensusAnalysis:
        """Create consensus from individual agent analyses"""
        
        # Calculate agreement metrics
        consensus_score = self._calculate_consensus_score(analyses)
        agreement_matrix = self._calculate_agreement_matrix(analyses)
        
        # Identify conflicts and their nature
        conflicts = self._identify_conflicts(analyses)
        
        # Determine appropriate weighting based on context
        weights = self._determine_weights(analyses, conflicts)
        
        # Calculate weighted consensus
        overall_sentiment = self._calculate_overall_sentiment(analyses, weights)
        overall_impact = self._calculate_overall_impact(analyses, weights)
        
        # Synthesize unified factors
        unified_factors = self._find_unified_factors(analyses)
        
        # Generate recommendation
        recommendation, confidence = self._generate_recommendation(
            analyses, overall_sentiment, conflicts
        )
        
        # Assess volatility
        volatility = self._assess_volatility(analyses, conflicts)
        
        # Compile risks and opportunities
        key_risks = self._compile_key_items(analyses, "risk_factors")
        key_opportunities = self._compile_key_items(analyses, "opportunities")
        
        # Generate summaries
        executive_summary = self._generate_executive_summary(
            overall_sentiment, overall_impact, recommendation, conflicts
        )
        detailed_rationale = self._generate_detailed_rationale(
            analyses, conflicts, weights
        )
        
        return ConsensusAnalysis(
            article_id=article.article_id,
            agent_analyses=analyses,
            overall_sentiment=overall_sentiment,
            overall_impact=overall_impact,
            consensus_score=consensus_score,
            unified_factors=unified_factors,
            conflicting_views=conflicts,
            market_recommendation=recommendation,
            action_confidence=confidence,
            volatility_expectation=volatility,
            key_risks=key_risks,
            key_opportunities=key_opportunities,
            executive_summary=executive_summary,
            detailed_rationale=detailed_rationale
        )
    
    def _calculate_consensus_score(self, analyses: Dict[str, AgentAnalysis]) -> float:
        """Calculate how aligned agents are (0=total disagreement, 1=perfect alignment)"""
        sentiments = [a.sentiment_score for a in analyses.values()]
        
        # Calculate variance in sentiment scores
        sentiment_variance = np.var(sentiments)
        sentiment_alignment = 1 - min(sentiment_variance, 1.0)
        
        # Check impact assessment alignment
        impacts = [a.impact_assessment.value for a in analyses.values()]
        impact_alignment = len(set(impacts)) / len(impacts)
        
        # Check time horizon alignment  
        horizons = [a.time_horizon for a in analyses.values()]
        horizon_alignment = len(set(horizons)) / len(horizons)
        
        # Weighted consensus
        consensus = (sentiment_alignment * 0.5 + 
                    (1 - impact_alignment) * 0.3 + 
                    (1 - horizon_alignment) * 0.2)
        
        return round(consensus, 3)
    
    def _calculate_agreement_matrix(self, analyses: Dict[str, AgentAnalysis]) -> Dict[str, Dict[str, float]]:
        """Calculate pairwise agreement between agents"""
        matrix = {}
        agent_names = list(analyses.keys())
        
        for i, agent1 in enumerate(agent_names):
            matrix[agent1] = {}
            for j, agent2 in enumerate(agent_names):
                if i == j:
                    matrix[agent1][agent2] = 1.0
                else:
                    # Calculate agreement based on sentiment distance
                    sent_diff = abs(analyses[agent1].sentiment_score - 
                                  analyses[agent2].sentiment_score)
                    agreement = 1 - (sent_diff / 2)  # Normalize to 0-1
                    matrix[agent1][agent2] = round(agreement, 3)
        
        return matrix
    
    def _identify_conflicts(self, analyses: Dict[str, AgentAnalysis]) -> List[Dict[str, str]]:
        """Identify and explain key disagreements between agents"""
        conflicts = []
        
        # Check sentiment conflicts
        sentiments = {name: a.sentiment_score for name, a in analyses.items()}
        if max(sentiments.values()) - min(sentiments.values()) > 1.0:
            conflict_agents = self._get_extreme_agents(sentiments)
            conflicts.append({
                "type": "sentiment_divergence",
                "description": f"{conflict_agents[0]} sees {sentiments[conflict_agents[0]]:.2f} sentiment while {conflict_agents[1]} sees {sentiments[conflict_agents[1]]:.2f}",
                "implication": "High uncertainty in market reaction"
            })
        
        # Check time horizon conflicts
        horizons = {name: a.time_horizon for name, a in analyses.items()}
        unique_horizons = set(horizons.values())
        if len(unique_horizons) > 2:
            conflicts.append({
                "type": "timing_disagreement", 
                "description": f"Agents disagree on impact timing: {', '.join([f'{k}={v}' for k,v in horizons.items()])}",
                "implication": "Mixed signals on when impact will materialize"
            })
        
        # Check impact magnitude conflicts
        impacts = {name: a.impact_assessment for name, a in analyses.items()}
        if self._has_impact_conflict(impacts):
            conflicts.append({
                "type": "impact_magnitude_conflict",
                "description": "Agents disagree on impact severity",
                "implication": "Uncertainty in reaction magnitude"
            })
        
        return conflicts
    
    def _determine_weights(self, 
                          analyses: Dict[str, AgentAnalysis], 
                          conflicts: List[Dict]) -> Dict[str, float]:
        """Determine agent weights based on context and conflicts"""
        
        # Start with balanced weights
        profile = "balanced"
        
        # Adjust based on article characteristics
        fundamental_analysis = analyses.get("FundamentalAnalystAgent")
        if fundamental_analysis:
            # If strong quantitative metrics mentioned, weight fundamental higher
            if any(word in str(fundamental_analysis.primary_factors).lower() 
                   for word in ["earnings", "revenue", "margin", "cash flow"]):
                profile = "earnings_focused"
        
        # If high conflict, increase market dynamics weight for context
        if len(conflicts) > 2:
            profile = "uncertainty_high"
            
        # If sentiment and fundamentals strongly disagree, look to market dynamics
        sentiment = analyses.get("SentimentAnalystAgent")
        if sentiment and fundamental_analysis:
            if abs(sentiment.sentiment_score - fundamental_analysis.sentiment_score) > 1.0:
                profile = "uncertainty_high"
        
        weights = self.weight_profiles[profile].copy()
        
        # Normalize to actual agent names
        return {
            "SentimentAnalystAgent": weights["sentiment"],
            "FundamentalAnalystAgent": weights["fundamental"],
            "MarketDynamicsAgent": weights["market_dynamics"]
        }
    
    def _calculate_overall_sentiment(self, 
                                   analyses: Dict[str, AgentAnalysis],
                                   weights: Dict[str, float]) -> SentimentSignal:
        """Calculate weighted overall sentiment"""
        weighted_sentiment = sum(
            analyses[agent].sentiment_score * weight 
            for agent, weight in weights.items()
        )
        
        # Map to sentiment signal
        if weighted_sentiment >= 0.6:
            return SentimentSignal.STRONG_BULLISH
        elif weighted_sentiment >= 0.2:
            return SentimentSignal.BULLISH
        elif weighted_sentiment >= -0.2:
            return SentimentSignal.NEUTRAL
        elif weighted_sentiment >= -0.6:
            return SentimentSignal.BEARISH
        else:
            return SentimentSignal.STRONG_BEARISH
    
    def _calculate_overall_impact(self,
                                analyses: Dict[str, AgentAnalysis],
                                weights: Dict[str, float]) -> MarketImpact:
        """Calculate weighted overall impact"""
        # Map impact to numeric scale
        impact_values = {
            MarketImpact.VERY_HIGH: 5,
            MarketImpact.HIGH: 4,
            MarketImpact.MODERATE: 3,
            MarketImpact.LOW: 2,
            MarketImpact.NEGLIGIBLE: 1
        }
        
        weighted_impact = sum(
            impact_values[analyses[agent].impact_assessment] * weight
            for agent, weight in weights.items()
        )
        
        # Map back to impact level
        if weighted_impact >= 4.5:
            return MarketImpact.VERY_HIGH
        elif weighted_impact >= 3.5:
            return MarketImpact.HIGH
        elif weighted_impact >= 2.5:
            return MarketImpact.MODERATE
        elif weighted_impact >= 1.5:
            return MarketImpact.LOW
        else:
            return MarketImpact.NEGLIGIBLE
    
    def _find_unified_factors(self, analyses: Dict[str, AgentAnalysis]) -> List[str]:
        """Find factors that multiple agents agree on"""
        all_factors = {}
        
        for agent_name, analysis in analyses.items():
            for factor in analysis.primary_factors:
                factor_lower = factor.lower()
                if factor_lower not in all_factors:
                    all_factors[factor_lower] = []
                all_factors[factor_lower].append(agent_name)
        
        # Return factors mentioned by at least 2 agents
        unified = [
            factor for factor, agents in all_factors.items() 
            if len(agents) >= 2
        ]
        
        return unified[:5]  # Top 5 unified factors
    
    def _generate_recommendation(self,
                               analyses: Dict[str, AgentAnalysis],
                               overall_sentiment: SentimentSignal,
                               conflicts: List[Dict]) -> Tuple[str, float]:
        """Generate trading recommendation with confidence"""
        
        # High conflict = high volatility caution
        if len(conflicts) >= 3:
            return "high_volatility_caution", 0.4
        
        # Map sentiment to recommendation
        sentiment_to_action = {
            SentimentSignal.STRONG_BULLISH: "strong_buy",
            SentimentSignal.BULLISH: "buy",
            SentimentSignal.NEUTRAL: "hold",
            SentimentSignal.BEARISH: "sell",
            SentimentSignal.STRONG_BEARISH: "strong_sell"
        }
        
        base_recommendation = sentiment_to_action[overall_sentiment]
        
        # Calculate confidence based on agent agreement
        sentiments = [a.sentiment_score for a in analyses.values()]
        confidences = [a.confidence_level for a in analyses.values()]
        
        sentiment_variance = np.var(sentiments)
        avg_confidence = np.mean(confidences)
        
        # High variance = lower confidence
        confidence = avg_confidence * (1 - min(sentiment_variance, 0.5))
        
        # If fundamental strongly disagrees with sentiment, reduce confidence
        fundamental = analyses.get("FundamentalAnalystAgent")
        sentiment_agent = analyses.get("SentimentAnalystAgent")
        
        if fundamental and sentiment_agent:
            if abs(fundamental.sentiment_score - sentiment_agent.sentiment_score) > 1.0:
                confidence *= 0.7
                
        return base_recommendation, round(confidence, 3)
    
    def _assess_volatility(self,
                         analyses: Dict[str, AgentAnalysis],
                         conflicts: List[Dict]) -> str:
        """Assess expected volatility"""
        
        # Conflict count indicates volatility
        if len(conflicts) >= 3:
            return "very_high"
        
        # Check if any agent mentions volatility risks
        all_risks = []
        for analysis in analyses.values():
            all_risks.extend(analysis.risk_factors)
        
        volatility_keywords = ["volatil", "uncertain", "swing", "fluctuat"]
        volatility_mentions = sum(
            1 for risk in all_risks 
            if any(keyword in risk.lower() for keyword in volatility_keywords)
        )
        
        if volatility_mentions >= 3:
            return "high"
        elif len(conflicts) >= 2 or volatility_mentions >= 1:
            return "moderate"
        else:
            return "low"
    
    def _compile_key_items(self, 
                          analyses: Dict[str, AgentAnalysis],
                          field: str) -> List[str]:
        """Compile and deduplicate items from all agents"""
        all_items = []
        for analysis in analyses.values():
            items = getattr(analysis, field, [])
            all_items.extend(items)
        
        # Deduplicate while preserving order
        seen = set()
        unique_items = []
        for item in all_items:
            item_lower = item.lower()
            if item_lower not in seen:
                seen.add(item_lower)
                unique_items.append(item)
        
        return unique_items[:5]  # Top 5
    
    def _generate_executive_summary(self,
                                  sentiment: SentimentSignal,
                                  impact: MarketImpact,
                                  recommendation: str,
                                  conflicts: List[Dict]) -> str:
        """Generate concise executive summary"""
        
        conflict_note = f" However, {len(conflicts)} areas of disagreement suggest caution." if conflicts else ""
        
        summary = (
            f"Overall {sentiment.value} sentiment with {impact.value} expected impact. "
            f"Recommendation: {recommendation.replace('_', ' ').title()}.{conflict_note}"
        )
        
        if conflicts:
            main_conflict = conflicts[0]["type"].replace("_", " ")
            summary += f" Primary concern: {main_conflict}."
            
        return summary
    
    def _generate_detailed_rationale(self,
                                   analyses: Dict[str, AgentAnalysis],
                                   conflicts: List[Dict],
                                   weights: Dict[str, float]) -> str:
        """Generate detailed explanation of consensus logic"""
        
        rationale_parts = []
        
        # Explain each agent's view
        for agent_name, analysis in analyses.items():
            weight = weights.get(agent_name, 0.33)
            rationale_parts.append(
                f"{agent_name} (weight: {weight:.1%}): "
                f"Sees {analysis.sentiment_score:+.2f} sentiment based on "
                f"{analysis.primary_factors[0].lower() if analysis.primary_factors else 'multiple factors'}."
            )
        
        # Explain conflicts
        if conflicts:
            rationale_parts.append(
                f"\nKey disagreements: {', '.join(c['type'].replace('_', ' ') for c in conflicts)}. "
                "This suggests market uncertainty and potential volatility."
            )
        else:
            rationale_parts.append(
                "\nAgents show strong alignment, suggesting clear market direction."
            )
        
        # Explain weighting decision
        rationale_parts.append(
            f"\nWeighting approach: {self._get_weight_rationale(weights)}"
        )
        
        return " ".join(rationale_parts)
    
    def _get_weight_rationale(self, weights: Dict[str, float]) -> str:
        """Explain why certain weights were chosen"""
        if weights.get("FundamentalAnalystAgent", 0) > 0.5:
            return "Fundamental-heavy due to strong quantitative metrics in news."
        elif weights.get("MarketDynamicsAgent", 0) > 0.35:
            return "Market dynamics emphasized due to high uncertainty/conflicts."
        else:
            return "Balanced weighting as all perspectives are relevant."
    
    def _get_extreme_agents(self, sentiments: Dict[str, float]) -> Tuple[str, str]:
        """Get agents with most extreme sentiment differences"""
        sorted_agents = sorted(sentiments.items(), key=lambda x: x[1])
        return sorted_agents[0][0], sorted_agents[-1][0]
    
    def _has_impact_conflict(self, impacts: Dict[str, MarketImpact]) -> bool:
        """Check if impact assessments significantly conflict"""
        impact_values = {
            MarketImpact.VERY_HIGH: 5,
            MarketImpact.HIGH: 4,
            MarketImpact.MODERATE: 3,
            MarketImpact.LOW: 2,
            MarketImpact.NEGLIGIBLE: 1
        }
        
        values = [impact_values[impact] for impact in impacts.values()]
        return max(values) - min(values) >= 2