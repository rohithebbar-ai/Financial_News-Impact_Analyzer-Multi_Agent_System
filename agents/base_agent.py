# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic_ai import Agent
from models.data_models import NewsArticle, AgentAnalysis, MarketImpact
import os
import asyncio
from dotenv import load_dotenv

class BaseFinancialAgent(ABC):
    """Base class for all financial analysis agents"""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the agent with model configuration"""
        load_dotenv()
        
        if model:
            self.model = model
        else:
            # Try environment variable first, then default
            env_model = os.getenv("OPENAI_MODEL")
            if env_model:
                self.model = env_model
            else:
                self.model = "openai:gpt-4" 
        
        self.name = self.__class__.__name__
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in your .env file or environment."
            )
        
        self.agent = self._create_agent()
        
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Define the agent's specialized system prompt"""
        pass
        
    @abstractmethod
    def _get_specialist_focus_areas(self) -> List[str]:
        """Define what this agent specifically looks for"""
        pass
    
    def _create_agent(self) -> Agent:
        """Create the Pydantic AI agent with structured output"""
        return Agent(
            self.model,                           # Model as first positional argument
            system_prompt=self._get_full_system_prompt(),
            output_type=AgentAnalysis,            # FIXED: result_type -> output_type
            output_retries=3                      # FIXED: result_retries -> output_retries
        )
    
    def _get_full_system_prompt(self) -> str:
        """Combine base prompt with output format instructions"""
        base_prompt = self._get_system_prompt()
        focus_areas = "\n".join([f"- {area}" for area in self._get_specialist_focus_areas()])
        
        return f"""{base_prompt}

Your Specialized Focus Areas:
{focus_areas}

You must provide your analysis in the following structured format:
- agent_name: Your role name (e.g., "SentimentAnalystAgent")
- sentiment_score: A float between -1.0 (extremely bearish) and 1.0 (extremely bullish)
- confidence_level: A float between 0.0 and 1.0 indicating your confidence
- impact_assessment: One of "very_high", "high", "moderate", "low", or "negligible"
- time_horizon: One of "immediate", "short_term", "medium_term", or "long_term"
- primary_factors: A list of up to 5 key factors influencing your assessment
- risk_factors: A list of identified risks from your perspective
- opportunities: A list of potential opportunities you see
- reasoning: A detailed explanation of your analysis
- supporting_quotes: 1-3 key quotes from the article supporting your analysis
- specialist_insights: A dictionary with your unique domain-specific insights

Focus on your specialized perspective and provide insights that other analysts might miss."""

    async def analyze(self, article: NewsArticle) -> AgentAnalysis:
        """Analyze the article and return structured analysis"""
        
        # Build the prompt
        prompt = f"""Analyze this financial news article from your specialized perspective:

Article ID: {article.article_id}
Headline: {article.headline}
Content: {article.content}
Published: {article.published_at}

Provide a comprehensive analysis focusing on your domain expertise."""

        try:
            # Run the agent and get structured output
            result = await self.agent.run(prompt)
            
            # FIXED: Use modern result access
            analysis = result.output  # Modern way to access result
            
            # Ensure agent name is set correctly
            analysis.agent_name = self.name
            return analysis
                
        except Exception as e:
            print(f"Error in {self.name}: {e}")
            # Return a default analysis on error
            return AgentAnalysis(
                agent_name=self.name,
                sentiment_score=0.0,
                confidence_level=0.0,
                impact_assessment=MarketImpact.MODERATE,
                time_horizon="short_term",
                primary_factors=[f"Error analyzing: {str(e)}"],
                risk_factors=[],
                opportunities=[],
                reasoning=f"Analysis failed: {str(e)}",
                supporting_quotes=[],
                specialist_insights={}
            )