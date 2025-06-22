#models/data_models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Any
from datetime import datetime
from enum import Enum

class NewsArticle(BaseModel):
    """Input model for financial news article"""
    article_id: str
    headline: str
    content: str
    published_at: str
    
class SentimentSignal(str, Enum):
    """Sentiment categories with market-standard terminology"""
    STRONG_BULLISH = "strong_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    STRONG_BEARISH = "strong_bearish"
    
class MarketImpact(str, Enum):
    """Expected market impact levels"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    NEGLIGIBLE = "negligible"
    
class AgentAnalysis(BaseModel):
    """Individuak agent's analysis output"""
    agent_name: str
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment from -1 (bearish) to 1 (bullish)")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in analysis 0 - 1")
    impact_assessment: MarketImpact
    time_horizon: Literal["immediate", "short_term", "medium_term", "long_term"]
    
    #key insights from this agent's perspective
    primary_factors: List[str] = Field(..., max_items=5, description="Top factors influencing assessment")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risks")
    opportunites: List[str] = Field(default_factory=list, description="Identified opportunites")
    
    # Reasoning and evidence
    reasoning: str = Field(..., description="Agent's reasoning process")
    supporting_quotes: List[str] = Field(default_factory=list, max_items=3, description="key quotes from article")
    
    # Agent specific insights
    specialist_insights: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific analysis")
    
class ConsensusAnalysis(BaseModel):
    """Combined analysis from all the agents"""
    article_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Individual agent analyses
    agent_analyses: Dict[str, AgentAnalysis]
    
    # Consensus metrics
    overall_sentiment: SentimentSignal
    overall_impact: MarketImpact
    consensus_score: float = Field(..., ge=0.0, le=1.0, description="How aligned agents are (0=total disagreement, 1 = perfect alignment)")
    
    # Combined insights
    unified_factors: List[str] = Field(..., description="Factors multiple agents agree on")
    conflicting_views: List[Dict[str, str]] =  Field(default_factory=List, description="Where agents disagree and why")
    
    #Decision and recommendation
    market_recommendation : Literal["strong_buy", "buy", "hold", "sell", "strong_sell",  "high_volatility_caution"]
    action_confidence: float = Field(..., ge=0.0, le=1.0)
    
    #Risk assessment
    volatility_expectation: Literal["very_high", "high", "moderate", "low"]
    key_risks: List[str]
    key_opportunities: List[str]
    
    #Synthesis
    executive_summary: str = Field(..., max_length=500, description="Brief summary for decision makers")
    detailed_rationale: str = Field(..., description="Detailed explanation of consensus/conflicts")
    
class PromptIteration(BaseModel):
    """Track prompt evolution for documentation"""
    iteration_number: int
    agent_name: str
    prompt_version: str
    changes_made: str
    rationale: str
    test_results: Optional[str] = None
    
class EvaluationResult(BaseModel):
    """Results from evaluation metrics"""
    metric_name: str
    value: float
    interpretation: str
    details: Optional[Dict[str, Any]] = None
    
class TestCaseResult(BaseModel):
    """Results for a single test case"""
    article_id: str
    consensus_analysis: ConsensusAnalysis
    processing_time_seconds: float
    agent_agreement_matrix: Dict[str, Dict[str, float]] #pairwise agreement
    notable_insights: List[str]
    evaluation_metrics: List[EvaluationResult]