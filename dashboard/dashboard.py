import streamlit as st
import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================
# 🏁 Judul dan Deskripsi
# ==============================
st.header('🚴 Analisis Penyewaan Sepeda dengan Streamlit')
st.markdown("""
Dashboard ini menampilkan eksplorasi dan analisis pola penyewaan sepeda berdasarkan waktu, cuaca, dan musim.
Terdapat fitur interaktif untuk memfilter data berdasarkan **tanggal**, **musim**, dan **cuaca**.
""")

# ==============================
# 📦 Load Data
# ==============================
all_data_df = pd.read_csv('all_data.csv')

# ==============================
# 🧹 Data Cleaning
# ==============================
column_mapping = {
    'dteday': 'date',
    'hr': 'hour',
    'temp': 'temperature',
    'hum': 'humidity',
    'cnt': 'total'
}
all_data_df.rename(columns=column_mapping, inplace=True)
all_data_df['date'] = pd.to_datetime(all_data_df['date'])

all_data_df['season'] = all_data_df['season'].astype('category')
all_data_df['season'] = all_data_df['season'].cat.rename_categories({
    1: 'Winter',
    2: 'Spring',
    3: 'Summer',
    4: 'Autumn'
})

weather_map = {
    1: 'Clear / Partly Cloudy',
    2: 'Mist / Cloudy',
    3: 'Light Rain / Snow',
    4: 'Heavy Rain / Fog'
}
all_data_df['weather_desc'] = all_data_df['weathersit'].map(weather_map)

# ==============================
# 🧭 Filter Interaktif
# ==============================
st.sidebar.header("🔍 Filter Data")
min_date = all_data_df['date'].min()
max_date = all_data_df['date'].max()

# Filter berdasarkan rentang tanggal
start_date, end_date = st.sidebar.date_input(
    "Pilih rentang tanggal:",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter berdasarkan musim
selected_season = st.sidebar.multiselect(
    "Pilih musim:",
    options=all_data_df['season'].unique(),
    default=all_data_df['season'].unique()
)

# Filter berdasarkan cuaca
selected_weather = st.sidebar.multiselect(
    "Pilih kondisi cuaca:",
    options=all_data_df['weather_desc'].unique(),
    default=all_data_df['weather_desc'].unique()
)

# Terapkan filter ke dataset
filtered_df = all_data_df[
    (all_data_df['date'] >= pd.to_datetime(start_date)) &
    (all_data_df['date'] <= pd.to_datetime(end_date)) &
    (all_data_df['season'].isin(selected_season)) &
    (all_data_df['weather_desc'].isin(selected_weather))
]

st.success(f"Menampilkan data dari **{start_date}** hingga **{end_date}** "
           f"({len(filtered_df)} baris setelah filter diterapkan).")

# ==============================
# 🌦️ RFM-Style Analysis Section
# ==============================
st.subheader("📊 Analisis RFM-Style")

# === Pertanyaan 1: Lonjakan Penyewaan (Recency)
st.markdown("### 🕒 Kapan terakhir kali terjadi lonjakan penyewaan sepeda yang signifikan?")
daily_total = filtered_df.groupby('date')['total'].sum().reset_index()
if not daily_total.empty:
    peak_day = daily_total.loc[daily_total['total'].idxmax()]
    st.write(f"📅 Lonjakan tertinggi terjadi pada **{peak_day['date'].date()}** "
             f"dengan total penyewaan **{peak_day['total']:,} sepeda.**")

    fig1, ax1 = plt.subplots(figsize=(10, 4))
    sns.lineplot(x='date', y='total', data=daily_total, color='blue')
    plt.axvline(peak_day['date'], color='red', linestyle='--', label='Puncak Tertinggi')
    plt.legend()
    plt.title('Tren Penyewaan Harian & Puncak Tertinggi')
    st.pyplot(fig1)
else:
    st.warning("Tidak ada data dalam rentang filter yang dipilih.")

# === Pertanyaan 2: Frekuensi Penyewaan antar Musim (Frequency)
st.markdown("### 🔁 Bagaimana perbandingan frekuensi penyewaan antar musim?")
if not filtered_df.empty:
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.boxplot(x='season', y='total', data=filtered_df, palette='Set2')
    plt.title('Distribusi Frekuensi Penyewaan per Musim')
    st.pyplot(fig2)

    season_avg = filtered_df.groupby('season')['total'].mean().sort_values(ascending=False)
    st.write("**Rata-rata penyewaan per musim:**")
    st.dataframe(season_avg)
else:
    st.warning("Tidak ada data untuk menampilkan perbandingan musim.")

# === Pertanyaan 3: Cuaca dengan Penyewaan Tertinggi (Monetary)
st.markdown("### 💰 Cuaca seperti apa yang menghasilkan total penyewaan tertinggi?")
if not filtered_df.empty:
    weather_total = filtered_df.groupby('weather_desc')['total'].sum().sort_values(ascending=False).reset_index()

    fig3, ax3 = plt.subplots(figsize=(8, 4))
    sns.barplot(x='total', y='weather_desc', data=weather_total, palette='coolwarm')
    plt.title('Total Penyewaan Berdasarkan Cuaca')
    st.pyplot(fig3)

    st.success(f"🌤️ {weather_total.iloc[0]['weather_desc']} — total "
               f"{int(weather_total.iloc[0]['total']):,} sepeda disewa.")
else:
    st.warning("Tidak ada data untuk menampilkan hasil cuaca.")
