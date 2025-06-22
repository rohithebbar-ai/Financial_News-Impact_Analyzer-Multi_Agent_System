# data/test_cases.py
from models.data_models import NewsArticle

TEST_ARTICLES = [
    NewsArticle(
        article_id="FIN-001",
        headline="Tesla crushes Q3 expectations with record profits, but Musk warns of 'turbulent times'",
        content="Tesla (NASDAQ: TSLA) reported stunning Q3 results with earnings of $1.05 per share, beating analyst expectations of $0.73. Revenue surged 23% year-over-year to $25.2 billion, driven by record vehicle deliveries and improving margins. However, CEO Elon Musk tempered enthusiasm during the earnings call, warning of 'turbulent times ahead' and 'storm clouds gathering' for the global economy. He specifically mentioned supply chain pressures and potential demand softening in key markets. The stock initially surged 8% in after-hours trading before pulling back to +2% as investors digested Musk's cautionary comments.",
        published_at="2024-10-22T16:00:00Z"
    ),
    NewsArticle(
        article_id="FIN-002",
        headline="Small biotech CureGen soars on FDA approval, analysts remain skeptical",
        content="CureGen (NASDAQ: CURE), a small-cap biotech, received FDA approval for its novel cancer treatment CG-401, sending shares up 187% in pre-market trading. The drug showed promising results in Phase 3 trials with 73% efficacy rate. However, leading analysts from Goldman Sachs and Morgan Stanley issued cautionary notes, citing commercialization challenges and competition from established players. 'While the approval is positive, CureGen lacks the infrastructure to capitalize effectively,' noted Goldman's biotech team. The company has just $47 million in cash reserves and no existing sales force.",
        published_at="2024-11-01T14:30:00Z"
    ),
    NewsArticle(
        article_id="FIN-003",
        headline="Amazon announces 'transformational' AI venture, but at massive cost",
        content="Amazon (NASDAQ: AMZN) unveiled Project Olympus, a $50 billion investment in AGI development over the next 5 years, calling it 'the most ambitious technical undertaking in human history.' CEO Andy Jassy described it as essential for Amazon's future, projecting it could add $500 billion to company value by 2030. However, the massive upfront investment spooked investors, with shares falling 7% as analysts worried about near-term margin pressure. CFO Brian Olsavsky acknowledged the project would reduce operating margins by 200-300 basis points annually through 2028. Several analysts downgraded the stock citing execution risk.",
        published_at="2024-09-15T09:00:00Z"
    ),
    NewsArticle(
        article_id="FIN-004",
        headline="Regional bank FirstState posts record earnings amid industry turmoil",
        content="FirstState Bank (NYSE: FSB) reported record Q2 earnings of $3.20 per share, up 45% year-over-year, defying the regional banking crisis narrative. Net interest margins expanded to 4.2% while credit losses remained near historic lows at 0.3%. CEO Patricia Chen attributed success to conservative underwriting and limited commercial real estate exposure. 'We've been preparing for this environment for years,' Chen stated. However, the broader regional banking index remains down 30% year-to-date, and analysts warn that FirstState's small size ($15B assets) could make it an acquisition target as sector consolidation accelerates.",
        published_at="2024-10-12T10:30:00Z"
    ),
    NewsArticle(
        article_id="FIN-005", 
        headline="China tech giant ByteDance reports stellar growth, regulatory clouds remain",
        content="ByteDance, TikTok's parent company, leaked financials show revenue grew 70% to $120 billion in 2023, with operating margins exceeding 25%. The figures, first reported by Bloomberg, suggest TikTok's monetization is accelerating faster than Meta or YouTube at similar stages. However, regulatory pressures continue mounting with potential U.S. ban legislation advancing in Congress and new EU data privacy rules taking effect. India's continued ban has already cost ByteDance an estimated $6 billion annually. Investment banks value the company between $250-300 billion despite the regulatory overhang, suggesting massive upside if political risks resolve.",
        published_at="2024-11-21T18:45:00Z"
    )
]

def get_test_articles():
    """Return all test articles"""
    return TEST_ARTICLES

def get_article_by_id(article_id: str) -> NewsArticle:
    """Get specific test article by ID"""
    for article in TEST_ARTICLES:
        if article.article_id == article_id:
            return article
    raise ValueError(f"Article {article_id} not found")