import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# Set page config to wide layout
st.set_page_config(layout="wide")

# Define electoral votes and coordinates for each state (complete list)
electoral_votes = {
    "Alabama": (9, [32.806671, -86.791130]),
    "Alaska": (3, [61.370716, -152.404419]),
    "Arizona": (11, [33.729759, -111.431221]),
    "Arkansas": (6, [34.969704, -92.373123]),
    "California": (54, [36.116203, -119.681564]),
    "Colorado": (10, [39.059811, -105.311104]),
    "Connecticut": (7, [41.597782, -72.755371]),
    "Delaware": (3, [39.318523, -75.507141]),
    "Florida": (30, [27.766279, -81.686783]),
    "Georgia": (16, [33.040619, -83.643074]),
    "Hawaii": (4, [21.094318, -157.498337]),
    "Idaho": (4, [44.240459, -114.478828]),
    "Illinois": (19, [40.349457, -88.986137]),
    "Indiana": (11, [39.849426, -86.258278]),
    "Iowa": (6, [42.011539, -93.210526]),
    "Kansas": (6, [38.526600, -96.726486]),
    "Kentucky": (8, [37.668140, -84.670067]),
    "Louisiana": (8, [31.169546, -91.867805]),
    "Maine": (4, [44.693947, -69.381927]),
    "Maryland": (10, [39.063946, -76.802101]),
    "Massachusetts": (11, [42.230171, -71.530106]),
    "Michigan": (15, [43.326618, -84.536095]),
    "Minnesota": (10, [45.694454, -93.900192]),
    "Mississippi": (6, [32.741646, -89.678696]),
    "Missouri": (10, [38.456085, -92.288368]),
    "Montana": (4, [46.921925, -110.454353]),
    "Nebraska": (5, [41.125370, -98.268082]),
    "Nevada": (6, [38.313515, -117.055374]),
    "New Hampshire": (4, [43.452492, -71.563896]),
    "New Jersey": (14, [40.298904, -74.521011]),
    "New Mexico": (5, [34.840515, -106.248482]),
    "New York": (28, [42.165726, -74.948051]),
    "North Carolina": (16, [35.630066, -79.806419]),
    "North Dakota": (3, [47.528912, -99.784012]),
    "Ohio": (17, [40.388783, -82.764915]),
    "Oklahoma": (7, [35.565342, -96.928917]),
    "Oregon": (8, [44.572021, -122.070938]),
    "Pennsylvania": (19, [40.590752, -77.209755]),
    "Rhode Island": (4, [41.680893, -71.511780]),
    "South Carolina": (9, [33.856892, -80.945007]),
    "South Dakota": (3, [44.299782, -99.438828]),
    "Tennessee": (11, [35.747845, -86.692345]),
    "Texas": (40, [31.054487, -97.563461]),
    "Utah": (6, [40.150032, -111.862434]),
    "Vermont": (3, [44.045876, -72.710686]),
    "Virginia": (13, [37.769337, -78.169968]),
    "Washington": (12, [47.400902, -121.490494]),
    "Washington, D.C.": (3, [38.89511, -77.03637]),
    "West Virginia": (4, [38.491226, -80.954456]),
    "Wisconsin": (10, [44.268543, -89.616508]),
    "Wyoming": (3, [42.755966, -107.302490])
}

# Updated list of swing states
swing_states = [
    "Arizona", "Georgia", "Michigan", "Nevada", "North Carolina", 
    "Pennsylvania", "Wisconsin", "Florida", "Virginia", 
    "New Hampshire", "Minnesota", "Iowa"
]

non_swing_results = {
    "California": "blue", "Texas": "red", "New York": "blue", "Washington": "blue",
    "Oregon": "blue", "Idaho": "red", "Montana": "red", "Wyoming": "red",
    "Utah": "red", "New Mexico": "blue", "Colorado": "blue", "North Dakota": "red",
    "South Dakota": "red", "Nebraska": "red", "Kansas": "red", "Oklahoma": "red",
    "Missouri": "red", "Arkansas": "red", "Louisiana": "red", "Mississippi": "red",
    "Alabama": "red", "South Carolina": "red", "Tennessee": "red", "Kentucky": "red",
    "West Virginia": "red", "Indiana": "red", "Ohio": "red", "Maine": "blue",
    "Vermont": "blue", "New Jersey": "blue", "Connecticut": "blue", "Rhode Island": "blue",
    "Massachusetts": "blue", "Delaware": "blue", "Maryland": "blue", "Illinois": "blue",
    "Hawaii": "blue", "Alaska": "red", "Washington, D.C.": "blue"
}



# Load or initialize ballots CSV
ballots_file = "ballots.csv"
if not os.path.exists(ballots_file):
    pd.DataFrame(columns=["username", "state", "choice", "electoral_votes"]).to_csv(ballots_file, index=False)

# Main screen toggle
screen = st.radio("Select Screen", ["Submit Ballot", "View Results"])

if screen == "Submit Ballot":
    # Clear session state when a new username is entered
    username = st.text_input("Enter your username to start or edit your ballot:")
    if username:
        # Load ballots to check if the user already submitted
        ballots_df = pd.read_csv(ballots_file)
        user_submitted = username in ballots_df["username"].values

        # Initialize session state for new users or editing users
        if "user_map" not in st.session_state:
            st.session_state.user_map = {state: "gray" for state in electoral_votes.keys()}
        if "electoral_totals" not in st.session_state:
            st.session_state.electoral_totals = {"blue": 0, "red": 0}

        if user_submitted and "edit_mode" not in st.session_state:
            # Display only the option to edit the ballot
            st.warning("You have already submitted a ballot.")
            if st.button("Edit Ballot"):
                st.session_state.edit_mode = True
                # Prepopulate user's previous selections
                user_votes = ballots_df[ballots_df["username"] == username].set_index("state")["choice"].to_dict()
                st.session_state.user_map = {state: user_votes.get(state, "gray") for state in electoral_votes.keys()}
                st.session_state.electoral_totals = {
                    "blue": sum(votes for state, (votes, _) in electoral_votes.items() if st.session_state.user_map[state] == "blue"),
                    "red": sum(votes for state, (votes, _) in electoral_votes.items() if st.session_state.user_map[state] == "red")
                }

        if not user_submitted or "edit_mode" in st.session_state:
            # Show only swing states by default
            show_swing_states = st.checkbox("Show only Swing States", value=True)
            states_to_show = swing_states if show_swing_states else list(electoral_votes.keys())
            if st.button("Autopopulate Non-Swing States"):
                for state, color in non_swing_results.items():
                    if state not in swing_states:
                        st.session_state.user_map[state] = color
                        # Update electoral totals
                        if color == "blue":
                            st.session_state.electoral_totals["blue"] += electoral_votes[state][0]
                        elif color == "red":
                            st.session_state.electoral_totals["red"] += electoral_votes[state][0]
            # Select a state and color it
            state_selected = st.selectbox("Select a state to mark:", states_to_show, key="state_select_submit")
            
            if st.button("Mark Blue"):
                if st.session_state.user_map[state_selected] != "blue":
                    if st.session_state.user_map[state_selected] == "red":
                        st.session_state.electoral_totals["red"] -= electoral_votes[state_selected][0]
                    st.session_state.user_map[state_selected] = "blue"
                    st.session_state.electoral_totals["blue"] += electoral_votes[state_selected][0]
            
            if st.button("Mark Red"):
                if st.session_state.user_map[state_selected] != "red":
                    if st.session_state.user_map[state_selected] == "blue":
                        st.session_state.electoral_totals["blue"] -= electoral_votes[state_selected][0]
                    st.session_state.user_map[state_selected] = "red"
                    st.session_state.electoral_totals["red"] += electoral_votes[state_selected][0]

            # Create Folium map
            map_center = [37.0902, -95.7129]  # Center of the US
            m = folium.Map(location=map_center, zoom_start=4)

            # Add markers for each state based on user selections
            for state, (votes, coords) in electoral_votes.items():
                if show_swing_states and state not in swing_states:
                    continue
                color = "blue" if st.session_state.user_map[state] == "blue" else "red" if st.session_state.user_map[state] == "red" else "gray"
                folium.Marker(location=coords, tooltip=f"{state} ({votes} votes)", icon=folium.Icon(color=color)).add_to(m)

            # Display the map
            st_folium(m, width=700)

            # Display electoral vote totals in line
            col1, col2 = st.columns(2)
            col1.metric("Total Democrat (Blue) Votes", st.session_state.electoral_totals["blue"])
            col2.metric("Total Republican (Red) Votes", st.session_state.electoral_totals["red"])

            # Submit or Resubmit ballot button
            if st.button("Submit/Resubmit Ballot"):
                # Remove any previous entries for this user
                ballots_df = ballots_df[ballots_df["username"] != username]
                
                # Prepare new ballot data
                ballot_data = [
                    {
                        "username": username,
                        "state": state,
                        "choice": st.session_state.user_map[state],
                        "electoral_votes": electoral_votes[state][0]
                    }
                    for state in st.session_state.user_map.keys()
                    if st.session_state.user_map[state] in ["blue", "red"]
                ]
                
                # Overwrite ballots file with new data
                ballot_df = pd.DataFrame(ballot_data)
                updated_ballots_df = pd.concat([ballots_df, ballot_df], ignore_index=True)
                updated_ballots_df.to_csv(ballots_file, index=False)
                
                st.write("Your ballot has been resubmitted!")
                # Clear edit mode
                del st.session_state["edit_mode"]

# Results page metrics with two columns layout
# Results page metrics with two columns layout, only complete ballots in averages
if screen == "View Results":
    # Load all ballots
    ballots_df = pd.read_csv(ballots_file)
    
    # Show only swing states if checked
    show_swing_states_only = st.checkbox("Show only Swing States", value=True)
    states_to_check = swing_states if show_swing_states_only else list(electoral_votes.keys())
    
    # Filter for complete ballots
    complete_ballots = (
        ballots_df[ballots_df["state"].isin(states_to_check)]
        .groupby("username")["state"]
        .nunique() == len(states_to_check)
    )
    complete_users = complete_ballots[complete_ballots].index.tolist()
    complete_df = ballots_df[ballots_df["username"].isin(complete_users) & ballots_df["state"].isin(states_to_check)]
    
    # Dropdown to select a user and view their results
    selected_user = st.selectbox("Select a user to view results:", ballots_df["username"].unique(), key="user_select_results")
    user_df = ballots_df[(ballots_df["username"] == selected_user) & (ballots_df["state"].isin(states_to_check))]
    
    # Display state-by-state voting in a table for the selected user with an expander
    expander_open = show_swing_states_only  # Default open if "Show only Swing States" is checked
    with st.expander(f"State-by-State Voting for {selected_user}", expanded=expander_open):
        st.table(user_df[["state", "choice", "electoral_votes"]].sort_values(by="state"))
    
    # Calculate the Total Pot
    total_pot = ballots_df["username"].nunique() * 25
    st.write(f"<h3 style='color: green;'>Total Pot: ${total_pot}</h3>", unsafe_allow_html=True)

    # Calculate selected user's total blue and red counts
    selected_user_total_blue = user_df[user_df["choice"] == "blue"]["electoral_votes"].sum()
    selected_user_total_red = user_df[user_df["choice"] == "red"]["electoral_votes"].sum()
    
    # Calculate average total blue and red counts for complete ballots only
    avg_total_blue = complete_df[complete_df["choice"] == "blue"].groupby("username")["electoral_votes"].sum().mean()
    avg_total_red = complete_df[complete_df["choice"] == "red"].groupby("username")["electoral_votes"].sum().mean()
    
    # Display the metrics in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"{selected_user}'s Totals")
        st.metric("Total Blue Votes", selected_user_total_blue)
        st.metric("Total Red Votes", selected_user_total_red)
    
    with col2:
        st.subheader("Average Totals of Complete Ballots")
        st.metric("Average Total Blue Votes", f"{avg_total_blue:.1f}")
        st.metric("Average Total Red Votes", f"{avg_total_red:.1f}")

    # Display map for the user's ballot
    map_center = [37.0902, -95.7129]
    m = folium.Map(location=map_center, zoom_start=4)
    
    for state, (votes, coords) in electoral_votes.items():
        if show_swing_states_only and state not in swing_states:
            continue
        state_choice = user_df[user_df["state"] == state]["choice"]
        color = state_choice.iloc[0] if not state_choice.empty else "gray"
        folium.Marker(location=coords, tooltip=f"{state} ({votes} votes)", icon=folium.Icon(color=color)).add_to(m)

    st_folium(m, width=700)
    
    # Download button for ballots file
    st.download_button(
        label="Download Ballots CSV",
        data=ballots_df.to_csv(index=False),
        file_name="ballots.csv",
        mime="text/csv"
    )
