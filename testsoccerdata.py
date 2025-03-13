import soccerdata as sd
import pandas as pd

fbref = sd.FBref()
clubelo = sd.ClubElo()
#whoscored = sd.WhoScored()
sofascore = sd.Sofascore("ITA-Serie A", "2425")
espn = sd.ESPN("ITA-Serie A")
fotmob = sd.FotMob("ITA-Serie A", '2425')
matchhistory = sd.MatchHistory("ITA-Serie A", '2425')
understat = sd.Understat("ENG-Premier League", "2425")

# Create scraper class instance filtering on specific leagues and seasons
# Retrieve data for the specified leagues and seasons
#season_stats = fbref.read_team_season_stats(stat_type='shooting')
#season = sd.FBref().read_seasons(False)

#whoscored_available = whoscored.read_player_match_stats()
#sofascore_available = sofascore.read_schedule()
#espn_available = espn.read_matchsheet(554576)
clubelo_available = clubelo.read_by_date()
#fotmob_available = fotmob.read_team_match_stats()
#matchhistory_available = matchhistory.read_games()
#understat_available = understat.read_shot_events()

pd.set_option('display.max_columns', None)
df = pd.DataFrame(clubelo_available)
df.to_csv('dataframe_output.csv', index=True)

print(df)

#print(season_stats)

#print(sd.FBref.available_leagues())