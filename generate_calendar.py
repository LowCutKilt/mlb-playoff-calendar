import requests
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event
import re
from bs4 import BeautifulSoup

def scrape_espn_schedule():
    """Scrape MLB playoff schedule from ESPN"""
    url = "https://www.espn.com/mlb/schedule/_/seasontype/3"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        games = []
        
        # Find all game containers
        schedule_tables = soup.find_all('div', class_='ScheduleTables')
        
        for table in schedule_tables:
            # Get date header
            date_header = table.find('div', class_='Table__Title')
            if not date_header:
                continue
                
            date_text = date_header.get_text(strip=True)
            
            # Parse date
            game_date = parse_espn_date(date_text)
            if not game_date:
                continue
            
            # Find all games for this date
            rows = table.find_all('tr', class_='Table__TR')
            
            for row in rows:
                try:
                    # Get teams
                    teams = row.find_all('span', class_='Table__Team')
                    if len(teams) < 2:
                        continue
                    
                    away_team = teams[0].get_text(strip=True)
                    home_team = teams[1].get_text(strip=True)
                    
                    # Get time
                    time_elem = row.find('td', class_='date__col')
                    if time_elem:
                        time_text = time_elem.get_text(strip=True)
                        game_time = parse_time(time_text, game_date)
                        
                        if game_time:
                            games.append({
                                'away_team': away_team,
                                'home_team': home_team,
                                'datetime': game_time,
                                'date_str': date_text
                            })
                except Exception as e:
                    print(f"Error parsing game row: {e}")
                    continue
        
        return games
    
    except Exception as e:
        print(f"Error scraping ESPN: {e}")
        return []

def parse_espn_date(date_text):
    """Parse ESPN date format"""
    try:
        # Remove day of week if present
        date_text = re.sub(r'^[A-Za-z]+,\s*', '', date_text)
        
        # Try parsing different formats
        for fmt in ['%B %d, %Y', '%A, %B %d', '%B %d']:
            try:
                parsed = datetime.strptime(date_text, fmt)
                # If year not specified, use current year or next year for playoffs
                if fmt == '%B %d' or fmt == '%A, %B %d':
                    current_year = datetime.now().year
                    # Playoffs are in October, so if we're before October, use current year
                    # Otherwise use next year if month is before October
                    parsed = parsed.replace(year=current_year)
                    if parsed.month < 10 and datetime.now().month >= 10:
                        parsed = parsed.replace(year=current_year + 1)
                return parsed
            except ValueError:
                continue
        return None
    except Exception as e:
        print(f"Error parsing date {date_text}: {e}")
        return None

def parse_time(time_text, game_date):
    """Parse time and combine with date"""
    try:
        # Handle TBD/postponed
        if 'TBD' in time_text or 'PPD' in time_text:
            return None
        
        # Extract time (e.g., "7:08 PM ET")
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)\s*ET', time_text)
        if not time_match:
            return None
        
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        ampm = time_match.group(3)
        
        # Convert to 24-hour
        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0
        
        # Combine date and time
        et_tz = pytz.timezone('America/New_York')
        game_datetime = game_date.replace(hour=hour, minute=minute)
        game_datetime = et_tz.localize(game_datetime)
        
        return game_datetime
    
    except Exception as e:
        print(f"Error parsing time {time_text}: {e}")
        return None

def create_ical_calendar(games):
    """Create iCalendar file from games"""
    cal = Calendar()
    cal.add('prodid', '-//MLB Playoff Calendar//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'MLB Playoffs 2024')
    cal.add('x-wr-timezone', 'America/New_York')
    cal.add('x-wr-caldesc', 'MLB Playoff Schedule - Auto-updated daily')
    
    for game in games:
        if not game.get('datetime'):
            continue
            
        event = Event()
        
        # Create title
        title = f"{game['away_team']} @ {game['home_team']}"
        event.add('summary', title)
        
        # Add start time
        event.add('dtstart', game['datetime'])
        
        # Add end time (assume 3.5 hours for baseball games)
        event.add('dtend', game['datetime'] + timedelta(hours=3, minutes=30))
        
        # Add description
        description = f"MLB Playoff Game\n{game['away_team']} at {game['home_team']}"
        event.add('description', description)
        
        # Add location
        event.add('location', f"{game['home_team']} Stadium")
        
        # Create unique ID
        uid = f"{game['datetime'].strftime('%Y%m%d%H%M')}-{game['away_team']}-{game['home_team']}@mlb-playoffs"
        event.add('uid', uid)
        
        # Add timestamp
        event.add('dtstamp', datetime.now(pytz.UTC))
        
        cal.add_component(event)
    
    return cal

def main():
    print("Scraping MLB playoff schedule from ESPN...")
    games = scrape_espn_schedule()
    
    print(f"Found {len(games)} games")
    
    if games:
        print("\nCreating calendar file...")
        cal = create_ical_calendar(games)
        
        # Write to file
        with open('mlb_playoffs.ics', 'wb') as f:
            f.write(cal.to_ical())
        
        print("Calendar file created: mlb_playoffs.ics")
        print("\nGames found:")
        for game in games[:5]:  # Show first 5
            if game.get('datetime'):
                print(f"  {game['datetime'].strftime('%Y-%m-%d %I:%M %p ET')}: {game['away_team']} @ {game['home_team']}")
    else:
        print("No games found. The season may be over or there's an issue with scraping.")

if __name__ == "__main__":
    main()
