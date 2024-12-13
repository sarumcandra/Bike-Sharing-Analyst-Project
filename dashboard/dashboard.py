import streamlit as st
from datetime import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='dark')

# Data untuk tren bike sharing
def create_yearly_users_df(df):
  yearly_users_df = df.groupby(by=["mnth","yr"]).cnt.sum().reset_index()
  yearly_users_df.rename(columns={
      "mnth":"Month",
      "yr":"Year",
      "cnt":"Total Users"
  }, inplace=True)

  return yearly_users_df

# data untuk jumlah penyewa per musim
def create_season_users_df(df):
  season_users_df = df.groupby(by="season").cnt.sum().reset_index()
  season_users_df.rename(columns={
      "season":"Season",
      "cnt":"Total Users"
  }, inplace=True)

  return season_users_df

# data untuk jumlah penyewa per cuaca
def create_weather_users_df(df):
  weather_users_df = df.groupby(by="weathersit").cnt.sum().reset_index()
  weather_users_df.rename(columns={
      "weathersit":"Weather",
      "cnt":"Total Users"
  }, inplace=True)

  return weather_users_df

# data untuk jumlah penyewa berdasarkan hari libur atau tidak
def create_holiday_users_df(df):
  holiday_users_df = df.groupby(by="workingday").cnt.sum().reset_index()
  holiday_users_df.rename(columns={
      "workingday":"Day",
      "cnt":"Total Users"
  }, inplace=True)

  return holiday_users_df

# data untuk jumlah penyewa per jam
def create_hr_users_df(df):
  hr_users_df = df.groupby(by=["hr","yr"]).cnt.sum().reset_index()
  hr_users_df.rename(columns={
      "hr":"Hour",
      "yr":"Year",
      "cnt":"Total Users"
  }, inplace=True)

  return hr_users_df

# data untuk jumlah penyewa per waktu
def create_time_users_df(df):
  time_users_df = df.groupby(by=["time_range"]).cnt.sum().reset_index()
  time_users_df.rename(columns={
      "time_range":"Time",
      "cnt":"Total Users"
  }, inplace=True)

  return time_users_df

# data
day_df = pd.read_csv('day.csv')
hour_df = pd.read_csv('hour.csv')

#mengubah data type datetime
datetime_columns = ["dteday"]
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)
hour_df.sort_values(by="dteday", inplace=True)
hour_df.reset_index(inplace=True)

# mengubah label menjadi string agar mudah dibaca
mnth_map = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}
day_df["season"] = day_df["season"].map({
    1: "Spring",
    2: "Summer",
    3: "Fall",
    4: "Winter"
})
day_df["mnth"] = day_df["mnth"].map(mnth_map)
day_df["yr"] = day_df["yr"].map({0: 2011, 1: 2012})
day_df["workingday"] = day_df["workingday"].map({0: "Holiday", 1: "Workingday"})
day_df["weathersit"] = day_df["weathersit"].map({
    1: "Clear/Cloudy",
    2: "Mist + Cloudy",
    3: "Light Snow/Rain",
    4: "Heavy Rain/Snow"})
hour_df["yr"] = hour_df["yr"].map({0: "2011", 1: "2012"})

# Kolom baru untuk time range
time_range = [0, 4, 8, 10, 14, 16, 18, 22, 24]
labels = ['Midnight', 'Dawn', 'Morning', 'Noon', 'Afternoon', 'Sunset', 'Evening', 'Night']
hour_df['time_range'] = pd.cut(hour_df['hr'], bins=time_range, labels=labels, right=False)

# mengurutkan data
day_df["mnth"] = pd.Categorical(
    day_df["mnth"],
    categories=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    ordered=True
)

hour_df["time_range"] = pd.Categorical(
    hour_df["time_range"],
    categories=["Midnight", "Dawn", "Morning", "Noon", "Afternoon", "Sunset", "Evening", "Night"],
    ordered=True
)

# rentang waktu
for column in datetime_columns:
  day_df[column] = pd.to_datetime(day_df[column])

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

start_date, end_date = st.date_input(
      label='Rentang Waktu',min_value=min_date,
      max_value=max_date,
      value=[min_date, max_date]
  )

main_df = day_df[(day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))]
main1_df = hour_df[(hour_df["dteday"] >= str(start_date)) & (hour_df["dteday"] <= str(end_date))]

yearly_users_df = create_yearly_users_df(main_df)
season_users_df = create_season_users_df(main_df)
weather_users_df = create_weather_users_df(main_df)
holiday_users_df = create_holiday_users_df(main_df)
hr_users_df = create_hr_users_df(main1_df)
time_users_df = create_time_users_df(main1_df)

st.header('Bike Sharing Dashboard :bike:')

st.subheader('Bike Sharing Trend')

col1, col2, col3 = st.columns(3)

with col1:
    total_users = main_df.cnt.sum()
    st.metric("Total Users", value=total_users)

with col2:
    total_casual = main_df.casual.sum()
    st.metric("Total Casual Users", value=total_casual)

with col3:
    total_registered = main_df.registered.sum()
    st.metric("Total Registered Users", value=total_registered)

fig, ax = plt.subplots(figsize=(16, 8))
sns.lineplot(
    data=yearly_users_df,
    x="Month",
    y="Total Users",
    hue="Year",
    ax=ax,
    palette="Set2",
    marker="o"
)
ax.set_title("Yearly Users", loc="center", fontsize=30)
ax.set_xlabel("Month")
ax.set_ylabel("Total Users")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader('Top Season & Weather')
col1, col2 = st.columns(2)

with col1:
  fig, ax = plt.subplots(figsize=(20,10))
  colors = ["#52A736", "#8AC847", "#8AC847", "#8AC847"]

  sns.barplot(
      x="Total Users",
      y="Season",
      data=season_users_df.sort_values(by="Total Users", ascending=False),
      palette=colors,
      ax=ax
  )
  ax.set_title("Top Season", loc="center", fontsize=30)
  ax.set_ylabel("Season")
  ax.set_xlabel("Total Users (million)")
  ax.tick_params(axis='y', labelsize=20)
  ax.tick_params(axis='x', labelsize=15)
  st.pyplot(fig)

with col2:
  fig, ax = plt.subplots(figsize=(20,10))

  colors = ["#52A736", "#8AC847", "#8AC847"]

  sns.barplot(
      x="Total Users",
      y="Weather",
      data=weather_users_df.sort_values(by="Total Users", ascending=False),
      palette=colors,
      ax=ax
  )
  ax.set_title("Top Weather", loc="center", fontsize=30)
  ax.set_ylabel("Weather")
  ax.set_xlabel("Total Users (million)")
  ax.tick_params(axis='y', labelsize=20)
  ax.tick_params(axis='x', labelsize=15)
  st.pyplot(fig)

st.subheader('Day with Most Bike Sharing')
fig, ax = plt.subplots(figsize=(20,10))
sns.barplot(
    x="Day",
    y="Total Users",
    data=holiday_users_df.sort_values(by="Total Users", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Day with Most Bike Sharing'", loc="center", fontsize=30)
ax.set_ylabel("Total Users (million)")
ax.set_xlabel("Day")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader('Trend Bike Sharing by Hour')
fig, ax = plt.subplots(figsize=(16,8))

sns.lineplot(
    data=hr_users_df,
    x="Hour",
    y="Total Users",
    hue="Year",
    ax=ax,
    palette="Set2",
    marker="o"
)
ax.set_title("Trend Bike Sharing by Hour", loc="center", fontsize=30)
ax.set_ylabel("Total Users")
ax.set_xlabel("Hour")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader('Top Time Range')
fig, ax = plt.subplots(figsize=(20,10))

colors = ['#001A38', '#F3D69E', '#F6BD73', '#F2D13F', '#FBCB78', '#FF9436', '#003367', '#00224E']

sns.barplot(
    x="Time",
    y="Total Users",
    data=time_users_df.sort_values(by="Total Users", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Top Time Range", loc="center", fontsize=30)
ax.set_ylabel("Total Users (million)")
ax.set_xlabel("Time Range")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.caption('Copyright (c) Arum 2024')
