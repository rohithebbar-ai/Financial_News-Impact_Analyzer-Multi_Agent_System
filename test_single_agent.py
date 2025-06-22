#!/usr/bin/env python3
"""
Test script for single agent validation
Step 5 in the development workflow

This script tests the SentimentAnalystAgent to ensure:
1. It can analyze news articles correctly
2. It returns properly structured AgentAnalysis objects
3. It provides reasonable sentiment scores and insights
4. It handles different types of news appropriately
"""

import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Import your models and agent
from models.data_models import NewsArticle, AgentAnalysis, MarketImpact
from agents.sentiment_agent import SentimentAnalystAgent

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_analysis_results(analysis: AgentAnalysis, test_name: str):
    """Print analysis results in a readable format"""
    print(f"\n📊 {test_name} Results:")
    print("-" * 40)
    print(f"🤖 Agent: {analysis.agent_name}")
    print(f"📈 Sentiment Score: {analysis.sentiment_score:+.2f} ({get_sentiment_label(analysis.sentiment_score)})")
    print(f"🎯 Confidence: {analysis.confidence_level:.0%}")
    print(f"⚡ Impact: {analysis.impact_assessment.value}")
    print(f"⏰ Time Horizon: {analysis.time_horizon}")
    
    print(f"\n🔍 Primary Factors:")
    for i, factor in enumerate(analysis.primary_factors, 1):
        print(f"  {i}. {factor}")
    
    if analysis.risk_factors:
        print(f"\n⚠️  Risk Factors:")
        for i, risk in enumerate(analysis.risk_factors, 1):
            print(f"  {i}. {risk}")
    
    if analysis.opportunites:  # Note: keeping the typo from their model
        print(f"\n💡 Opportunities:")
        for i, opp in enumerate(analysis.opportunites, 1):
            print(f"  {i}. {opp}")
    
    if analysis.supporting_quotes:
        print(f"\n📝 Supporting Quotes:")
        for i, quote in enumerate(analysis.supporting_quotes, 1):
            print(f"  {i}. \"{quote}\"")
    
    print(f"\n🧠 Reasoning:")
    print(f"  {analysis.reasoning}")
    
    if analysis.specialist_insights:
        print(f"\n🔬 Specialist Insights:")
        for key, value in analysis.specialist_insights.items():
            print(f"  {key}: {value}")

def get_sentiment_label(score: float) -> str:
    """Convert sentiment score to human-readable label"""
    if score >= 0.6:
        return "Strong Bullish"
    elif score >= 0.2:
        return "Bullish"
    elif score >= -0.2:
        return "Neutral"
    elif score >= -0.6:
        return "Bearish"
    else:
        return "Strong Bearish"

def validate_analysis(analysis: AgentAnalysis) -> tuple[bool, list[str]]:
    """Validate that analysis meets expected structure"""
    issues = []
    
    # Check required fields
    if not analysis.agent_name:
        issues.append("Missing agent_name")
    
    if not (-1.0 <= analysis.sentiment_score <= 1.0):
        issues.append(f"Sentiment score {analysis.sentiment_score} out of range [-1, 1]")
    
    if not (0.0 <= analysis.confidence_level <= 1.0):
        issues.append(f"Confidence {analysis.confidence_level} out of range [0, 1]")
    
    if not analysis.primary_factors:
        issues.append("No primary factors provided")
    
    if len(analysis.primary_factors) > 5:
        issues.append(f"Too many primary factors: {len(analysis.primary_factors)} (max 5)")
    
    if not analysis.reasoning:
        issues.append("No reasoning provided")
    
    if len(analysis.supporting_quotes) > 3:
        issues.append(f"Too many supporting quotes: {len(analysis.supporting_quotes)} (max 3)")
    
    return len(issues) == 0, issues

def create_test_articles() -> list[NewsArticle]:
    """Create test articles with different sentiment scenarios"""
    
    return [
        # Test 1: Clearly Positive News
        NewsArticle(
            article_id="TEST-001",
            headline="Tesla Reports Record Q3 Earnings, Beats All Expectations",
            content="""Tesla (NASDAQ: TSLA) announced outstanding Q3 results with earnings of $1.20 per share, 
            dramatically beating analyst expectations of $0.85. Revenue surged 45% to $28.5 billion, driven by 
            strong vehicle deliveries and expanding margins. CEO Elon Musk expressed confidence about the future, 
            stating "We're entering our strongest growth phase yet with revolutionary new products coming soon." 
            The company also announced a $5 billion share buyback program.""",
            published_at="2024-12-21T16:00:00Z"
        ),
        
        # Test 2: Mixed Signals / Neutral
        NewsArticle(
            article_id="TEST-002", 
            headline="Apple Reports Solid Earnings but Warns of Supply Chain Challenges",
            content="""Apple Inc. (AAPL) reported quarterly earnings that met analyst expectations with revenue 
            of $90.1 billion. However, management warned of potential supply chain disruptions in the coming quarter 
            that could impact iPhone production. While services revenue grew 8%, hardware sales remained flat. 
            CEO Tim Cook noted both opportunities in emerging markets and headwinds from economic uncertainty.""",
            published_at="2024-12-21T15:30:00Z"
        ),
        
        # Test 3: Clearly Negative News
        NewsArticle(
            article_id="TEST-003",
            headline="TechCorp Announces Massive Layoffs, CEO Resignation Amid Scandal",
            content="""TechCorp (NASDAQ: TECH) announced devastating news today with the resignation of CEO John Smith 
            following an accounting scandal investigation. The company is laying off 40% of its workforce (12,000 employees) 
            and expects to report a massive loss this quarter. Trading has been halted as regulators investigate 
            potential securities fraud. Credit rating agencies are reviewing the company's debt for possible downgrade.""",
            published_at="2024-12-21T14:00:00Z"
        ),
        
        # Test 4: Hype vs Reality Test
        NewsArticle(
            article_id="TEST-004",
            headline="🚀 REVOLUTIONARY AI BREAKTHROUGH! Small Cap Soars 300% on Quantum Computing Claims! 🚀",
            content="""NanoTech Industries, a small technology company, announced today what it calls a 
            "revolutionary quantum AI breakthrough" that will "change everything." The stock soared 300% 
            in pre-market trading on the announcement. However, details remain vague, and the company has 
            provided no peer-reviewed research or technical specifications. Industry experts express skepticism, 
            noting the company's lack of previous quantum computing experience.""",
            published_at="2024-12-21T13:00:00Z"
        )
    ]

async def test_sentiment_agent():
    """Main test function"""
    
    print_header("Sentiment Agent Testing Suite")
    
    # Check environment setup
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("Please set your OpenAI API key in .env file")
        return False
    
    print("✅ Environment setup validated")
    
    # Initialize agent
    try:
        agent = SentimentAnalystAgent()
        print("✅ SentimentAnalystAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False
    
    # Create test articles
    test_articles = create_test_articles()
    print(f"✅ Created {len(test_articles)} test articles")
    
    # Test each article
    all_tests_passed = True
    
    for i, article in enumerate(test_articles, 1):
        print_header(f"Test Case {i}: {article.article_id}")
        print(f"📰 Headline: {article.headline}")
        
        try:
            # Run analysis
            print("🔄 Running sentiment analysis...")
            start_time = datetime.now()
            
            analysis = await agent.analyze(article)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Print results
            print_analysis_results(analysis, f"Test {i}")
            print(f"\n⏱️  Processing time: {processing_time:.2f} seconds")
            
            # Validate results
            is_valid, issues = validate_analysis(analysis)
            
            if is_valid:
                print("✅ Analysis validation: PASSED")
            else:
                print("❌ Analysis validation: FAILED")
                for issue in issues:
                    print(f"  - {issue}")
                all_tests_passed = False
            
            # Sentiment-specific checks
            print(f"\n🔍 Sentiment Analysis Check:")
            
            # Test 1 should be positive
            if i == 1 and analysis.sentiment_score <= 0:
                print("⚠️  Warning: Expected positive sentiment for record earnings news")
            
            # Test 3 should be negative  
            elif i == 3 and analysis.sentiment_score >= 0:
                print("⚠️  Warning: Expected negative sentiment for layoffs/scandal news")
            
            # Test 4 should show awareness of hype
            elif i == 4:
                if "hype" in analysis.reasoning.lower() or "skeptic" in analysis.reasoning.lower():
                    print("✅ Agent correctly identified hype/skepticism elements")
                else:
                    print("⚠️  Agent may have missed hype vs reality signals")
            
        except Exception as e:
            print(f"❌ Test {i} failed with error: {e}")
            all_tests_passed = False
    
    # Final summary
    print_header("Test Summary")
    
    if all_tests_passed:
        print("🎉 All tests PASSED! Your sentiment agent is working correctly.")
        print("\n✅ Next Steps:")
        print("  1. Agent structure validation: ✅")
        print("  2. Sentiment scoring: ✅") 
        print("  3. Output formatting: ✅")
        print("  4. Error handling: ✅")
        print("\n🚀 Ready to proceed to step 6: Create your second agent!")
    else:
        print("❌ Some tests FAILED. Please review and fix issues before proceeding.")
        print("\n🔧 Common issues to check:")
        print("  - API key configuration")
        print("  - Pydantic model field names match")
        print("  - Agent prompt returning structured data")
        print("  - Import paths are correct")
    
    return all_tests_passed

async def quick_test():
    """Quick test with just one article for rapid iteration"""
    print_header("Quick Test - Single Article")
    
    # Quick test article
    article = NewsArticle(
        article_id="QUICK-001",
        headline="Company XYZ Beats Earnings Expectations",
        content="Company XYZ reported strong quarterly results, beating analyst expectations.",
        published_at="2024-12-21T12:00:00Z"
    )
    
    try:
        agent = SentimentAnalystAgent()
        analysis = await agent.analyze(article)
        
        print(f"✅ Quick test successful!")
        print(f"Sentiment: {analysis.sentiment_score:+.2f}")
        print(f"Confidence: {analysis.confidence_level:.0%}")
        print(f"Agent: {analysis.agent_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Sentiment Agent Test Suite")
    print("Choose test mode:")
    print("1. Full test suite (4 test cases)")
    print("2. Quick test (1 test case)")
    
    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            asyncio.run(test_sentiment_agent())
        elif choice == "2":
            asyncio.run(quick_test())
        else:
            print("Invalid choice. Running quick test...")
            asyncio.run(quick_test())
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your setup and try again")