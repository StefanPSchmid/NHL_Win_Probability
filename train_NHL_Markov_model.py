import requests
from typing import Sequence
import numpy as np
from NHLMarkovModel import NHLMarkovModel

from process_game import create_score_timeline
from handle_api import get_game_ids_season

def get_all_game_ids(seasons: Sequence[str] = ["20212022", "20222023", "20232024"]):

    """
    Gets all regular season game IDs for specified seasons.
    """

    game_ids = []

    for season in seasons:
        game_ids.extend(get_game_ids_season(season=season))
    
    return game_ids

def train_Markov_Model(game_ids: Sequence[str], save_name: str):
    """
    Trains a Markov Model based on specified games and saves the model.
    """
    model = NHLMarkovModel()

    for n, game in enumerate(game_ids):
        print(f"Processing game {n}")

        url = f"https://api-web.nhle.com/v1/gamecenter/{game}/play-by-play"

        response = requests.get(url=url)

        if response.status_code == 200:
            data = response.json()
        else:
            print(f"Failed to retrieve data; Status Code: {response.status_code}")

        goals_state, situations_state, location_state = create_score_timeline(plays=data['plays'])
        model.update_transitions(goals=goals_state, situations=situations_state, locations=location_state)

    model.normalize()
    model.save(save_name)

if __name__ == "__main__":

    seasons = ["20212022", "20222023", "20232024"]
    game_ids = get_all_game_ids(seasons=seasons)
    train_Markov_Model(game_ids=game_ids, save_name='NHL_Markov_Model_all_situation.pkl')