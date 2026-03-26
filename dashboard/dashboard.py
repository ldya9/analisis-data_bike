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
# LOAD DATA (MAIN DATA)
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("./dashboard/main_data.csv")
    return df

df = load_data()

# =========================
# DATA PREPROCESSING
# =========================
df['dteday'] = pd.to_datetime(df['dteday'])

# Mapping biar user-friendly
year_map = {0: "2011", 1: "2012"}
season_map = {
    1: "Spring",
    2: "Summer",
    3: "Fall",
    4: "Winter"
}
weather_map = {
    1: "Clear",
    2: "Mist/Cloudy",
    3: "Light Rain/Snow",
    4: "Heavy Rain/Snow"
}

df['year_label'] = df['yr'].map(year_map)
df['season_label'] = df['season'].map(season_map)
df['weather_label'] = df['weathersit'].map(weather_map)

# =========================
# SIDEBAR
# =========================
logo = Image.open("./dashboard/logo.png")
st.sidebar.image(logo, width=140)
st.sidebar.markdown("## 🚴 Bike Sharing Analysis")

menu = st.sidebar.radio(
    "Navigation",
    ["Overview", 
     "Weather Analysis", 
     "User Pattern Analysis",
     "Advanced Analysis"]
)

# =========================
# FILTER (DYNAMIC)
# =========================
st.sidebar.markdown("### 🔍 Filter Data")

year_filter = st.sidebar.multiselect(
    "Pilih Tahun",
    options=df['year_label'].unique(),
    default=df['year_label'].unique()
)

season_filter = st.sidebar.multiselect(
    "Pilih Musim",
    options=df['season_label'].unique(),
    default=df['season_label'].unique()
)

weather_filter = st.sidebar.multiselect(
    "Pilih Cuaca",
    options=df['weather_label'].unique(),
    default=df['weather_label'].unique()
)

filtered_df = df[
    (df['year_label'].isin(year_filter)) &
    (df['season_label'].isin(season_filter)) &
    (df['weather_label'].isin(weather_filter))
]

# =========================
# COLOR
# =========================
PRIMARY = "#355872"
SECONDARY = "#7AAACE"

# =========================
# OVERVIEW
# =========================
if menu == "Overview":
    st.title("🚴 Bike Sharing Dashboard (2011–2012)")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Rentals", f"{int(filtered_df['cnt'].sum()):,}")
    col2.metric("Average Daily Rentals", round(filtered_df['cnt'].mean(), 2))
    col3.metric("Total Registered Users", f"{int(filtered_df['registered'].sum()):,}")

    st.divider()
    st.dataframe(filtered_df.head())

# =========================
# WEATHER ANALYSIS
# =========================
elif menu == "Weather Analysis":
    st.title("🌦 Weather Impact on Bike Rentals")

    weather_avg = filtered_df.groupby('weather_label')['cnt'].mean().reset_index()

    left, center, right = st.columns([1,2,1])

    with center:
        fig, ax = plt.subplots(figsize=(5,3))
        sns.barplot(
            data=weather_avg,
            x='weather_label',
            y='cnt',
            color=PRIMARY,
            ax=ax
        )

        ax.set_ylabel("Avg Rentals")
        ax.set_xlabel("")
        ax.set_title("Rentals by Weather")
        plt.xticks(rotation=20)

        st.pyplot(fig)

# =========================
# USER PATTERN ANALYSIS
# =========================
elif menu == "User Pattern Analysis":
    st.title("👥 User Pattern: Casual vs Registered")

    filtered_df['day_type'] = filtered_df['weekday'].apply(
        lambda x: "Weekend" if x in [0,6] else "Weekday"
    )

    user_pattern = filtered_df.groupby('day_type')[['casual','registered']].mean().reset_index()

    left, center, right = st.columns([1,2,1])

    with center:
        fig, ax = plt.subplots(figsize=(5,3))

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
        ax.set_xticklabels(user_pattern['day_type'])

        ax.set_ylabel("Avg Rentals")
        ax.set_title("Weekday vs Weekend Usage")
        ax.legend()

        st.pyplot(fig)

# =========================
# ADVANCED ANALYSIS
# =========================
elif menu == "Advanced Analysis":
    st.title("📊 Demand Grouping")

    bins = [0,1000,3000,6000]
    labels = ['Low','Medium','High']

    filtered_df['Demand Category'] = pd.cut(filtered_df['cnt'], bins=bins, labels=labels)
    demand_summary = filtered_df['Demand Category'].value_counts()

    left, center, right = st.columns([1,2,1])

    with center:
        fig, ax = plt.subplots(figsize=(5,3))

        ax.bar(
            demand_summary.index.astype(str),
            demand_summary.values,
            color=SECONDARY
        )

        ax.set_ylabel("Days")
        ax.set_title("Demand Distribution")

        st.pyplot(fig)
