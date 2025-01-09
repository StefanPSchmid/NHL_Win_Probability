import streamlit as st
from datetime import datetime, date
from handle_api import get_game_id
from plot_win_probability import plot_specific_game
import time

def main():
    st.title("NHL Win Probability Predictor")
    
    # Add a brief description
    st.write("""
    This app predicts win probabilities for NHL games using a Markov model.
    Select the teams and date to generate a prediction visualization.
    """)
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    # Team selection
    with col1:
        # You might want to replace this with actual NHL team list
        nhl_teams = [
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
        home_team = st.selectbox("Select Home Team", sorted(nhl_teams), index=nhl_teams.index("TOR"))
    
    with col2:
        # Filter out home team from away team options to prevent same team matchup
        away_teams = [team for team in nhl_teams if team != home_team]
        away_team = st.selectbox("Select Away Team", sorted(away_teams), index=away_teams.index("BOS"))
    
    # Date selection
    # Default to today, allow selection starting from after lockout 2004/05 season
    max_date = datetime.now().date()
    min_date = date(2005, 10, 5)
    
    selected_date = st.date_input(
        "Select Game Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )
    
    # Convert date to required format (YYYY-MM-DD)
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Generate button
    if st.button("Generate Win Probability Plot"):
        try:
            start_time = time.time()
            with st.spinner("Fetching game data and generating plot..."):
                # Get game ID and create plot
                game_id, live = get_game_id(home_team=home_team, away_team=away_team, date=date_str)
                
                if game_id:
                    # Create figure using your existing function
                    fig = plot_specific_game(
                        game_id=game_id,
                        home_team=home_team,
                        away_team=away_team,
                        live=live
                    )
                    
                    # Display the plot
                    st.pyplot(fig)

                    st.info(f"Entire processing took {time.time() - start_time}")
                else:
                    st.error("No game found for the selected teams and date.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    # Add additional information or documentation
    with st.expander("About this app"):
        st.write("""
        This app uses a Markov model trained on historical NHL data to predict win probabilities.
        The model takes into account various factors including:
        - Team performance
        - Home/Away advantage
        - Historical matchup data
        
        The visualization shows how win probability changes throughout the game based on these factors.
        """)

if __name__ == "__main__":
    main()