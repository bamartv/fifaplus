import requests
import tweepy
import os

# গিটহাব সিক্রেটস থেকে API Key গুলো নেওয়া হবে
API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

# ভিআইপি টিমের লিস্ট (এদের খেলা থাকলেই শুধু টুইট হবে)
VIP_TEAMS = [
    "Real Madrid", "FC Barcelona", "Atletico Madrid", "Girona",
    "Manchester United", "Manchester City", "Liverpool", "Arsenal", "Chelsea", "Tottenham Hotspur", "Newcastle United", "Aston Villa",
    "Juventus", "Inter", "AC Milan", "Napoli", "AS Roma",
    "Bayern München", "Borussia Dortmund", "Bayer 04 Leverkusen",
    "Paris Saint-Germain", "Marseille",
    "Argentina", "Brazil", "Portugal", "France", "England", "Germany", "Spain", "Morocco",
    "Inter Miami CF", "Al-Nassr", "Al-Hilal", "Al-Ittihad",
    "Bangladesh", "India", "Pakistan", "Australia", "Afghanistan",
    "Royal Challengers Bengaluru", "Chennai Super Kings", "Mumbai Indians", "Kolkata Knight Riders", "Gujarat Titans"
]

def load_tweeted_goals():
    if not os.path.exists('tweeted_goals.txt'):
        return set()
    with open('tweeted_goals.txt', 'r') as f:
        return set(f.read().splitlines())

def save_tweeted_goal(goal_id):
    with open('tweeted_goals.txt', 'a') as f:
        f.write(f"{goal_id}\n")

def run_bot():
    print("🔄 Checking for VIP live matches and goals...")
    tweeted_goals = load_tweeted_goals()
    
    url = 'https://www.sofascore.com/api/v1/sport/football/events/live'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Cache-Control': 'no-cache'
    }

    try:
        live_res = requests.get(url, headers=headers).json()
        events = live_res.get('events', [])
        
        # Tweepy Client Setup
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )

        for match in events:
            match_id = match['id']
            home = match.get('homeTeam', {}).get('name', 'Home')
            away = match.get('awayTeam', {}).get('name', 'Away')
            
            # চেক করা হচ্ছে ম্যাচটি ভিআইপি লিস্টে আছে কি না
            if home in VIP_TEAMS or away in VIP_TEAMS:
                print(f"🎯 VIP Match Found: {home} vs {away}")
                
                inc_url = f'https://www.sofascore.com/api/v1/event/{match_id}/incidents'
                inc_res = requests.get(inc_url, headers=headers).json()
                incidents = inc_res.get('incidents', [])
                
                for inc in incidents:
                    if inc.get('incidentType') == 'goal':
                        goal_id = str(inc.get('id', f"{match_id}_{inc.get('time')}"))
                        
                        if goal_id not in tweeted_goals:
                            time_min = inc.get('time', '')
                            player = inc.get('player', {}).get('name', 'Unknown Player')
                            h_sc = inc.get('homeScore', 0)
                            a_sc = inc.get('awayScore', 0)
                            
                            tweet_text = f"🚨 GOAL!!! What a strike by {player}! 🔥\n⏱️ {time_min}' min\n\n⚽ {home} {h_sc} - {a_sc} {away}\n\n📺 Watch LIVE in HD with 0 buffering here:\n👉 https://livesportsplay.top\n\n#LiveFootball #Sports #livesportsplay"
                            
                            try:
                                client.create_tweet(text=tweet_text)
                                print(f"✅ Successfully Tweeted Goal for {home} vs {away}")
                                save_tweeted_goal(goal_id)
                                tweeted_goals.add(goal_id)
                            except Exception as e:
                                print(f"❌ Error Tweeting: {e}")
                                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_bot()
