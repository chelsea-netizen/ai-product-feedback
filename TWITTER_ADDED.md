# ✅ Twitter Support Added!

Twitter/X data collection is now available for your AI Product Feedback Tracker!

## 🎉 What's New

- ✅ Twitter scraper created
- ✅ CLI updated to support `--sources twitter`
- ✅ Searches for tweets about AI products + UX topics
- ✅ Setup guide created

## 🚀 How to Enable Twitter

### Quick Start:

1. **Get Twitter API access** (free, takes ~15 minutes):
   - Go to: https://developer.twitter.com/en/portal/dashboard
   - Sign up for free API access
   - Create an app
   - Copy your Bearer Token

2. **Set the token**:
   ```bash
   export TWITTER_BEARER_TOKEN="your_token_here"
   ```

3. **Collect from Twitter**:
   ```bash
   fa run -m sandbox.chelsea.ai_product_feedback.cli collect \
       --sources twitter \
       --limit 50 \
       --no-save \
       --output ~/Desktop/twitter_feedback.jsonl
   ```

4. **Include in daily collection**:
   Edit `daily_collect.sh` to add `twitter` to the sources.

## 📚 Full Setup Guide

See: `sandbox/sandbox/chelsea/ai_product_feedback/TWITTER_SETUP.md`

## 💰 Free Tier Limits

- 500,000 tweets/month
- You'll use ~3,000/month (100/day)
- Plenty of headroom!

## 🔍 What It Searches

Twitter scraper searches for:
- "claude ux"
- "chatgpt interface"
- "gemini error"
- "copilot confusing"
- And more...

Only collects tweets mentioning both:
1. An AI product
2. UX/content topics

## 📊 Example Output

After enabling, you'll see tweets like:
- "Claude's error messages are so much clearer than ChatGPT"
- "Gemini's interface is confusing when switching models"
- "Why does Copilot's UI hide the settings?"

Perfect for tracking real-time UX feedback!

## ⚡ Next Steps

1. Follow setup guide to get Twitter API token
2. Test collection with Twitter
3. Update daily script to include Twitter
4. Watch your dashboard fill with Twitter feedback!

---

**Questions?** Check `TWITTER_SETUP.md` for troubleshooting!
