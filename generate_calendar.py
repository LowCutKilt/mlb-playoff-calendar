import requests
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event
import json

def scrape_mlb_api():
    """Scrape MLB playoff schedule from MLB's official API"""
    
    try:
        current_year = datetime.now().year
        games = []
        
        # Try multiple game types for playoffs
        # F = Postseason (all rounds)
        # D = Division Series
        # L = League Championship
        # W = World Series
        game_types = ['F', 'D', 'L', 'W']
        
        for game_type in game_types:
            url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&season={current_year}&gameType={game_type}&hydrate=team,venue"
            
            print(f"Fetching from MLB API (type {game_type}): {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse the schedule data
            if 'dates' in data:
                for date_entry in data['dates']:
                    for game in date_entry.get('games', []):
                        try:
                            # Get game time
                            game_time_str = game.get('gameDate')
                            if not game_time_str:
                                continue
                            
                            # Parse ISO format time
                            game_time = datetime.strptime(game_time_str, '%Y-%m-%dT%H:%M:%SZ')
                            game_time = pytz.UTC.localize(game_time)
                            
                            # Convert to ET
                            et_tz = pytz.timezone('America/New_York')
                            game_time_et = game_time.astimezone(et_tz)
                            
                            # Get team info
                            away_team = game.get('teams', {}).get('away', {}).get('team', {}).get('name', 'TBD')
                            home_team = game.get('teams', {}).get('home', {}).get('team', {}).get('name', 'TBD')
                            
                            # Get venue
                            venue = game.get('venue', {}).get('name', 'TBD')
                            
                            # Get series description
                            series_desc = game.get('seriesDescription', 'MLB Playoffs')
                            game_number = game.get('seriesGameNumber', '')
                            
                            # Get game ID to avoid duplicates
                            game_id = game.get('gamePk', '')
                            
                            # Check if already added
                            if not any(g.get('game_id') == game_id for g in games):
                                games.append({
                                    'game_id': game_id,
                                    'away_team': away_team,
                                    'home_team': home_team,
                                    'datetime': game_time_et,
                                    'venue': venue,
                                    'series': series_desc,
                                    'game_number': game_number,
                                    'status': game.get('status', {}).get('detailedState', '')
                                })
                        except Exception as e:
                            print(f"Error parsing game: {e}")
                            continue
        
        # Sort by datetime
        games.sort(key=lambda x: x['datetime'])
        
        return games
    
    except Exception as e:
        print(f"Error fetching from MLB API: {e}")
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
    cal.add('x-wr-caldesc', 'MLB Playoff Schedule - Auto-updated daily from MLB.com')
    
    for game in games:
        if not game.get('datetime'):
            continue
            
        event = Event()
        
        # Create title with series info
        away = game.get('away_team', 'TBD')
        home = game.get('home_team', 'TBD')
        series = game.get('series', '')
        game_num = game.get('game_number', '')
        
        if series and game_num:
            title = f"{series} Game {game_num}: {away} @ {home}"
        else:
            title = f"{away} @ {home}"
        
        event.add('summary', title)
        
        # Add start time
        event.add('dtstart', game['datetime'])
        
        # Add end time (assume 3.5 hours for baseball games)
        event.add('dtend', game['datetime'] + timedelta(hours=3, minutes=30))
        
        # Add description
        status = game.get('status', '')
        description = f"{series}\n{away} at {home}"
        if status:
            description += f"\nStatus: {status}"
        event.add('description', description)
        
        # Add location
        venue = game.get('venue', f"{home} Stadium")
        event.add('location', venue)
        
        # Create unique ID using game_id
        game_id = game.get('game_id', game['datetime'].strftime('%Y%m%d%H%M'))
        uid = f"{game_id}-{away}-{home}@mlb-playoffs"
        event.add('uid', uid)
        
        # Add timestamp
        event.add('dtstamp', datetime.now(pytz.UTC))
        
        cal.add_component(event)
    
    return cal

def main():
    print("Fetching MLB playoff schedule from MLB.com API...")
    games = scrape_mlb_api()
    
    print(f"Found {len(games)} games")
    
    if games:
        print("\nCreating calendar file...")
        cal = create_ical_calendar(games)
        
        # Write to file
        with open('mlb_playoffs.ics', 'wb') as f:
            f.write(cal.to_ical())
        
        print("Calendar file created: mlb_playoffs.ics")
        print("\nGames found:")
        for game in games[:15]:  # Show first 15
            if game.get('datetime'):
                series = game.get('series', 'Playoff')
                status = game.get('status', '')
                print(f"  {game['datetime'].strftime('%Y-%m-%d %I:%M %p ET')}: {series} - {game.get('away_team', 'TBD')} @ {game.get('home_team', 'TBD')} ({status})")
    else:
        print("No games found. The playoffs may not have started yet or may be over.")

if __name__ == "__main__":
    main()
