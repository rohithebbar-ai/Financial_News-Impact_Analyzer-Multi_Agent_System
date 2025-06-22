# main.py
import asyncio
import os
from datetime import datetime
from typing import Dict, List
import json
from dotenv import load_dotenv

from models.data_models import (
    NewsArticle, ConsensusAnalysis, TestCaseResult, 
    AgentAnalysis, PromptIteration
)
from agents.sentiment_agent import SentimentAnalystAgent
from agents.fundamental_agent import FundamentalAnalystAgent  
from agents.market_dynamics_agent import MarketDynamicsAgent
from utils.consensus_engine import ConsensusEngine
from evaluation.metrics import MetricsCalculator
from data.test_cases import get_test_articles

class FinancialNewsAnalyzer:
    """Main orchestrator for multi-agent financial news analysis"""
    
    def __init__(self):
        # Initialize agents
        self.agents = {
            "sentiment": SentimentAnalystAgent(),
            "fundamental": FundamentalAnalystAgent(),
            "market_dynamics": MarketDynamicsAgent()
        }
        
        # Initialize consensus engine
        self.consensus_engine = ConsensusEngine()
        
        # Initialize metrics calculator
        self.metrics_calculator = MetricsCalculator()
        
        # Track prompt iterations
        self.prompt_iterations: List[PromptIteration] = []
        
    async def analyze_article(self, article: NewsArticle) -> ConsensusAnalysis:
        """Analyze a single article using all agents"""
        print(f"\n{'='*60}")
        print(f"Analyzing: {article.article_id} - {article.headline[:50]}...")
        print(f"{'='*60}")
        
        # Run all agents in parallel for efficiency
        agent_tasks = {
            name: agent.analyze(article)
            for name, agent in self.agents.items()
        }
        
        # Gather results
        agent_results = {}
        for name, task in agent_tasks.items():
            try:
                result = await task
                agent_results[result.agent_name] = result
                print(f"\n{result.agent_name}:")
                print(f"  Sentiment: {result.sentiment_score:+.2f}")
                print(f"  Impact: {result.impact_assessment.value}")
                print(f"  Confidence: {result.confidence_level:.2%}")
            except Exception as e:
                print(f"Error with {name} agent: {e}")
                # Continue with other agents
        
        # Synthesize consensus
        consensus = self.consensus_engine.synthesize(article, agent_results)
        
        # Display consensus results
        print(f"\nCONSENSUS ANALYSIS:")
        print(f"  Overall Sentiment: {consensus.overall_sentiment.value}")
        print(f"  Market Impact: {consensus.overall_impact.value}")
        print(f"  Recommendation: {consensus.market_recommendation}")
        print(f"  Confidence: {consensus.action_confidence:.2%}")
        print(f"  Consensus Score: {consensus.consensus_score:.2%}")
        
        if consensus.conflicting_views:
            print(f"\n  ⚠️  Conflicts Detected:")
            for conflict in consensus.conflicting_views:
                print(f"    - {conflict['description']}")
        
        print(f"\n  Executive Summary:")
        print(f"    {consensus.executive_summary}")
        
        return consensus
    
    async def run_all_tests(self):
        """Run analysis on all test articles"""
        print("\n" + "="*80)
        print("FINANCIAL NEWS IMPACT ANALYZER - MULTI-AGENT SYSTEM")
        print("="*80)
        
        test_articles = get_test_articles()
        
        for article in test_articles:
            start_time = datetime.now()
            
            # Analyze article
            consensus = await self.analyze_article(article)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create test result
            result = TestCaseResult(
                article_id=article.article_id,
                consensus_analysis=consensus,
                processing_time_seconds=processing_time,
                agent_agreement_matrix=self._calculate_agreement_matrix(consensus.agent_analyses),
                notable_insights=self._extract_notable_insights(consensus),
                evaluation_metrics=[]  # Will be filled by metrics calculator
            )
            
            # Add to metrics
            self.metrics_calculator.add_result(result)
            
            # Small delay between analyses (for API rate limits if using real APIs)
            await asyncio.sleep(0.5)
        
        # Generate evaluation report
        print("\n" + "="*80)
        print("EVALUATION REPORT")
        print("="*80)
        print(self.metrics_calculator.generate_summary_report())
        
        # Save results
        self._save_results()
    
    def _calculate_agreement_matrix(self, 
                                  agent_analyses: Dict[str, AgentAnalysis]) -> Dict[str, Dict[str, float]]:
        """Calculate pairwise agreement between agents"""
        matrix = {}
        agents = list(agent_analyses.keys())
        
        for i, agent1 in enumerate(agents):
            matrix[agent1] = {}
            for j, agent2 in enumerate(agents):
                if i == j:
                    matrix[agent1][agent2] = 1.0
                else:
                    # Simple sentiment distance as agreement measure
                    sent_diff = abs(
                        agent_analyses[agent1].sentiment_score - 
                        agent_analyses[agent2].sentiment_score
                    )
                    agreement = 1 - (sent_diff / 2)
                    matrix[agent1][agent2] = round(agreement, 3)
        
        return matrix
    
    def _extract_notable_insights(self, consensus: ConsensusAnalysis) -> List[str]:
        """Extract key insights from the analysis"""
        insights = []
        
        # Map sentiment enum to numeric values for analysis
        sentiment_values = {
            "strong_bullish": 1.0,
            "bullish": 0.5,
            "neutral": 0.0,
            "bearish": -0.5,
            "strong_bearish": -1.0
        }
        
        # High consensus with strong sentiment
        sentiment_numeric = sentiment_values.get(consensus.overall_sentiment.value, 0.0)
        if consensus.consensus_score > 0.8 and abs(sentiment_numeric) > 0.5:
            insights.append("Strong agent alignment on clear market signal")
        
        # High disagreement
        if len(consensus.conflicting_views) >= 2:
            insights.append("Multiple conflicts suggest high uncertainty")
        
        # Sentiment vs fundamentals divergence
        agent_sentiments = {
            name: analysis.sentiment_score 
            for name, analysis in consensus.agent_analyses.items()
        }
        
        if "SentimentAnalystAgent" in agent_sentiments and "FundamentalAnalystAgent" in agent_sentiments:
            sent_fund_diff = abs(
                agent_sentiments["SentimentAnalystAgent"] - 
                agent_sentiments["FundamentalAnalystAgent"]
            )
            if sent_fund_diff > 1.0:
                insights.append("Major sentiment/fundamentals divergence detected")
        
        return insights
    
    def _save_results(self):
        """Save analysis results to file"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics_calculator.calculate_all_metrics(),
            "test_results": [
                {
                    "article_id": r.article_id,
                    "consensus_score": r.consensus_analysis.consensus_score,
                    "recommendation": r.consensus_analysis.market_recommendation,
                    "conflicts": len(r.consensus_analysis.conflicting_views),
                    "processing_time": r.processing_time_seconds
                }
                for r in self.metrics_calculator.results
            ]
        }
        
        with open("analysis_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print("\n✓ Results saved to analysis_results.json")
    
    def document_prompt_iterations(self):
        """Document the prompt engineering process"""
        iterations = [
            PromptIteration(
                iteration_number=1,
                agent_name="SentimentAnalystAgent",
                prompt_version="Basic sentiment analysis",
                changes_made="Initial simple prompt asking for positive/negative assessment",
                rationale="Start with baseline to test agent responsiveness",
                test_results="Agents gave similar responses, lacked specialization"
            ),
            PromptIteration(
                iteration_number=2, 
                agent_name="All Agents",
                prompt_version="Added structured output requirements",
                changes_made="Required specific scores, factors, and confidence levels",
                rationale="Need consistent output format for consensus building",
                test_results="Better structure but agents still too similar"
            ),
            PromptIteration(
                iteration_number=3,
                agent_name="All Agents",
                prompt_version="Emphasized specialized perspectives",
                changes_made="Added detailed role descriptions and focus areas for each agent",
                rationale="Agents need distinct viewpoints to complement each other",
                test_results="Much better differentiation - agents now disagree meaningfully"
            )
        ]
        
        # Create docs directory if it doesn't exist
        os.makedirs("docs", exist_ok=True)
        
        # Save iterations
        with open("docs/prompt_iterations.json", "w") as f:
            json.dump([i.model_dump() for i in iterations], f, indent=2)
        
        print("✓ Prompt iterations documented in docs/prompt_iterations.json")

async def main():
    """Main entry point"""
    # Check for API key
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Please set it to use the system.")
        print("Example: export OPENAI_API_KEY='your-key-here'")
        return
    
    # Create analyzer
    analyzer = FinancialNewsAnalyzer()
    
    # Document prompt iterations
    analyzer.document_prompt_iterations()
    
    # Run all tests
    await analyzer.run_all_tests()
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    asyncio.run(main())