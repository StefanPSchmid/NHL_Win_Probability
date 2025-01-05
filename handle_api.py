from typing import List, Tuple, Optional
import requests

def get_game_ids_season(season: str) -> List[int]:
    """Retrieve all regular season game IDs for a given NHL season.

    Makes API calls to the NHL web API for each team to collect all game IDs
    for regular season games (gameType = 2) in the specified season.

    Args:
        season (str): The NHL season to get games for, format: "20232024"

    Returns:
        List[int]: A list of unique game IDs for all regular season games

    Note:
        - Prints status messages about the number of unique games found
        - Regular season games are identified by gameType = 2
        - Makes separate API calls for each team to ensure complete coverage
    """

    nhl_team_abbreviations = [
        "ANA",  # Anaheim Ducks
        "ARI",  # Arizona Coyotes
        "BOS",  # Boston Bruins
        "BUF",  # Buffalo Sabres
        "CGY",  # Calgary Flames
        "CAR",  # Carolina Hurricanes
        "CHI",  # Chicago Blackhawks
        "COL",  # Colorado Avalanche
        "CBJ",  # Columbus Blue Jackets
        "DAL",  # Dallas Stars
        "DET",  # Detroit Red Wings
        "EDM",  # Edmonton Oilers
        "FLA",  # Florida Panthers
        "LAK",  # Los Angeles Kings
        "MIN",  # Minnesota Wild
        "MTL",  # Montreal Canadiens
        "NSH",  # Nashville Predators
        "NJD",  # New Jersey Devils
        "NYI",  # New York Islanders
        "NYR",  # New York Rangers
        "OTT",  # Ottawa Senators
        "PHI",  # Philadelphia Flyers
        "PIT",  # Pittsburgh Penguins
        "SJS",  # San Jose Sharks
        "SEA",  # Seattle Kraken
        "STL",  # St. Louis Blues
        "TBL",  # Tampa Bay Lightning
        "TOR",  # Toronto Maple Leafs
        "UTA",  # Utah HC
        "VAN",  # Vancouver Canucks
        "VGK",  # Vegas Golden Knights
        "WSH",  # Washington Capitals
        "WPG"   # Winnipeg Jets
    ]

    unique_game_ids = set()

    for nhl_team in nhl_team_abbreviations:

        game_ids = []

        url = f"https://api-web.nhle.com/v1/club-schedule-season/{nhl_team}/{season}"
        response = requests.get(url=url)
        if response.status_code == 200:
            data = response.json()
        else:
            print(f"Failed to retrieve data; Status Code: {response.status_code}")

        for game in data["games"]:

            if game["gameType"] == 2:
                game_ids.append(game["id"])

        unique_game_ids.update(game_ids)

        print("LENGTH UNIQUE GAME IDS: ", len(unique_game_ids), "LENGTH GAME IDS: ", len(game_ids))

    return list(unique_game_ids)

def get_game_id(home_team: str, away_team: str, date: Optional[str] = None) -> Tuple[Optional[int], Optional[bool]]:
    """Retrieve the game ID and live status for a specific NHL game.

    Makes an API call to the NHL web API to find a game matching the specified
    teams and optionally a specific date.

    Args:
        home_team (str): Abbreviation of the home team (e.g., "TOR")
        away_team (str): Abbreviation of the away team (e.g., "MTL")
        date (Optional[str], optional): Date of the game in format "YYYY-MM-DD". 
            If None, searches for live games. Defaults to None.

    Returns:
        Tuple[Optional[int], Optional[bool]]: A tuple containing:
            - game_id (Optional[int]): The ID of the matching game, or None if not found
            - is_live (Optional[bool]): Whether the game is currently live, or None if not found

    Note:
        - If date is None, searches only currently live games (i.e. from today)
        - If date is provided, searches for games on that specific date
        - Prints error message if the game cannot be found
    """

    if date is None:
        url = f"https://api-web.nhle.com/v1/score/now"
    else:
        url = f"https://api-web.nhle.com/v1/score/{date}"

    response = requests.get(url=url)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Failed to retrieve data; Status Code: {response.status_code}")

    for game in data["games"]:

        if date is None:
            if game["awayTeam"]["abbrev"] == away_team and game["homeTeam"]["abbrev"] == home_team:
                return game["id"], game["gameState"] == "LIVE"
            else:
                continue
        else:
            if game["gameDate"] == date and game["awayTeam"]["abbrev"] == away_team and game["homeTeam"]["abbrev"] == home_team:
                return game["id"], game["gameState"] == "LIVE"
            else:
                continue

    raise ValueError(f"Game with home team {home_team}, away team {away_team} on {date if date is not None else 'live'} could not be found.")