#!/usr/bin/env python3
"""Main collection script - runs daily to collect feedback and generate HTML."""

from datetime import datetime
from pathlib import Path

from scraper import collect_feedback
from generate_html import generate_html


def main() -> None:
    """Run daily collection and HTML generation."""
    output_dir = Path(__file__).parent
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date = datetime.now().strftime("%Y-%m-%d")

    print("=" * 60)
    print("AI Product Feedback - Daily Collection")
    print(f"Date: {date}")
    print("=" * 60)

    # Collect feedback
    output_file = output_dir / f"feedback_{timestamp}.jsonl"
    feedback = collect_feedback(limit=100, output_path=output_file)

    if not feedback:
        print("\n⚠️  No feedback collected today")
        return

    # Append to cumulative file
    cumulative_file = output_dir / "feedback_all.jsonl"
    print(f"\n📝 Appending {len(feedback)} items to cumulative file...")

    # Read existing IDs to avoid duplicates
    existing_ids = set()
    if cumulative_file.exists():
        with cumulative_file.open() as f:
            import json
            for line in f:
                if line.strip():
                    try:
                        item = json.loads(line)
                        existing_ids.add(item["id"])
                    except json.JSONDecodeError:
                        continue

    # Append only new items
    new_count = 0
    with cumulative_file.open("a") as f:
        import json
        for item in feedback:
            if item.id not in existing_ids:
                f.write(json.dumps(item.to_dict()) + "\n")
                new_count += 1

    print(f"  ✓ Added {new_count} new items (skipped {len(feedback) - new_count} duplicates)")

    # Generate main HTML
    print("\n🎨 Generating HTML views...")
    generate_html(cumulative_file, output_dir / "index.html")

    # Generate today's HTML
    generate_html(output_file, output_dir / f"today_{date}.html")

    # Stats
    print("\n" + "=" * 60)
    print("📊 Collection Complete!")
    print("=" * 60)

    total_lines = sum(1 for _ in cumulative_file.open())
    print(f"  Total items (all time): {total_lines}")
    print(f"  New items today: {new_count}")
    print(f"\n📁 Files:")
    print(f"  - Today's data: {output_file}")
    print(f"  - All data: {cumulative_file}")
    print(f"  - Main HTML: {output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
