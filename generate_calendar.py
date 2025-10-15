import requests
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event
import re
from bs4 import BeautifulSoup

def scrape_espn_playoff_story():
    """Scrape MLB playoff schedule from ESPN's playoff story page"""
    url = "https://www.espn.com/mlb/story/_/id/46409722/2025-mlb-playoffs-word-series-schedule-how-watch-postseason-bracket-standings"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        games = []
        
        # Extract text content and parse games
        content = soup.get_text()
        
        # Find game entries with pattern: "Day at/vs Team, Time (TV)"
        # Examples: "Game 1: Tuesday at 1:08 p.m. (ESPN)"
        game_pattern = r'Game\s+\d+:?\s+([A-Za-z]+)\s+at\s+(\d{1,2}):(\d{2})\s+([ap]\.m\.)'
        matches = re.finditer(game_pattern, content, re.IGNORECASE)
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Determine the year for games
        # If we're in October or later, playoff games are in the current year
        # Otherwise they're in the next year
        playoff_year = current_year if current_month >= 10 else current_year + 1
        
        # Map day names to dates
        day_map = {}
        today = datetime.now()
        for i in range(60):  # Look ahead 60 days
            future_date = today + timedelta(days=i)
            day_name = future_date.strftime('%A')
            if day_name not in day_map:
                day_map[day_name] = future_date
        
        # Find matchup information
        matchup_pattern = r'([A-Za-z\s]+)\s+(?:at|vs\.?)\s+([A-Za-z\s]+)'
        matchups = []
        
        for match in matches:
            day_name = match.group(1)
            hour = int(match.group(2))
            minute = int(match.group(3))
            ampm = match.group(4).lower().replace('.', '')
            
            if day_name in day_map:
                game_date = day_map[day_name]
                
                # Convert to 24-hour
                if 'pm' in ampm and hour != 12:
                    hour += 12
                elif 'am' in ampm and hour == 12:
                    hour = 0
                
                # Create datetime
                et_tz = pytz.timezone('America/New_York')
                game_datetime = game_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                game_datetime = et_tz.localize(game_datetime)
                
                # Try to extract matchup near this game time
                # For now, use generic placeholder
                games.append({
                    'away_team': 'TBD',
                    'home_team': 'TBD',
                    'datetime': game_datetime,
                    'description': 'MLB Playoff Game'
                })
        
        # Also try to extract specific matchups from the page
        # Look for patterns like "Tigers at Guardians", "Red Sox at Yankees", etc.
        team_matchup_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:at|vs\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        team_matches = re.finditer(team_matchup_pattern, content)
        
        matchup_list = []
        for tm in team_matches:
            away = tm.group(1).strip()
            home = tm.group(2).strip()
            # Filter out non-team names
            if len(away.split()) <= 3 and len(home.split()) <= 3:
                if away not in ['Game', 'Best', 'American', 'National', 'All'] and home not in ['Game', 'Best', 'American', 'National', 'All']:
                    matchup_list.append((away, home))
        
        # Try to match games with matchups
        if matchup_list and games:
            matchup_idx = 0
            for game in games:
                if matchup_idx < len(matchup_list):
                    game['away_team'] = matchup_list[matchup_idx][0]
                    game['home_team'] = matchup_list[matchup_idx][1]
                    game['description'] = f"{matchup_list[matchup_idx][0]} at {matchup_list[matchup_idx][1]}"
                    matchup_idx += 1
        
        return games
    
    except Exception as e:
        print(f"Error scraping ESPN: {e}")
        import traceback
        traceback.print_exc()
        return []

def create_ical_calendar(games):
    """Create iCalendar file from games"""
    cal = Calendar()
    cal.add('prodid', '-//MLB Playoff Calendar//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'MLB Playoffs 2025')
    cal.add('x-wr-timezone', 'America/New_York')
    cal.add('x-wr-caldesc', 'MLB Playoff Schedule - Auto-updated daily')
    
    for game in games:
        if not game.get('datetime'):
            continue
            
        event = Event()
        
        # Create title
        away = game.get('away_team', 'TBD')
        home = game.get('home_team', 'TBD')
        title = f"{away} @ {home}" if away != 'TBD' and home != 'TBD' else "MLB Playoff Game"
        event.add('summary', title)
        
        # Add start time
        event.add('dtstart', game['datetime'])
        
        # Add end time (assume 3.5 hours for baseball games)
        event.add('dtend', game['datetime'] + timedelta(hours=3, minutes=30))
        
        # Add description
        description = game.get('description', f"MLB Playoff Game\n{away} at {home}")
        event.add('description', description)
        
        # Add location
        location = f"{home} Stadium" if home != 'TBD' else "TBD"
        event.add('location', location)
        
        # Create unique ID
        uid = f"{game['datetime'].strftime('%Y%m%d%H%M')}-{away}-{home}@mlb-playoffs"
        event.add('uid', uid)
        
        # Add timestamp
        event.add('dtstamp', datetime.now(pytz.UTC))
        
        cal.add_component(event)
    
    return cal

def main():
    print("Scraping MLB playoff schedule from ESPN...")
    games = scrape_espn_playoff_story()
    
    print(f"Found {len(games)} games")
    
    if games:
        print("\nCreating calendar file...")
        cal = create_ical_calendar(games)
        
        # Write to file
        with open('mlb_playoffs.ics', 'wb') as f:
            f.write(cal.to_ical())
        
        print("Calendar file created: mlb_playoffs.ics")
        print("\nGames found:")
        for game in games[:10]:  # Show first 10
            if game.get('datetime'):
                print(f"  {game['datetime'].strftime('%Y-%m-%d %I:%M %p ET')}: {game.get('away_team', 'TBD')} @ {game.get('home_team', 'TBD')}")
    else:
        print("No games found. The season may be over or there's an issue with scraping.")

if __name__ == "__main__":
    main()
