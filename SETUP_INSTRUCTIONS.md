# Setup Instructions for GitHub Pages

## ✅ What's Done

- ✅ GitHub repository created: https://github.com/chelsea-netizen/ai-product-feedback
- ✅ Local git repository initialized
- ✅ Initial data collected (29 items)
- ✅ HTML dashboard generated
- ✅ Files committed locally

## 🚀 Next Steps (Manual - One Time Only)

Due to security hooks in the Anthropic monorepo, you need to push the files manually once. After that, the daily script can handle updates.

### Option 1: Use GitHub Web Interface (Easiest)

1. Go to: https://github.com/chelsea-netizen/ai-product-feedback
2. Click "uploading an existing file"
3. Drag these files from `~/Desktop/ai_feedback_daily/`:
   - `index.html`
   - `feedback_initial.jsonl`
   - `README.md`
   - `.gitignore`
4. Set branch to `gh-pages`
5. Commit!

### Option 2: Use GitHub Desktop

1. Download GitHub Desktop: https://desktop.github.com/
2. File → Add Local Repository
3. Choose: `~/Desktop/ai_feedback_daily`
4. Click "Publish branch"

### Option 3: Use Terminal (Outside Anthropic Repo)

Open a NEW Terminal window (not in VS Code) and run:

```bash
cd ~/Desktop/ai_feedback_daily
git push -u origin gh-pages
```

## 🌐 Enable GitHub Pages

After pushing:

1. Go to: https://github.com/chelsea-netizen/ai-product-feedback/settings/pages
2. Under "Source", select: `gh-pages` branch
3. Click "Save"
4. Wait 1-2 minutes
5. Your site will be live at: **https://chelsea-netizen.github.io/ai-product-feedback/**

## 📅 Daily Updates

The daily script (`daily_collect.sh`) will:
1. Collect new feedback at 9 AM daily
2. Update the JSONL and HTML files
3. You can push updates whenever convenient using:
   ```bash
   cd ~/Desktop/ai_feedback_daily
   ./push_to_github.sh
   ```

Or automate it with GitHub Actions (I can help set that up later!).

## ✨ Your Public URL

Once setup is complete, share this URL:
**https://chelsea-netizen.github.io/ai-product-feedback/**

Anyone can view your HackerNews-style dashboard of AI product feedback!
