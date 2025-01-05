from handle_api import get_game_id
from plot_win_probability import plot_specific_game

if __name__ == "__main__":

    home_team = "TOR"
    away_team = "BOS"
    date = "2025-01-04"


    game_id, live = get_game_id(home_team=home_team, away_team=away_team, date = date)
    plot_specific_game(game_id=game_id, home_team=home_team, away_team=away_team, live=live)