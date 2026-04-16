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
import warnings
import urllib3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    RSS_FEEDS,
    KEYWORDS,
    DAILY_LIMIT,
    COLLECTION_TIME,
    MAX_ENTRIES_PER_FEED,
)
from openai import OpenAI

# Suppress SSL warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DeepSeekAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
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
                    {
                        "role": "system",
                        "content": "You are an AI expert analyzing technical content.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
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
                "confidence": 1,
            }


class RSSCollector:
    def __init__(self):
        self.analyzer = DeepSeekAnalyzer()
        self.collected_count = 0

    def fetch_feeds(self) -> List[Dict]:
        all_entries = []
        seen_urls = set()  # For deduplication

        for feed_url in RSS_FEEDS:
            try:
                # Use requests to fetch with custom SSL handling
                headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; AI-Knowledge-Base/1.0)"
                }
                response = requests.get(
                    feed_url, headers=headers, timeout=30, verify=False
                )

                if response.status_code != 200:
                    print(f"Error fetching {feed_url}: HTTP {response.status_code}")
                    continue

                # Parse the response content
                feed = feedparser.parse(response.text)
                print(f"Fetched {len(feed.entries)} entries from {feed_url}")

                # Limit number of entries processed per feed
                entries_to_process = feed.entries[:MAX_ENTRIES_PER_FEED]

                for entry in entries_to_process:
                    if self.collected_count >= DAILY_LIMIT:
                        break

                    # Get entry URL for deduplication
                    entry_url = entry.get("link", "")
                    if not entry_url or entry_url in seen_urls:
                        continue  # Skip duplicate or missing URL

                    # Check if content contains keywords
                    content = self._get_entry_content(entry)
                    if self._contains_keywords(content):
                        seen_urls.add(entry_url)  # Mark as seen
                        all_entries.append(
                            {
                                "title": entry.get("title", ""),
                                "url": entry_url,
                                "content": content,
                                "source": feed_url,
                                "published": entry.get("published", ""),
                            }
                        )
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

        # For arXiv papers (which are already in AI categories), accept all
        # or use more lenient checking
        if len(text_lower) < 100:  # Short text (likely just title)
            # Check if title seems AI-related
            ai_indicators = [
                "learning",
                "neural",
                "network",
                "transformer",
                "gpt",
                "llm",
                "nlp",
                "vision",
            ]
            if any(indicator in text_lower for indicator in ai_indicators):
                return True

        # Original keyword check
        return any(
            keyword.lower() in text_lower for keyword in KEYWORDS if keyword.strip()
        )

    def save_to_markdown(self, entry: Dict, analysis: Dict):
        # Determine category based on source
        category = self._categorize_entry(entry["source"])
        date_str = datetime.now().strftime("%Y%m%d")

        # Create filename
        title_slug = re.sub(r"[^\w\s-]", "", entry["title"]).strip().lower()
        title_slug = re.sub(r"[-\s]+", "-", title_slug)[:50]
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
            for evidence in analysis.get("evidence", []):
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
        elif "hnrss.org" in source_url:
            return "news"
        elif any(
            domain in source_url
            for domain in [
                "openai.com",
                "anthropic.com",
                "google.com",
                "meta.com",
                "deepmind.com",
            ]
        ):
            return "blog"
        elif any(
            word in source_url.lower()
            for word in ["github.com", "tool", "library", "framework"]
        ):
            return "tool"
        else:
            # Default to news for unknown sources
            return "news"

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
