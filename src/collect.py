import feedparser
import requests
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import schedule
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, RSS_FEEDS, KEYWORDS, DAILY_LIMIT, COLLECTION_TIME
from openai import OpenAI


class DeepSeekAnalyzer:
    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        self.model = "deepseek-chat"
    
    def analyze(self, content: str, source_url: str) -> Dict:
        prompt = f"""Analyze this AI-related content:

{content[:3000]}

Provide analysis with:
1. One-sentence summary (一级结论)
2. Key supporting evidence bullet points (多级论据)  
3. Your expert commentary (评论)
4. Recommendation score 1-5 (推荐度) - based on source credibility and content quality
5. Confidence score 1-5 (置信度) - based on source credibility

Format as JSON with keys: summary, evidence, commentary, recommendation, confidence"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI expert analyzing technical content."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            analysis = response.choices[0].message.content
            import json
            return json.loads(analysis)
        except Exception as e:
            print(f"Analysis error: {e}")
            return {
                "summary": "Analysis failed",
                "evidence": [],
                "commentary": f"Error: {e}",
                "recommendation": 1,
                "confidence": 1
            }


class RSSCollector:
    def __init__(self):
        self.analyzer = DeepSeekAnalyzer()
        self.collected_count = 0
        
    def fetch_feeds(self) -> List[Dict]:
        all_entries = []
        
        for feed_url in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url, agent='Mozilla/5.0 (compatible; AI-Knowledge-Base/1.0)')
                print(f"Fetched {len(feed.entries)} entries from {feed_url}")
                
                for entry in feed.entries:
                    if self.collected_count >= DAILY_LIMIT:
                        break
                        
                    # Check if content contains keywords
                    content = self._get_entry_content(entry)
                    if self._contains_keywords(content):
                        all_entries.append({
                            "title": entry.get("title", ""),
                            "url": entry.get("link", ""),
                            "content": content,
                            "source": feed_url,
                            "published": entry.get("published", "")
                        })
                        self.collected_count += 1
                        
            except Exception as e:
                print(f"Error fetching {feed_url}: {e}")
                
        return all_entries
    
    def _get_entry_content(self, entry) -> str:
        content = ""
        if hasattr(entry, "summary"):
            content = entry.summary
        if hasattr(entry, "content"):
            for item in entry.content:
                content += item.get("value", "")
        return content
    
    def _contains_keywords(self, text: str) -> bool:
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in KEYWORDS if keyword.strip())
    
    def save_to_markdown(self, entry: Dict, analysis: Dict):
        # Determine category based on source
        category = self._categorize_entry(entry["source"])
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Create filename
        title_slug = re.sub(r'[^\w\s-]', '', entry["title"]).strip().lower()
        title_slug = re.sub(r'[-\s]+', '-', title_slug)[:50]
        filename = f"{date_str}_{title_slug}.md"
        
        # Create directory if not exists
        category_dir = Path("knowledge-base") / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Write markdown
        filepath = category_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {entry['title']}\n\n")
            f.write(f"**Source**: [{entry['source']}]({entry['url']})\n")
            f.write(f"**Published**: {entry.get('published', 'N/A')}\n")
            f.write(f"**Collected**: {datetime.now().isoformat()}\n\n")
            
            f.write("## Summary\n")
            f.write(f"{analysis['summary']}\n\n")
            
            f.write("## Evidence\n")
            for evidence in analysis.get('evidence', []):
                f.write(f"- {evidence}\n")
            f.write("\n")
            
            f.write("## Commentary\n")
            f.write(f"{analysis['commentary']}\n\n")
            
            f.write("## Ratings\n")
            f.write(f"- **Recommendation**: {analysis['recommendation']}/5\n")
            f.write(f"- **Confidence**: {analysis['confidence']}/5\n")
            
        print(f"Saved: {filepath}")
    
    def _categorize_entry(self, source_url: str) -> str:
        if "arxiv.org" in source_url:
            return "papers"
        elif "importai.io" in source_url:
            return "news"
        elif "openai.com" in source_url or "anthropic.com" in source_url:
            return "blog"
        else:
            return "tool"
    
    def collect_and_analyze(self):
        print(f"Starting collection at {datetime.now()}")
        print(f"Target: {DAILY_LIMIT} items, keywords: {KEYWORDS}")
        
        entries = self.fetch_feeds()
        print(f"Found {len(entries)} relevant entries")
        
        for entry in entries:
            print(f"Analyzing: {entry['title'][:50]}...")
            analysis = self.analyzer.analyze(entry["content"], entry["url"])
            self.save_to_markdown(entry, analysis)
            time.sleep(1)  # Rate limiting
            
        print(f"Collection complete. Saved {len(entries)} items.")


def main():
    collector = RSSCollector()
    
    # Run once and exit (for testing)
    collector.collect_and_analyze()
    
    print("Collection completed. Exiting.")


if __name__ == "__main__":
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
        print("ERROR: Please set DEEPSEEK_API_KEY in .env file")
        print("Copy .env.example to .env and add your API key")
        sys.exit(1)
    
    main()