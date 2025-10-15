# MLB Playoff Calendar Generator

Automatically scrapes MLB playoff schedules and generates a subscribable Google Calendar.

## 🚀 Quick Start

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it something like `mlb-playoff-calendar`
3. Make it **Public** (required for GitHub Pages)
4. Initialize with a README

### Step 2: Add Files to Repository

Create the following files in your repository:

1. **`generate_calendar.py`** - Copy the Python script
2. **`requirements.txt`** - Copy the requirements file
3. **`.github/workflows/update_calendar.yml`** - Copy the workflow file
   - Create the `.github/workflows/` folder structure first

### Step 3: Enable GitHub Pages

1. Go to your repository Settings
2. Click on "Pages" in the left sidebar
3. Under "Source", select `main` branch
4. Click Save
5. Your site will be published at: `https://[username].github.io/[repo-name]/`

### Step 4: Run the Workflow

1. Go to the "Actions" tab in your repository
2. Click on "Update MLB Playoff Calendar" workflow
3. Click "Run workflow" to trigger it manually the first time
4. Wait for it to complete (usually 30-60 seconds)
5. The `mlb_playoffs.ics` file should now appear in your repository

### Step 5: Subscribe in Google Calendar

1. Get your calendar URL: `https://[username].github.io/[repo-name]/mlb_playoffs.ics`
   - Replace `[username]` with your GitHub username
   - Replace `[repo-name]` with your repository name

2. Open Google Calendar
3. Click the **+** next to "Other calendars"
4. Select "From URL"
5. Paste your calendar URL
6. Click "Add calendar"

**Note:** Google Calendar can take several hours to initially load the calendar and may only check for updates every 24-48 hours.

## 🔄 How It Works

- The workflow runs automatically **every day at 6 AM ET**
- It scrapes the latest playoff schedule from MLB.com
- Generates a new `.ics` calendar file
- Commits it back to the repository
- Google Calendar picks up the updates automatically

## 🎯 Manual Updates

You can manually trigger an update anytime:

1. Go to the "Actions" tab
2. Select "Update MLB Playoff Calendar"
3. Click "Run workflow"

## 🛠️ Troubleshooting

### Calendar not showing up in Google Calendar
- Make sure your repository is **Public**
- Make sure GitHub Pages is enabled
- Wait 2-4 hours for Google to initially fetch the calendar
- Try the URL directly in your browser - it should download an .ics file

### No games showing up
- Check if the playoff season has started
- View the Actions log to see if there were scraping errors
- ESPN may have changed their HTML structure (may need script updates)

### Calendar not updating
- Check the Actions tab for any failed runs
- Google Calendar typically updates subscribed calendars every 24-48 hours
- You can remove and re-add the calendar to force a refresh

## 📝 Customization

### Change update frequency
Edit `.github/workflows/update_calendar.yml` and modify the cron schedule:
```yaml
schedule:
  - cron: '0 10 * * *'  # Currently 6 AM ET daily
```

### Change calendar name or description
Edit `generate_calendar.py` and modify these lines:
```python
cal.add('x-wr-calname', 'MLB Playoffs 2024')
cal.add('x-wr-caldesc', 'MLB Playoff Schedule - Auto-updated daily')
```

### Add multiple sources
You can add additional scraping functions for MLB.com or other sources as fallbacks.

## 📋 File Structure

```
mlb-playoff-calendar/
├── .github/
│   └── workflows/
│       └── update_calendar.yml
├── generate_calendar.py
├── requirements.txt
├── mlb_playoffs.ics (generated)
└── README.md
```

## 🤝 Contributing

Feel free to fork this repository and customize it for your needs!

## 📄 License

MIT License - Feel free to use and modify as needed.
