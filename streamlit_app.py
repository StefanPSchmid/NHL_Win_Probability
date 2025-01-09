import streamlit as st
from datetime import datetime, date
from handle_api import get_game_id
from plot_win_probability import plot_specific_game
import time

# Set page configuration
st.set_page_config(
    page_title="NHL Win Probability Predictor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #1d3557;
        color: white;
        padding: 0.75rem;
        font-weight: bold;
        border: none;
        border-radius: 0.5rem;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #457b9d;
    }
    .title-container {
        background-color: #1d3557;
        padding: 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        color: white;
    }
    .team-selection-container {
        background-color: #f1faee;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .at-symbol {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        font-size: 1.5rem;
        font-weight: bold;
        color: #1d3557;
    }
    .away-team-header {
        text-align: right !important;
    }
    .stDateInput > div > div {
        background-color: white;
    }
    .plot-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .about-section {
        background-color: #1d3557;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 2rem;
        color: white;
    }
    /* Right align the away team select box */
    [data-testid="stSelectbox"] {
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    # Title section with custom styling
    st.markdown("""
        <div class="title-container">
            <h1 style='text-align: center;'>NHL Win Probability</h1>
            <p style='text-align: center; font-size: 1.2rem;'>
                Predict the probabilities of your NHL games, live and after the game.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create columns for team selection with @ symbol
    col1, col2, col3 = st.columns([2, 0.25, 2])
    
    # NHL teams list
    nhl_teams = [
        "ANA", "ARI", "BOS", "BUF", "CGY", "CAR", "CHI", "COL", 
        "CBJ", "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL",
        "NSH", "NJD", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS",
        "SEA", "STL", "TBL", "TOR", "UTA", "VAN", "VGK", "WSH", "WPG"
    ]
    
    # Team selection with improved styling
    with col1:
        st.markdown('<h3 class="away-team-header">Away Team</h3>', unsafe_allow_html=True)
        away_team = st.selectbox(
            "Select Away Team",
            sorted(nhl_teams),
            index=nhl_teams.index("BOS"),
            key="away_team",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown('<div class="at-symbol">@</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("### Home Team")
        home_teams = [team for team in nhl_teams if team != away_team]
        home_team = st.selectbox(
            "Select Home Team",
            sorted(home_teams),
            index=home_teams.index("TOR") if "TOR" in home_teams else 0,
            key="home_team",
            label_visibility="collapsed"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Date selection with custom container
    st.markdown("### Game Date")
    max_date = datetime.now().date()
    min_date = date(2005, 10, 5)
    
    selected_date = st.date_input(
        "Select Game Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Convert date to required format
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Generate button
    if st.button("Generate Win Probability Plot"):
        try:
            start_time = time.time()
            with st.spinner("Analyzing game data..."):
                game_id, live = get_game_id(home_team=home_team, away_team=away_team, date=date_str)
                
                if game_id:
                    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                    fig = plot_specific_game(
                        game_id=game_id,
                        home_team=home_team,
                        away_team=away_team,
                        live=live
                    )
                    st.pyplot(fig)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("⚠️ No game found for the selected teams and date.")
        except Exception as e:
            st.error(f"⚠️ An error occurred: {str(e)}")
    
    # About section with custom styling
    with st.expander("About this Predictor"):
        st.markdown("""
        <div class="about-section">
            <h4>How it Works</h4>
            <p>This advanced predictor uses a Markov model trained on historical NHL from the seasons 2021/22, 2022/23, 2023/24 data to forecast game outcomes. The model takes a game as states, considers the following:</p>
            <ul>
                <li>Score difference</li>
                <li>Number of players on the ice</li>
                <li>In which third the puck is</li>
            </ul>
            <p>The visualization shows real-time win probability predicted at every second of the game, helping you understand how different game events impact each team's chances of victory. The prediction works for past and live games.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()