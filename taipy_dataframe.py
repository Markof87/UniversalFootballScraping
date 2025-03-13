from taipy.gui import Gui
import soccerdata as sd
import pandas as pd
import datetime

clubelo = sd.ClubElo()
clubelo_available = clubelo.read_by_date()

pd.set_option('display.max_columns', None)
df = pd.DataFrame(clubelo_available)
df = df.reset_index()

page = """
<|{df[['team', 'country', 'level', 'elo']]}|table|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Dynamic chart", use_reloader=True)