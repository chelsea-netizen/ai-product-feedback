#!/usr/bin/env python3
"""Standalone AI Product Feedback Scraper.

This script collects AI product feedback from Reddit and HackerNews,
categorizes it, and outputs to JSONL format.
"""

import json
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

import httpx


# =============================================================================
# Data Models
# =============================================================================


class FeedbackSource(Enum):
    """Source platforms for feedback."""
    REDDIT = "reddit"
    HACKERNEWS = "hackernews"


class AIProduct(Enum):
    """AI products we're tracking."""
    CLAUDE = "claude"
    CHATGPT = "chatgpt"
    GEMINI = "gemini"
    COPILOT = "copilot"
    PERPLEXITY = "perplexity"
    GROK = "grok"
    UNKNOWN = "unknown"


class FeedbackCategory(Enum):
    """Categories of UX/content feedback."""
    CONTENT_CLARITY = "content_clarity"
    TONE = "tone"
    ERROR_MESSAGES = "error_messages"
    ONBOARDING = "onboarding"
    NAVIGATION = "navigation"
    RESPONSE_QUALITY = "response_quality"
    FEATURE_DISCOVERY = "feature_discovery"
    NAMING_TERMINOLOGY = "naming_terminology"
    GENERAL_UX = "general_ux"


@dataclass
class Feedback:
    """A piece of feedback about an AI product."""
    id: str
    source: FeedbackSource
    source_url: str
    title: str | None
    text: str
    author: str | None
    timestamp: datetime
    score: int | None
    num_comments: int | None
    products: list[AIProduct]
    categories: list[FeedbackCategory]
    sentiment: str | None
    collected_at: datetime
    processed: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "source": self.source.value,
            "source_url": self.source_url,
            "title": self.title,
            "text": self.text,
            "author": self.author,
            "timestamp": self.timestamp.isoformat(),
            "score": self.score,
            "num_comments": self.num_comments,
            "products": [p.value for p in self.products],
            "categories": [c.value for c in self.categories],
            "sentiment": self.sentiment,
            "collected_at": self.collected_at.isoformat(),
            "processed": self.processed,
        }


# =============================================================================
# Keywords for filtering
# =============================================================================

AI_KEYWORDS = [
    "chatgpt", "claude", "gemini", "copilot", "perplexity",
    "grok", "bard", "gpt-4", "gpt-3", "openai", "anthropic",
]

UX_KEYWORDS = [
    # General UX terms
    "ux", "user experience", "confusing", "unclear", "error",
    "interface", "design", "usability", "hard to use", "difficult",
    "tone", "response", "output", "formatting", "frustrating",
    # Specific UX feedback indicators
    "why is it called", "why did they name", "confusing name",
    "what does", "what's a", "what is a", "difference between",
    "didn't know", "didn't realize", "had no idea", "just learned",
    "hidden feature", "found by accident", "error message",
    "sounds", "comes across", "robotic", "verbose", "patronizing",
    "wall of text", "hard to read", "doesn't make sense",
    "getting started", "new user", "first time", "learning curve",
    "can't find", "where is", "how do i",
]


# =============================================================================
# Helper functions
# =============================================================================

def is_relevant(text: str) -> bool:
    """Check if text contains relevant keywords."""
    if not text:
        return False
    text_lower = text.lower()
    has_ai = any(keyword in text_lower for keyword in AI_KEYWORDS)
    has_ux = any(keyword in text_lower for keyword in UX_KEYWORDS)
    return has_ai and has_ux


def extract_products(text: str) -> list[AIProduct]:
    """Extract mentioned AI products from text."""
    text_lower = text.lower()
    products = []

    if any(kw in text_lower for kw in ["claude", "anthropic"]):
        products.append(AIProduct.CLAUDE)
    if any(kw in text_lower for kw in ["chatgpt", "gpt-4", "gpt-3", "openai"]):
        products.append(AIProduct.CHATGPT)
    if any(kw in text_lower for kw in ["gemini", "bard"]):
        products.append(AIProduct.GEMINI)
    if "copilot" in text_lower:
        products.append(AIProduct.COPILOT)
    if "perplexity" in text_lower:
        products.append(AIProduct.PERPLEXITY)
    if "grok" in text_lower:
        products.append(AIProduct.GROK)

    return products if products else [AIProduct.UNKNOWN]


def extract_categories(text: str) -> list[FeedbackCategory]:
    """Extract feedback categories from text."""
    text_lower = text.lower()
    categories = []

    # Naming & terminology
    if any(kw in text_lower for kw in [
        "why is it called", "why did they name", "confusing name",
        "what does", "what's a", "what is a", "difference between"
    ]):
        categories.append(FeedbackCategory.NAMING_TERMINOLOGY)

    # Feature discovery
    if any(kw in text_lower for kw in [
        "didn't know", "didn't realize", "had no idea", "just learned",
        "didn't even know", "hidden feature", "found by accident"
    ]):
        categories.append(FeedbackCategory.FEATURE_DISCOVERY)

    # Error messages
    if any(kw in text_lower for kw in ["error message", "error:", "failed"]):
        categories.append(FeedbackCategory.ERROR_MESSAGES)

    # Tone
    if any(kw in text_lower for kw in [
        "tone", "sounds", "comes across", "robotic", "verbose", "patronizing"
    ]):
        categories.append(FeedbackCategory.TONE)

    # Content clarity
    if any(kw in text_lower for kw in [
        "unclear", "confusing", "doesn't make sense", "hard to read", "wall of text"
    ]):
        categories.append(FeedbackCategory.CONTENT_CLARITY)

    # Onboarding
    if any(kw in text_lower for kw in [
        "onboarding", "getting started", "new user", "first time", "learning curve"
    ]):
        categories.append(FeedbackCategory.ONBOARDING)

    # Navigation
    if any(kw in text_lower for kw in [
        "navigation", "find", "locate", "menu", "can't find"
    ]):
        categories.append(FeedbackCategory.NAVIGATION)

    # Response quality
    if any(kw in text_lower for kw in [
        "response", "output", "answer", "result", "quality"
    ]):
        categories.append(FeedbackCategory.RESPONSE_QUALITY)

    return categories if categories else [FeedbackCategory.GENERAL_UX]


# =============================================================================
# Reddit Scraper
# =============================================================================

def scrape_reddit(limit: int = 100) -> Iterator[Feedback]:
    """Scrape Reddit for AI product feedback."""
    subreddits = [
        "artificial", "ChatGPT", "ClaudeAI", "OpenAI",
        "LocalLLaMA", "ArtificialIntelligence", "MachineLearning", "singularity",
    ]

    client = httpx.Client(timeout=30.0)
    collected = 0

    for subreddit in subreddits:
        if collected >= limit:
            break

        try:
            url = f"https://www.reddit.com/r/{subreddit}/new.json"
            response = client.get(
                url,
                headers={"User-Agent": "AI Product Feedback Collector v1.0"}
            )
            response.raise_for_status()
            data = response.json()

            for post in data["data"]["children"]:
                if collected >= limit:
                    break

                post_data = post["data"]
                title = post_data.get("title", "")
                text = post_data.get("selftext", "")
                combined_text = f"{title}\n\n{text}"

                if not is_relevant(combined_text):
                    continue

                feedback = Feedback(
                    id=f"reddit_{post_data['id']}",
                    source=FeedbackSource.REDDIT,
                    source_url=f"https://reddit.com{post_data['permalink']}",
                    title=title,
                    text=text,
                    author=post_data.get("author"),
                    timestamp=datetime.fromtimestamp(
                        post_data["created_utc"], tz=timezone.utc
                    ),
                    score=post_data.get("score"),
                    num_comments=post_data.get("num_comments"),
                    products=extract_products(combined_text),
                    categories=extract_categories(combined_text),
                    sentiment=None,
                    collected_at=datetime.now(timezone.utc),
                    processed=False,
                )

                yield feedback
                collected += 1

        except Exception as e:
            print(f"  Error scraping r/{subreddit}: {e}")
            continue

    client.close()


# =============================================================================
# HackerNews Scraper
# =============================================================================

def scrape_hackernews(limit: int = 100) -> Iterator[Feedback]:
    """Scrape HackerNews for AI product feedback."""
    client = httpx.Client(timeout=30.0)
    base_url = "https://hacker-news.firebaseio.com/v0"
    collected = 0

    def fetch_item(item_id: int) -> dict | None:
        try:
            response = client.get(f"{base_url}/item/{item_id}.json")
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    try:
        response = client.get(f"{base_url}/newstories.json")
        response.raise_for_status()
        story_ids = response.json()[:500]

        for story_id in story_ids:
            if collected >= limit:
                break

            story = fetch_item(story_id)
            if not story:
                continue

            title = story.get("title", "")
            text = story.get("text", "")
            combined_text = f"{title}\n\n{text}"

            if is_relevant(combined_text):
                feedback = Feedback(
                    id=f"hn_story_{story['id']}",
                    source=FeedbackSource.HACKERNEWS,
                    source_url=f"https://news.ycombinator.com/item?id={story['id']}",
                    title=title,
                    text=text,
                    author=story.get("by"),
                    timestamp=datetime.fromtimestamp(story["time"], tz=timezone.utc),
                    score=story.get("score"),
                    num_comments=story.get("descendants"),
                    products=extract_products(combined_text),
                    categories=extract_categories(combined_text),
                    sentiment=None,
                    collected_at=datetime.now(timezone.utc),
                    processed=False,
                )

                yield feedback
                collected += 1

            # Check first-level comments
            if collected < limit and "kids" in story:
                for comment_id in story.get("kids", [])[:10]:
                    if collected >= limit:
                        break

                    comment = fetch_item(comment_id)
                    if not comment or "text" not in comment:
                        continue

                    comment_text = comment["text"]

                    if is_relevant(comment_text):
                        feedback = Feedback(
                            id=f"hn_comment_{comment['id']}",
                            source=FeedbackSource.HACKERNEWS,
                            source_url=f"https://news.ycombinator.com/item?id={comment['id']}",
                            title=f"Re: {title[:50]}...",
                            text=comment_text,
                            author=comment.get("by"),
                            timestamp=datetime.fromtimestamp(comment["time"], tz=timezone.utc),
                            score=None,
                            num_comments=None,
                            products=extract_products(comment_text),
                            categories=extract_categories(comment_text),
                            sentiment=None,
                            collected_at=datetime.now(timezone.utc),
                            processed=False,
                        )

                        yield feedback
                        collected += 1

    except Exception as e:
        print(f"  Error scraping HackerNews: {e}")

    client.close()


# =============================================================================
# Main collection function
# =============================================================================

def collect_feedback(limit: int = 100, output_path: Path | None = None) -> list[Feedback]:
    """Collect feedback from all sources."""
    all_feedback = []

    print("\n🔍 Scraping Reddit...")
    reddit_count = 0
    for feedback in scrape_reddit(limit=limit):
        all_feedback.append(feedback)
        reddit_count += 1
        print(f"  [{reddit_count}] {feedback.products[0].value}: {feedback.title[:60] if feedback.title else '(no title)'}...")
    print(f"  ✓ Collected {reddit_count} items from Reddit")

    print("\n🔍 Scraping HackerNews...")
    hn_count = 0
    for feedback in scrape_hackernews(limit=limit):
        all_feedback.append(feedback)
        hn_count += 1
        print(f"  [{hn_count}] {feedback.products[0].value}: {feedback.title[:60] if feedback.title else '(no title)'}...")
    print(f"  ✓ Collected {hn_count} items from HackerNews")

    print(f"\n📊 Total collected: {len(all_feedback)} items")

    if output_path:
        with output_path.open("w") as f:
            for feedback in all_feedback:
                f.write(json.dumps(feedback.to_dict()) + "\n")
        print(f"💾 Saved to {output_path}")

    return all_feedback


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Collect AI product feedback")
    parser.add_argument("--limit", type=int, default=100, help="Max items per source")
    parser.add_argument("--output", type=str, help="Output JSONL file path")
    args = parser.parse_args()

    output = Path(args.output) if args.output else None
    collect_feedback(limit=args.limit, output_path=output)
