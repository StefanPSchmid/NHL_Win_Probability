from typing import List, Dict, Tuple
import numpy as np
from datetime import timedelta

def create_score_timeline(plays: List[Dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create timeline arrays for game state tracking from play-by-play data.
    
    Args:
        plays (List[Dict]): List of play-by-play events, where each play is a dictionary
                           containing event details including period, time, score, and situation
    
    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: Three arrays containing:
            - goals_timeline: Integer array of score differentials (-6 to 6)
            - situations_timeline: Integer array of situation codes
            - location_last_plays_timeline: String array of zone codes ('O', 'D', 'N')
            
    Note:
        - Timeline arrays have length 360 (one entry per 10-second interval in regulation)
        - Only processes plays from regulation time periods
        - Score differential is clipped to range [-6, 6]
        - Zone codes: 'O' (offensive), 'D' (defensive), 'N' (neutral)
    """

    relevant_situation_codes = ['0641', '1460',
                                '0651', '1560',
                                '1541', '1451',
                                '1551',
                                '1550', '0551', 
                                '1531', '1351',
                                '0541', '1450',
                                '0531', '1350',
                                '1441',
                                '1431', '1341',
                                '1331']

    goals = [{'time_left': 360, 'score_diff': 0}]
    situations = [{'time_left': 360, 'situationCode': 1551}]
    location_last_plays = [{'time_left': 360, 'zoneCode': 'N'}]

    for play in plays:
        if not play['periodDescriptor']['periodType'] == 'REG':
            continue

        if play['typeCode'] == 505:

            goal = {}
            goal['time_left'] = int(round(3600 - 20 * 60 * (play['periodDescriptor']['number'] - 1) - timedelta(minutes=int(play['timeInPeriod'].split(':')[0]), seconds=int(play['timeInPeriod'].split(':')[1])).total_seconds(), -1) / 10)
            goal['score_diff'] = play['details']['homeScore'] - play['details']['awayScore']

            goals.append(goal)

        if 'situationCode' in play.keys() and play['situationCode'] in relevant_situation_codes:

            situation = {}
            situation['time_left'] = int(round(3600 - 20 * 60 * (play['periodDescriptor']['number'] - 1) - timedelta(minutes=int(play['timeInPeriod'].split(':')[0]), seconds=int(play['timeInPeriod'].split(':')[1])).total_seconds(), -1) / 10)
            situation['situationCode'] = play['situationCode'][::-1]

            situations.append(situation)

        if 'typeCode' in play.keys() and 'homeTeamDefendingSide' in play.keys() and 'details' in play.keys() and 'xCoord' in play['details'].keys():

            location_last_play = {}
            location_last_play['time_left'] = int(round(3600 - 20 * 60 * (play['periodDescriptor']['number'] - 1) - timedelta(minutes=int(play['timeInPeriod'].split(':')[0]), seconds=int(play['timeInPeriod'].split(':')[1])).total_seconds(), -1) / 10)

            if play['details']['zoneCode'] == 'N':
                location_last_play['zoneCode'] = 'N'
            elif play['homeTeamDefendingSide'] == 'right' and play['details']['xCoord'] < 0:
                location_last_play['zoneCode'] = 'O'
            elif play['homeTeamDefendingSide'] == 'right' and play['details']['xCoord'] > 0:
                location_last_play['zoneCode'] = 'D'
            elif play['homeTeamDefendingSide'] == 'left' and play['details']['xCoord'] > 0:
                location_last_play['zoneCode'] = 'O'
            elif play['homeTeamDefendingSide'] == 'left' and play['details']['xCoord'] > 0:
                location_last_play['zoneCode'] = 'D'
            else:
                location_last_play['zoneCode'] = 'N'
            
            location_last_plays.append(location_last_play)

    goals_timeline = np.zeros(360, dtype=int)
    situations_timeline = np.zeros(360, dtype=int)
    location_last_plays_timeline = np.full(360, '-', dtype=str)
    goals_sorted = sorted(goals, key=lambda x: x['time_left'], reverse=True)
    situations_sorted = sorted(situations, key=lambda x: x['time_left'], reverse=True)
    location_last_plays_sorted = sorted(location_last_plays, key=lambda x: x['time_left'], reverse=True)
    
    for i, goal in enumerate(goals_sorted):
        start = 360 - int(goals_sorted[i]['time_left'])
        end = 360 - (0 if i == len(goals_sorted) - 1 else int(goals_sorted[i+1]['time_left']))
        goals_timeline[start:end] = np.clip(goal['score_diff'], -6, 6)

    for i, situation in enumerate(situations_sorted):
        start = 360 - int(situations_sorted[i]['time_left'])
        end = 360 - (0 if i == len(situations_sorted) - 1 else int(situations_sorted[i+1]['time_left']))
        situations_timeline[start:end] = int(situation['situationCode'])

    for i, location_last_play in enumerate(location_last_plays):
        start = 360 - int(location_last_plays_sorted[i]['time_left'])
        end = 360 - (0 if i == len(location_last_plays_sorted) - 1 else int(location_last_plays_sorted[i+1]['time_left']))
        location_last_plays_timeline[start:end] = location_last_play['zoneCode']

    return goals_timeline, situations_timeline, location_last_plays_timeline