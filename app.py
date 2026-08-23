import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Tips Dataset EDA", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv("data/dataset.csv")


df = load_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

day_options = sorted(df["day"].unique())
selected_days = st.sidebar.multiselect("Day of week", day_options, default=day_options)

bill_min, bill_max = float(df["total_bill"].min()), float(df["total_bill"].max())
bill_range = st.sidebar.slider(
    "Total bill range ($)", min_value=bill_min, max_value=bill_max, value=(bill_min, bill_max)
)

sex_options = sorted(df["sex"].unique())
selected_sex = st.sidebar.multiselect("Sex", sex_options, default=sex_options)

smoker_options = sorted(df["smoker"].unique())
selected_smoker = st.sidebar.multiselect("Smoker", smoker_options, default=smoker_options)

filtered = df[
    df["day"].isin(selected_days)
    & df["sex"].isin(selected_sex)
    & df["smoker"].isin(selected_smoker)
    & df["total_bill"].between(bill_range[0], bill_range[1])
]

st.title("Tips Dataset — Exploratory Data Analysis")
st.markdown(
    "Interactive EDA of the classic **tips** dataset (restaurant bills and tips). "
    "Use the sidebar filters to slice the data; every section below updates accordingly."
)

if filtered.empty:
    st.warning("No rows match the current filter selection. Adjust the filters in the sidebar to see data.")
    st.stop()

# ---------- Section 1: Overview ----------
st.header("1. Overview")

col1, col2 = st.columns(2)
col1.metric("Rows", filtered.shape[0])
col2.metric("Columns", filtered.shape[1])

st.subheader("Data preview")
st.dataframe(filtered.head(20))

st.subheader("Column dtypes")
dtypes_df = filtered.dtypes.astype(str).reset_index()
dtypes_df.columns = ["Column", "Dtype"]
st.dataframe(dtypes_df)

# ---------- Section 2: EDA ----------
st.header("2. Exploratory Data Analysis")

st.subheader("Summary statistics")
st.dataframe(filtered.describe())
st.markdown("Descriptive statistics (count, mean, std, min/max, quartiles) for numeric columns.")

st.subheader("Missing values per column")
missing = filtered.isna().sum().reset_index()
missing.columns = ["Column", "Missing count"]
st.dataframe(missing)
st.markdown("Count of missing (NaN) values in each column of the filtered data.")

numeric_cols = filtered.select_dtypes(include="number").columns.tolist()
st.subheader("Correlation matrix")
if len(numeric_cols) >= 2:
    corr = filtered[numeric_cols].corr()
    fig_corr = px.imshow(
        corr, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto"
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    st.markdown("Pairwise Pearson correlation between numeric columns (total_bill, tip, size).")
else:
    st.info("Not enough numeric columns to compute a correlation matrix.")

# ---------- Section 3: Visualizations ----------
st.header("3. Visualizations")

st.subheader("Distribution of total bill")
fig_hist = px.histogram(filtered, x="total_bill", nbins=30, color="smoker")
st.plotly_chart(fig_hist, use_container_width=True)
st.markdown("Histogram showing the distribution of total bill amounts, split by smoker status.")

st.subheader("Total bill vs. tip")
fig_scatter = px.scatter(
    filtered, x="total_bill", y="tip", color="day", size="size", hover_data=["sex", "time"]
)
st.plotly_chart(fig_scatter, use_container_width=True)
st.markdown("Scatter plot of tip amount against total bill, colored by day of week.")

st.subheader("Average tip by day")
avg_tip_by_day = filtered.groupby("day", observed=True)["tip"].mean().reset_index()
fig_bar = px.bar(avg_tip_by_day, x="day", y="tip", color="day")
st.plotly_chart(fig_bar, use_container_width=True)
st.markdown("Bar chart of the average tip amount grouped by day of week.")

st.subheader("Total bill distribution by time")
fig_box = px.box(filtered, x="time", y="total_bill", color="time")
st.plotly_chart(fig_box, use_container_width=True)
st.markdown("Box plot comparing total bill distributions between Lunch and Dinner.")
