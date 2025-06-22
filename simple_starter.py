# improved_starter.py - Multi-Agent Financial News Analysis with Pydantic AI
"""
Improved version following Pydantic AI best practices and official examples.
Key improvements:
- Uses output_type parameter correctly
- Follows official Pydantic AI patterns
- Better error handling and debugging
- Cleaner agent definitions
"""

import asyncio
import os
from typing import Dict, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from dotenv import load_dotenv

# Step 1: Define data models
class NewsArticle(BaseModel):
    """The input - a financial news article"""
    headline: str
    content: str
    
class AgentAnalysis(BaseModel):
    """What each agent returns - structured response"""
    agent_name: str
    sentiment_score: float = Field(..., ge=-1, le=1, description="Sentiment from -1 (very bearish) to 1 (very bullish)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level from 0 to 1")
    key_insight: str = Field(..., description="Main takeaway from this agent's perspective")
    reasoning: str = Field(..., description="Brief explanation of the analysis")

class ConsensusResult(BaseModel):
    """Final consensus result"""
    recommendation: str = Field(..., description="BUY, SELL, or HOLD")
    confidence: float = Field(..., ge=0, le=1)
    average_sentiment: float = Field(..., ge=-1, le=1)
    disagreement_level: float = Field(..., ge=0)
    insights: List[str]

# Step 2: Create agents with proper output_type specification
def create_sentiment_agent() -> Agent[None, AgentAnalysis]:
    """Agent focused on market sentiment and emotions"""
    return Agent(
        'openai:gpt-4',
        output_type=AgentAnalysis,
        system_prompt="""You are a market sentiment expert specializing in emotional analysis of financial news.

Your focus areas:
- Market emotions (fear, greed, FOMO, panic)
- Investor psychology and sentiment
- Hype cycles and market psychology
- Social sentiment and retail investor behavior

Always set your agent_name to "Sentiment Analyst" and provide structured analysis."""
    )

def create_fundamental_agent() -> Agent[None, AgentAnalysis]:
    """Agent focused on fundamental business analysis"""
    return Agent(
        'openai:gpt-4',
        output_type=AgentAnalysis,
        system_prompt="""You are a fundamental analyst specializing in business metrics and financial analysis.

Your focus areas:
- Revenue, profits, and financial metrics
- Business fundamentals and growth prospects
- Competitive positioning
- Long-term value creation
- Financial health and sustainability

Always set your agent_name to "Fundamental Analyst" and provide structured analysis."""
    )

def create_technical_agent() -> Agent[None, AgentAnalysis]:
    """Agent focused on technical and market structure analysis"""
    return Agent(
        'openai:gpt-4',
        output_type=AgentAnalysis,
        system_prompt="""You are a technical analyst specializing in market structure and trading patterns.

Your focus areas:
- Price action and technical indicators
- Market structure and trends
- Trading volumes and liquidity
- Support/resistance levels
- Market timing considerations

Always set your agent_name to "Technical Analyst" and provide structured analysis."""
    )

# Step 3: Improved consensus function
def calculate_consensus(analyses: List[AgentAnalysis]) -> ConsensusResult:
    """Combine agent views into final recommendation with improved logic"""
    
    if not analyses:
        raise ValueError("No analyses provided")
    
    # Calculate metrics
    avg_sentiment = sum(a.sentiment_score for a in analyses) / len(analyses)
    sentiments = [a.sentiment_score for a in analyses]
    disagreement = max(sentiments) - min(sentiments)
    avg_confidence = sum(a.confidence for a in analyses) / len(analyses)
    
    # Enhanced recommendation logic
    if disagreement > 1.0:
        recommendation = "HOLD"
        final_confidence = 0.3  # Low confidence due to high disagreement
    elif avg_sentiment > 0.6:
        recommendation = "BUY"
        final_confidence = avg_confidence * 0.9  # High positive sentiment
    elif avg_sentiment < -0.6:
        recommendation = "SELL"
        final_confidence = avg_confidence * 0.9  # High negative sentiment
    elif abs(avg_sentiment) < 0.2:
        recommendation = "HOLD"
        final_confidence = avg_confidence * 0.7  # Neutral sentiment
    else:
        # Moderate sentiment
        recommendation = "BUY" if avg_sentiment > 0 else "SELL"
        final_confidence = avg_confidence * 0.8
    
    return ConsensusResult(
        recommendation=recommendation,
        confidence=final_confidence,
        average_sentiment=avg_sentiment,
        disagreement_level=disagreement,
        insights=[a.key_insight for a in analyses]
    )

# Step 4: Main analysis function
async def analyze_news(article: NewsArticle) -> ConsensusResult:
    """Run the multi-agent analysis with proper error handling"""
    
    print(f"\n📊 Analyzing: {article.headline}")
    print("=" * 80)
    
    # Create agents
    sentiment_agent = create_sentiment_agent()
    fundamental_agent = create_fundamental_agent()
    technical_agent = create_technical_agent()
    
    # Prepare analysis prompt
    prompt = f"""
Analyze this financial news article:

Headline: {article.headline}

Content: {article.content}

Provide your analysis based on your expertise area. Consider the implications for investors and the market.
"""
    
    print("\n🤖 Running agent analysis...")
    
    try:
        # Run all agents concurrently for better performance
        results = await asyncio.gather(
            sentiment_agent.run(prompt),
            fundamental_agent.run(prompt),
            technical_agent.run(prompt),
            return_exceptions=True
        )
        
        # Extract successful results and handle errors
        analyses = []
        agent_names = ["Sentiment", "Fundamental", "Technical"]
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Error from {agent_names[i]} Agent: {result}")
                continue
            
            analysis = result.output
            print(f"\n{analysis.agent_name}:")
            print(f"  💭 Sentiment: {analysis.sentiment_score:+.2f}")
            print(f"  🎯 Confidence: {analysis.confidence:.0%}")
            print(f"  💡 Insight: {analysis.key_insight}")
            print(f"  📝 Reasoning: {analysis.reasoning}")
            
            analyses.append(analysis)
        
        if not analyses:
            raise ValueError("All agents failed to provide analysis")
        
        # Calculate consensus
        print("\n🧠 Building Consensus...")
        consensus = calculate_consensus(analyses)
        
        # Display results
        print(f"\n📋 Final Analysis:")
        print(f"  🎯 Recommendation: {consensus.recommendation}")
        print(f"  🔒 Confidence: {consensus.confidence:.0%}")
        print(f"  📊 Average Sentiment: {consensus.average_sentiment:+.2f}")
        
        if consensus.disagreement_level > 0.5:
            print(f"  ⚠️  Warning: High agent disagreement ({consensus.disagreement_level:.2f} spread)")
        
        print(f"\n🔍 Key Insights:")
        for i, insight in enumerate(consensus.insights, 1):
            print(f"  {i}. {insight}")
        
        return consensus
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        raise

# Step 5: Test with various scenarios
async def main():
    """Run comprehensive tests"""
    
    load_dotenv()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY='your-key-here'")
        return
    
    print("🚀 Multi-Agent Financial News Analyzer")
    print("=====================================")
    
    # Test scenarios
    test_scenarios = [
        NewsArticle(
            headline="Tesla reports record Q3 profits but CEO warns of economic headwinds",
            content="""Tesla reported Q3 earnings of $3.5 billion, beating analyst expectations 
            by 25% and marking the company's strongest quarter ever. Revenue jumped 55% 
            year-over-year to $25.2 billion. However, CEO Elon Musk warned of 'significant 
            economic headwinds' and 'dark clouds on the horizon' in upcoming quarters, 
            citing rising interest rates, inflation concerns, and weakening consumer demand 
            for luxury vehicles."""
        ),
        NewsArticle(
            headline="Apple unveils revolutionary AI chip with 50% performance boost",
            content="""Apple announced its breakthrough M4 Pro chip featuring advanced AI 
            capabilities and 50% faster processing speeds compared to previous generation. 
            The chip includes dedicated neural processing units and promises to revolutionize 
            machine learning applications on Mac devices. Pre-orders for new MacBook Pro 
            models start next week, with industry analysts projecting strong demand."""
        )
    ]
    
    # Run analysis on all scenarios
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*20} TEST SCENARIO {i} {'='*20}")
        try:
            await analyze_news(scenario)
        except Exception as e:
            print(f"Scenario {i} failed: {e}")
        
        if i < len(test_scenarios):
            print("\n" + "Next scenario in 2 seconds...")
            await asyncio.sleep(2)
    
    print(f"\n{'='*60}")
    print("✅ Analysis complete!")
    print("\n🎯 Next Steps:")
    print("1. Modify agent prompts to see different perspectives")
    print("2. Add more specialized agents (e.g., Risk Analyst, Macro Economist)")
    print("3. Implement confidence weighting in consensus")
    print("4. Add real-time data feeds and market indicators")
    print("5. Create a web interface or API endpoint")

if __name__ == "__main__":
    asyncio.run(main())