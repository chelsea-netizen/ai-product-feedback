#!/usr/bin/env python3
"""Generate an HN-style HTML view of collected feedback."""

import json
from datetime import datetime
from pathlib import Path

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Product Feedback</title>
    <style>
        body {{
            font-family: Verdana, Geneva, sans-serif;
            font-size: 10pt;
            color: #828282;
            background-color: #f6f6ef;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 85%;
            max-width: 1200px;
            margin: 0 auto;
            background-color: #f6f6ef;
        }}
        .header {{
            background-color: #ff6600;
            padding: 2px;
            margin-bottom: 10px;
        }}
        .header h1 {{
            margin: 0;
            padding: 6px;
            font-size: 12pt;
            font-weight: bold;
            color: black;
        }}
        .filters {{
            background-color: white;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #828282;
        }}
        .item {{
            padding: 3px 0;
            margin-bottom: 5px;
        }}
        .title {{
            line-height: 12pt;
        }}
        .title a {{
            color: #000;
            text-decoration: none;
        }}
        .title a:visited {{
            color: #828282;
        }}
        .title a:hover {{
            text-decoration: underline;
        }}
        .meta {{
            font-size: 8pt;
            color: #828282;
            padding-left: 20px;
        }}
        .meta a {{
            color: #828282;
            text-decoration: none;
        }}
        .meta a:hover {{
            text-decoration: underline;
        }}
        .text {{
            font-size: 9pt;
            color: #000;
            padding: 5px 20px;
            margin-top: 5px;
            line-height: 14pt;
            max-width: 800px;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 6px;
            margin-right: 4px;
            font-size: 8pt;
            border-radius: 3px;
            font-weight: bold;
        }}
        .badge-claude {{ background-color: #d4a574; color: white; }}
        .badge-chatgpt {{ background-color: #10a37f; color: white; }}
        .badge-gemini {{ background-color: #4285f4; color: white; }}
        .badge-copilot {{ background-color: #6e40c9; color: white; }}
        .badge-perplexity {{ background-color: #4a9eff; color: white; }}
        .badge-grok {{ background-color: #000; color: white; }}
        .badge-unknown {{ background-color: #999; color: white; }}
        .badge-reddit {{ background-color: #ff4500; color: white; }}
        .badge-hackernews {{ background-color: #ff6600; color: white; }}
        .category {{
            font-size: 8pt;
            color: #666;
            font-style: italic;
        }}
        .stats {{
            background-color: white;
            padding: 10px;
            margin: 20px 0;
            border: 1px solid #828282;
        }}
        .stats h3 {{
            margin-top: 0;
            color: #000;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Product Feedback Tracker</h1>
        </div>

        <div class="stats">
            <h3>Overview</h3>
            <p>
                <strong>{total_items}</strong> items collected |
                Last updated: {last_updated}
            </p>
        </div>

        {items_html}

        <div style="padding: 20px; text-align: center; color: #828282; font-size: 8pt;">
            Generated from AI Product Feedback Collection System
        </div>
    </div>
</body>
</html>
"""


def get_product_badges(products: list[str]) -> str:
    """Generate HTML badges for products."""
    badges = []
    for product in products:
        badges.append(f'<span class="badge badge-{product}">{product}</span>')
    return " ".join(badges)


def get_source_badge(source: str) -> str:
    """Generate HTML badge for source."""
    return f'<span class="badge badge-{source}">{source}</span>'


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def generate_html(input_file: Path, output_file: Path, show_text: bool = True) -> None:
    """Generate an HN-style HTML view of feedback."""
    # Load feedback
    feedbacks = []
    with input_file.open() as f:
        for line in f:
            if line.strip():
                feedbacks.append(json.loads(line))

    # Sort by timestamp (newest first)
    feedbacks.sort(key=lambda x: x["timestamp"], reverse=True)

    # Generate HTML for each item
    items_html = []
    for i, feedback in enumerate(feedbacks, 1):
        timestamp = datetime.fromisoformat(feedback["timestamp"])
        time_str = timestamp.strftime("%Y-%m-%d %H:%M")

        title = escape_html(feedback["title"] or "(no title)")
        url = feedback["source_url"]

        product_badges = get_product_badges(feedback["products"])
        source_badge = get_source_badge(feedback["source"])
        categories = ", ".join(feedback["categories"])

        text_html = ""
        if show_text and feedback["text"]:
            text_preview = escape_html(truncate_text(feedback["text"], 400))
            text_html = f'<div class="text">{text_preview}</div>'

        score_str = (
            f"{feedback['score']} points"
            if feedback["score"] is not None
            else "0 points"
        )
        comments_str = (
            f"{feedback['num_comments']} comments"
            if feedback["num_comments"] is not None
            else "0 comments"
        )

        item_html = f"""
        <div class="item">
            <div class="title">
                {i}. <a href="{url}" target="_blank">{title}</a>
            </div>
            <div class="meta">
                {product_badges} {source_badge} |
                {score_str} | {comments_str} |
                {time_str} |
                <span class="category">{categories}</span>
            </div>
            {text_html}
        </div>
        """
        items_html.append(item_html)

    # Generate final HTML
    html = HTML_TEMPLATE.format(
        total_items=len(feedbacks),
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"),
        items_html="\n".join(items_html),
    )

    # Write to file
    output_file.write_text(html)
    print(f"✓ Generated HTML: {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate HTML from feedback JSONL")
    parser.add_argument("input", type=str, help="Input JSONL file")
    parser.add_argument("--output", type=str, help="Output HTML file")
    parser.add_argument("--no-text", action="store_true", help="Hide preview text")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_suffix(".html")

    generate_html(input_path, output_path, show_text=not args.no_text)
