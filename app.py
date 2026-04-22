import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------------ CONFIG ------------------
st.set_page_config(layout="wide")

FILE = "Player_Match_Stats-Grid view copy.csv"

# ------------------ STYLE ------------------
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: #ffffff;
}

h1, h2, h3 {
    font-weight: 600;
}

[data-testid="metric-container"] {
    background-color: #111827;
    border-radius: 12px;
    padding: 15px;
}

[data-testid="stDataFrame"] {
    background-color: #111827;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.title("🏐 GAA Performance Dashboard")
st.caption("Player performance insights & selection tool")

# ------------------ LOAD DATA ------------------
df = pd.read_csv(FILE)
df.columns = df.columns.str.strip()

# ------------------ INPUT SYSTEM ------------------
st.header("➕ Add Match Data")

with st.form("data_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        match = st.selectbox("Match", sorted(df["Match"].dropna().unique()))
        player = st.text_input("New Player (or type existing)")

    with col2:
        position = st.selectbox("Position", ["Forward", "Midfielder", "Defender"])
        minutes = st.number_input("Minutes", 0, 90, 60)

    with col3:
        scores = st.number_input("Scores", 0, 20)
        assists = st.number_input("Assists", 0, 20)

    col4, col5 = st.columns(2)

    with col4:
        shots = st.number_input("Shots", 0, 50)
        turnovers_won = st.number_input("Turnovers Won", 0, 20)

    with col5:
        turnovers_lost = st.number_input("Turnovers Lost", 0, 20)

    submitted = st.form_submit_button("Save Data")

    if submitted:
        new_row = {
            "Match": match,
            "Player": player,
            "Position (from Player)": position,
            "Minutes": minutes,
            "Shots": shots,
            "Scores": scores,
            "Assists": assists,
            "Turnovers Won": turnovers_won,
            "Turnovers Lost": turnovers_lost
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(FILE, index=False)

        st.success("✅ Data saved successfully!")

# ------------------ FEATURE ENGINEERING ------------------
df["Custom Rating"] = (
    df["Scores"] * 3 +
    df["Assists"] * 2 +
    df["Shots"] +
    df["Turnovers Won"] * 2 -
    df["Turnovers Lost"] * 2
)

team = df.groupby(["Position (from Player)", "Player"])["Custom Rating"].mean().reset_index()
top_players = team.sort_values(by="Custom Rating", ascending=False).head(10)
consistency = df.groupby("Player")["Custom Rating"].std().sort_values()

# ------------------ METRICS ------------------
avg_rating = round(df["Custom Rating"].mean(), 2)
total_players = df["Player"].nunique()
best_player = top_players.iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("🏆 Top Player", best_player["Player"])
col2.metric("📊 Avg Rating", avg_rating)
col3.metric("👥 Total Players", total_players)

# ------------------ TOP PLAYERS ------------------
st.subheader("🏆 Top Players")
st.dataframe(top_players, width="stretch")
st.bar_chart(top_players.set_index("Player")["Custom Rating"])

# ------------------ STARTING 15 ------------------
st.subheader("🏅 Best Starting 15")

team_sorted = team.sort_values(by="Custom Rating", ascending=False)

forwards = team_sorted[team_sorted["Position (from Player)"] == "Forward"].head(6)
midfielders = team_sorted[team_sorted["Position (from Player)"] == "Midfielder"].head(2)
defenders = team_sorted[team_sorted["Position (from Player)"] == "Defender"].head(6)

starting_15 = pd.concat([defenders, midfielders, forwards])
st.dataframe(starting_15, width="stretch")

# ------------------ FILTER ------------------
st.subheader("🔍 Filter by Position")

position_filter = st.selectbox(
    "Select Position",
    sorted(df["Position (from Player)"].dropna().unique())
)

filtered = team[team["Position (from Player)"] == position_filter]
st.dataframe(filtered.sort_values(by="Custom Rating", ascending=False), width="stretch")

# ------------------ CONSISTENCY ------------------
st.subheader("📊 Most Consistent Players")
st.dataframe(consistency.head(10), width="stretch")

# ------------------ PLAYER COMPARISON ------------------
st.subheader("📊 Player Comparison")

players = sorted(df["Player"].dropna().unique())

player1 = st.selectbox("Player 1", players)
player2 = st.selectbox("Player 2", players)

p1 = df[df["Player"] == player1].mean(numeric_only=True)
p2 = df[df["Player"] == player2].mean(numeric_only=True)

stats = ["Scores", "Assists", "Shots", "Turnovers Won", "Turnovers Lost"]

p1_values = [p1[s] for s in stats]
p2_values = [p2[s] for s in stats]

angles = np.linspace(0, 2 * np.pi, len(stats), endpoint=False).tolist()

p1_values += p1_values[:1]
p2_values += p2_values[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))

ax.plot(angles, p1_values, linewidth=2, label=player1)
ax.fill(angles, p1_values, alpha=0.2)

ax.plot(angles, p2_values, linewidth=2, label=player2)
ax.fill(angles, p2_values, alpha=0.2)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(stats)
ax.set_yticklabels([])
ax.grid(alpha=0.3)

ax.set_title("Player Comparison")
ax.legend(loc="upper right")

st.pyplot(fig)

# ------------------ INSIGHTS ------------------
st.subheader("🧠 Key Insights")

# Best player
best_player = team.sort_values(by="Custom Rating", ascending=False).iloc[0]

# Most consistent
most_consistent_player = consistency.index[0]
most_consistent_value = consistency.iloc[0]

# Best position
best_position = (
    team.groupby("Position (from Player)")["Custom Rating"]
    .mean()
    .sort_values(ascending=False)
    .index[0]
)

# Efficiency insight
efficiency = (
    df.groupby("Player")["Scores"].sum() /
    df.groupby("Player")["Shots"].sum()
).replace([np.inf, -np.inf], 0).fillna(0)

best_efficiency_player = efficiency.sort_values(ascending=False).index[0]

st.write(f"🏆 Best Player: {best_player['Player']} ({round(best_player['Custom Rating'],2)})")
st.write(f"📉 Most Consistent: {most_consistent_player} (Std Dev: {round(most_consistent_value,2)})")
st.write(f"📊 Strongest Position: {best_position}")
st.write(f"🔥 Most Efficient Player: {best_efficiency_player}")

st.success("Insights generated from player performance data")