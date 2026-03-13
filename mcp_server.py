# mcp_server.py
from mcp.server.fastmcp import FastMCP
import requests
import feedparser

# Initialize the MCP Server
mcp = FastMCP("AlphaMachineEngine")

@mcp.tool()
def fetch_sector_news(sector: str) -> str:
    """Fetches latest RSS news for a specific sector."""
    url = f"https://news.google.com/rss/search?q={sector}+stocks"
    feed = feedparser.parse(url)
    entries = [f"- {e.title}" for e in feed.entries[:5]]
    return "\n".join(entries) if entries else "No news found."

@mcp.tool()
def calculate_asymmetry_score(upside: float, downside: float) -> float:
    """Calculates the Risk/Reward asymmetry ratio."""
    if downside == 0: return upside
    return round(upside / abs(downside), 2)

if __name__ == "__main__":
    mcp.run()
