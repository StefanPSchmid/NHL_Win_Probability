import requests
import numpy as np
from datetime import timedelta
from typing import Optional, Tuple

from NHLMarkovModel import NHLMarkovModel
from process_game import create_score_timeline

import matplotlib.pyplot as plt

def color_distances(home_color_one: str, away_color_one: str, away_color_two: str) -> bool:
    """
    Calculate and compare the weighted RGB distances between home and away team colors.
    
    Args:
        home_color_one (str): Hex color code for home team's primary color
        away_color_one (str): Hex color code for away team's first color option
        away_color_two (str): Hex color code for away team's second color option
        
    Returns:
        bool: True if the distance between home_color_one and away_color_one is less than 
              the distance between home_color_one and away_color_two
    """

    rgb1 = [int(home_color_one.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    rgb2 = [int(away_color_one.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    rgb3 = [int(away_color_two.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]

    weights = [0.3, 0.59, 0.11]
    distance1 = sum((a - b) ** 2 * w for a, b, w in zip(rgb1, rgb2, weights)) ** 0.5
    distance2 = sum((a - b) ** 2 * w for a, b, w in zip(rgb1, rgb3, weights)) ** 0.5

    return distance1 < distance2


def plot_probabilities_percent(
    x_axis: np.ndarray,
    y_axis: np.ndarray,
    home_team: Tuple[Optional[str], Optional[str], Optional[str]] = (None, None, None),
    away_team: Tuple[Optional[str], Optional[str], Optional[str]] = (None, None, None),
    time_passed: Optional[float] = None
) -> None:
    """
    Plot game outcome probabilities as a stacked area chart.
    
    Args:
        x_axis (np.ndarray): Array of time points in seconds
        y_axis (np.ndarray): 2D array of probabilities with shape (n_timepoints, 3)
                            representing away win, draw, and home win probabilities
        home_team (Tuple[Optional[str], Optional[str], Optional[str]]): Tuple containing
                 (team name, primary color, text color) for home team
        away_team (Tuple[Optional[str], Optional[str], Optional[str]]): Tuple containing
                 (team name, primary color, text color) for away team
        time_passed (Optional[float]): Current game time in seconds for live games
    """

    assert y_axis.shape[0] == len(x_axis), "x_axis and y_axis must have matching lengths."
    assert y_axis.shape[1] == 3, "y_axis must have 3 columns: away win, draw, home win probabilities."

    y_axis_percent = y_axis * 100

    labels = ['Away' if away_team[0] is None else away_team[0], 'OT', 'Home' if home_team[0] is None else home_team[0]]
    colors = ['#D3D3D3'if away_team[1] is None else away_team[1], 'white', 'black' if home_team[1] is None else home_team[1]]  # Dark blue, light grey, red

    fig = plt.figure(figsize=(12, 6))
    plt.stackplot(
        x_axis,
        y_axis_percent[:, 0],  # Away Win
        y_axis_percent[:, 1],  # Draw
        y_axis_percent[:, 2],  # Home Win
        colors=colors,
        alpha=0.8
    )

    plt.xlabel('Game Minutes', fontsize=18)
    plt.ylabel('Outcome Probability / %', fontsize=18)
    plt.text(0, 15, labels[0], fontsize=18, color='white' if away_team[2] is None else away_team[2])
    plt.text(0, 85, labels[2], fontsize=18, color='white' if home_team[2] is None else home_team[2])
    plt.text(0, 45, labels[1], fontsize=18, color='black')
    plt.ylim(0, 100)  # Percentages should always sum to 100
    plt.xlim(x_axis[0], x_axis[-1])  # Ensure the x-axis range matches the data
    major_ticks = np.arange(0, 3301, 300)
    major_labels = [str(i // 60) for i in major_ticks]  # Convert to minutes
    plt.gca().set_xticks(major_ticks)
    plt.gca().set_xticklabels(major_labels, fontsize=16)
    minor_ticks = np.arange(60, 3541, 60)
    plt.gca().set_xticks(minor_ticks, minor=True)
    major_y_ticks = np.arange(0, 101, 10)
    major_y_labels = [str(i) for i in major_y_ticks]
    minor_y_ticks = np.arange(5, 96, 5)
    plt.gca().set_yticks(major_y_ticks)
    plt.gca().set_yticklabels(major_y_labels, fontsize=16)
    plt.gca().set_yticks(minor_y_ticks, minor=True)

    if time_passed is not None:
        plt.vlines(time_passed, ymin=0, ymax=100, colors='black', linestyles='dashed', linewidth = 2.5)
        plt.text(time_passed, 55, "Live", fontsize = 18, color='black')

    plt.tight_layout()
    return fig


def plot_specific_game(game_id: str, home_team: Optional[str] = None, away_team: Optional[str] = None, live: bool = False) -> None:
    """
    Retrieve and plot win probability data for a specific NHL game.
    
    Args:
        game_id (str): NHL game identifier
        home_team (Optional[str]): Three-letter code for home team
        away_team (Optional[str]): Three-letter code for away team
        live (bool): Whether to show current game time for live games
    """

    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    response = requests.get(url=url)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Failed to retrieve data; Status Code: {response.status_code}")

    goals_state, situations_state, location_state = create_score_timeline(plays=data['plays'])

    time_passed = None
    if live:
        last_play = data['plays'][-1]
        time_passed = 20 * 60 * (last_play['periodDescriptor']['number'] - 1) + timedelta(minutes=int(last_play['timeInPeriod'].split(':')[0]), seconds=int(last_play['timeInPeriod'].split(':')[1])).total_seconds()

    x_axis = []
    y_axis = []
    model = NHLMarkovModel.load('NHL_Markov_Model_home.pkl')

    for n in range(0, goals_state.shape[0]):

        trajectories = model.propagate(goals_state[n], situations_state[n], location_state[n], max(360 - 1 - n, 0))
        x_axis.append(n * 10)
        y_axis.append([np.sum(trajectories[0:342]), np.sum(trajectories[342:342+57]), np.sum(trajectories[342+57:741])]) # away win, draw, home win

    x_axis = np.array(x_axis)
    y_axis = np.array(y_axis)

    if home_team is None or away_team is None:
        fig = plot_probabilities_percent(x_axis=x_axis, y_axis=y_axis, time_passed=time_passed)
    else:
        home_color_one, home_color_two, away_color_one, away_color_two = get_team_colors(home_team=home_team, away_team=away_team)
        fig = plot_probabilities_percent(x_axis=x_axis, y_axis=y_axis, home_team=(home_team, home_color_one, home_color_two), away_team=(away_team, away_color_one, away_color_two), time_passed=time_passed)
    return fig

def get_team_colors(home_team: str, away_team: str) -> Tuple[str, str, str, str]:
    """
    Get the primary and secondary colors for home and away teams.
    
    Args:
        home_team (str): Three-letter code for home team
        away_team (str): Three-letter code for away team
        
    Returns:
        Tuple[str, str, str, str]: Tuple containing (home_primary, home_secondary,
                                  away_primary, away_secondary) colors as hex codes
    """
    team_colors = {
        "ANA": ('#F47A38', '#B9975B'),
        "ARI": ('#8C2633', '#E2D6B5'),
        "BOS": ('#FFB81C', '#000000'),
        "BUF": ('#003087', '#FFB81C'),
        "CGY": ('#D2001C', '#FAAF19'),
        "CAR": ('#CE1126', '#FFFFFF'),
        "CHI": ('#CF0A2C', '#FF671B'),
        "COL": ('#6F263D', '#236192'),
        "CBJ": ('#002654', '#CE1126'),
        "DAL": ('#006847', '#8F8F8C'),
        "DET": ('#CE1126', '#FFFFFF'),
        "EDM": ('#041E42', '#FF4C00'),
        "FLA": ('#041E42', '#C8102E'),
        "LAK": ('#111111', '#A2AAAD'),
        "MIN": ('#A6192E', '#154734'),
        "MTL": ('#AF1E2D', '#192168'),
        "NSH": ('#FFB81C', '#041E42'),
        "NJD": ('#CE1126', '#000000'),
        "NYI": ('#00539B', '#F47D30'),
        "NYR": ('#0038A8', '#CE1126'),
        "OTT": ('#000000', '#DA1A32'),
        "PHI": ('#F74902', '#000000'),
        "PIT": ('#000000', '#CFC493'),
        "STL": ('#002F87', '#FCB514'),
        "SJS": ('#006D75', '#EA7200'),
        "SEA": ('#001628', '#99D9D9'),
        "TBL": ('#002868', '#FFFFFF'),
        "TOR": ('#00205B', '#FFFFFF'),
        "UTA": ('#71AFE5','#090909'),
        "VAN": ('#00205B', '#00843D'),
        "VGK": ('#B4975A', '#333F42'),
        "WSH": ('#041E42', '#C8102E'),
        "WPG": ('#041E42', '#AC162C')
    }
    if home_team not in team_colors.keys() or away_team not in team_colors.keys():
        raise ValueError("Home team or away team could not be identified. Please make sure the three-letter codes are correct.")

    if (not team_colors[away_team][1] == '#FFFFFF') and color_distances(team_colors[home_team][0], team_colors[away_team][0], team_colors[away_team][1]):
        return team_colors[home_team][0], team_colors[home_team][1], team_colors[away_team][1], team_colors[away_team][0]
    else:
        return team_colors[home_team][0], team_colors[home_team][1], team_colors[away_team][0], team_colors[away_team][1]