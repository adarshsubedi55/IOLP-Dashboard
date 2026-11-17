from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

#page title and layout
st.set_page_config(page_title= "IOLP Dashboard", layout="wide", page_icon="random")


#cache
@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "iolp_cleaned.csv"
    df= pd.read_csv(file_path)
    return df

df= load_data() 


#Filters used to sort in the dataset
st.sidebar.header("Filters")

#Ownership type leased or owned
tenure = st.sidebar.multiselect("Owned or Leased", ["OWNED", "LEASED"], default=["OWNED"])


#Region wise filter 
regions = sorted(df["GSA Region"].unique())
selected_regions = st.sidebar.multiselect("GSA Region", regions, default=regions)


# State wise filter if only region is selected
state_options = sorted(df.loc[df["GSA Region"].isin(selected_regions), "State"].unique())
selected_states = st.sidebar.multiselect("State", state_options, default=state_options)

#Year of construction filter
year_min = int(df["Construction Date"].min())
year_max = int(df["Construction Date"].max())
selected_years = st.sidebar.slider("Construction year", year_min, year_max, (year_min, year_max))


# Leased buildings have no construction year
include_unknown_year = st.sidebar.checkbox("Include properties with unknown construction year", value=True)



#Building size
bands = ["<5k", "5-25k", "25-100k", "100-500k", "500k+"]
df["size_band"] = pd.cut(df["Building Rentable Square Feet"],
                         [-1, 5e3, 25e3, 100e3, 500e3, 1e8], labels=bands)
sel_bands = st.sidebar.multiselect("Building size (sq ft)", bands, default=bands)



available = "Available Square Feet"

available_steps = [0, 1, 10_000, 50_000, 250_000, int(df[available].max())]

available_range = st.sidebar.select_slider("Available sq ft", options=available_steps, value=(available_steps[0], available_steps[-1]), format_func=lambda x: f"{x:,}")





#applying filters
year_ok = df["Construction Date"].between(selected_years[0], selected_years[1])
if include_unknown_year:
    year_ok = year_ok | df["Construction Date"].isna()



available_ok = df[available].between(available_range[0], available_range[1])
available_ok = available_ok | df[available].isna()          # keep leased rows whose value is missing




filtered = df[
    df["Owned or Leased"].isin(tenure)
    & df["GSA Region"].isin(selected_regions)
    &df["State"].isin(selected_states)
    & year_ok
    & df["size_band"].isin(sel_bands)
    &available_ok
]

if filtered.empty:
    st.warning("No properties match these filters. Widen your selection.")
    st.stop()

st.sidebar.caption(f"{len(filtered):,} of {len(df):,} properties shown")



#Main dashboard

st.title("IOLP Property Utilization Dashboard")
st.write("Explore where federal property space sits unused, and which regions, states and building ages account for it.")
