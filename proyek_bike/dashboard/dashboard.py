import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
.main {
    background-color: #FFFBF1;
}
[data-testid="stSidebar"] {
    background-color: #84B179;
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #2E2E2E;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    day = pd.read_csv("./data/day.csv")
    hour = pd.read_csv("./data/hour.csv")
    return day, hour

day_df, hour_df = load_data()

# =========================
# SIDEBAR
# =========================
logo = Image.open("./dashboard/logo.png")
st.sidebar.image(logo, width=140)
st.sidebar.markdown("## Bike Sharing Analysis")

menu = st.sidebar.radio(
    "Navigation",
    ["Overview", 
     "Weather Analysis", 
     "User Pattern Analysis",
     "Advanced Analysis"]
)

# =========================
# COLOR PALETTE
# =========================
PRIMARY = "#355872"
SECONDARY = "#7AAACE"

# =========================
# OVERVIEW
# =========================
if menu == "Overview":
    st.title("Bike Sharing Dashboard (2011–2012)")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Rentals", f"{int(day_df['cnt'].sum()):,}")
    col2.metric("Average Daily Rentals", round(day_df['cnt'].mean(), 2))
    col3.metric("Total Registered Users", f"{int(day_df['registered'].sum()):,}")

    st.divider()
    st.dataframe(day_df.head())

# =========================
# WEATHER ANALYSIS
# =========================
elif menu == "Weather Analysis":
    st.title("Weather Impact on Bike Rentals")

    weather_avg = day_df.groupby('weathersit')['cnt'].mean().reset_index()

    weather_label = {
        1: "1 - Clear",
        2: "2 - Mist/Cloudy",
        3: "3 - Light Rain/Snow",
        4: "4 - Heavy Rain/Snow"
    }

    weather_avg['Weather'] = weather_avg['weathersit'].map(weather_label)

    left, center, right = st.columns([1,2,1])

    with center:
        fig, ax = plt.subplots(figsize=(4,2.5))
        sns.barplot(
            data=weather_avg,
            x='Weather',
            y='cnt',
            color=PRIMARY,
            ax=ax
        )

        ax.set_ylabel("Avg Rentals", fontsize=8)
        ax.set_xlabel("")
        ax.set_title("Rentals by Weather", fontsize=9)
        ax.tick_params(axis='x', labelsize=7)
        ax.tick_params(axis='y', labelsize=7)

        st.pyplot(fig)

# =========================
# USER PATTERN ANALYSIS
# =========================
elif menu == "User Pattern Analysis":
    st.title("User Pattern: Casual vs Registered")

    day_df['day_type'] = day_df['weekday'].apply(
        lambda x: "Weekend" if x in [0,6] else "Weekday"
    )

    user_pattern = day_df.groupby('day_type')[['casual','registered']].mean().reset_index()

    left, center, right = st.columns([1,2,1])

    with center:
        fig, ax = plt.subplots(figsize=(4,2.5))

        x = range(len(user_pattern['day_type']))
        width = 0.35

        ax.bar(
            [i - width/2 for i in x],
            user_pattern['casual'],
            width=width,
            color=PRIMARY,
            label='Casual'
        )

        ax.bar(
            [i + width/2 for i in x],
            user_pattern['registered'],
            width=width,
            color=SECONDARY,
            label='Registered'
        )

        ax.set_xticks(x)
        ax.set_xticklabels(user_pattern['day_type'], fontsize=7)

        ax.set_ylabel("Avg Rentals", fontsize=8)
        ax.set_title("Weekday vs Weekend Usage", fontsize=9)
        ax.tick_params(axis='y', labelsize=7)
        ax.legend(fontsize=7)

        st.pyplot(fig)

# =========================
# ADVANCED ANALYSIS
# =========================
elif menu == "Advanced Analysis":
    st.title("Demand Grouping")

    bins = [0,1000,3000,6000]
    labels = ['Low','Medium','High']

    day_df['Demand Category'] = pd.cut(day_df['cnt'], bins=bins, labels=labels)
    demand_summary = day_df['Demand Category'].value_counts()

    left, center, right = st.columns([1,2,1])

    with center:
        fig, ax = plt.subplots(figsize=(4,2.5))

        ax.bar(
            demand_summary.index.astype(str),
            demand_summary.values,
            color=SECONDARY
        )

        ax.set_ylabel("Days", fontsize=8)
        ax.set_title("Demand Distribution", fontsize=9)
        ax.tick_params(axis='both', labelsize=7)

        st.pyplot(fig)
