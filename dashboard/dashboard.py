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
Sekarang dilengkapi dengan fitur **filter interaktif** berdasarkan tanggal dan musim.
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

# Ganti tipe data & kategori musim
all_data_df['season'] = all_data_df['season'].astype('category')
all_data_df['season'] = all_data_df['season'].cat.rename_categories({
    1: 'Winter',
    2: 'Spring',
    3: 'Summer',
    4: 'Autumn'
})

# Konversi tanggal ke datetime
all_data_df['date'] = pd.to_datetime(all_data_df['date'])

# ==============================
# 🎛️ Fitur Interaktif: Filter
# ==============================
st.sidebar.header("🔍 Filter Data")

# Pilih rentang tanggal
min_date = all_data_df['date'].min()
max_date = all_data_df['date'].max()
date_range = st.sidebar.date_input(
    "Pilih rentang tanggal:",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Pilih musim
selected_season = st.sidebar.multiselect(
    "Pilih musim:",
    options=all_data_df['season'].unique(),
    default=all_data_df['season'].unique()
)

# Terapkan filter
filtered_df = all_data_df[
    (all_data_df['date'] >= pd.to_datetime(date_range[0])) &
    (all_data_df['date'] <= pd.to_datetime(date_range[1])) &
    (all_data_df['season'].isin(selected_season))
]

# ==============================
# 🌦️ RFM-Style Analysis Section
# ==============================
st.subheader("📊 Analisis RFM-Style")

# === Pertanyaan 1: Lonjakan Penyewaan (Recency)
st.markdown("### 🕒 Kapan terakhir kali terjadi lonjakan penyewaan sepeda yang signifikan?")

daily_total = filtered_df.groupby('date')['total'].sum().reset_index()
peak_day = daily_total.loc[daily_total['total'].idxmax()]

st.write(f"📅 Lonjakan tertinggi terjadi pada **{peak_day['date'].date()}** dengan total penyewaan **{peak_day['total']:,} sepeda.**")

fig1, ax1 = plt.subplots(figsize=(10, 4))
sns.lineplot(x='date', y='total', data=daily_total, color='teal')
plt.axvline(peak_day['date'], color='red', linestyle='--', label='Puncak Tertinggi')
plt.legend()
plt.title('Tren Penyewaan Harian & Puncak Tertinggi')
st.pyplot(fig1)

# === Pertanyaan 2: Frekuensi Penyewaan antar Musim (Frequency)
st.markdown("### 🔁 Bagaimana perbandingan frekuensi penyewaan antar musim?")
fig2, ax2 = plt.subplots(figsize=(8, 4))
sns.boxplot(x='season', y='total', data=filtered_df, palette='Blues')
plt.title('Distribusi Frekuensi Penyewaan per Musim')
st.pyplot(fig2)

season_avg = filtered_df.groupby('season')['total'].mean().sort_values(ascending=False)
st.write("**Rata-rata penyewaan per musim:**")
st.dataframe(season_avg)

# === Pertanyaan 3: Cuaca dengan Penyewaan Tertinggi (Monetary)
st.markdown("### 💰 Cuaca seperti apa yang menghasilkan total penyewaan tertinggi?")
weather_map = {
    1: 'Clear / Partly Cloudy',
    2: 'Mist / Cloudy',
    3: 'Light Rain / Snow',
    4: 'Heavy Rain / Fog'
}
filtered_df['weather_desc'] = filtered_df['weathersit'].map(weather_map)
weather_total = filtered_df.groupby('weather_desc')['total'].sum().sort_values(ascending=False).reset_index()

fig3, ax3 = plt.subplots(figsize=(8, 4))
sns.barplot(x='total', y='weather_desc', data=weather_total, palette='Blues')
plt.title('Total Penyewaan Berdasarkan Cuaca')
st.pyplot(fig3)

st.write("**Kondisi cuaca dengan total penyewaan tertinggi:**")
st.success(f"{weather_total.iloc[0]['weather_desc']} — total {int(weather_total.iloc[0]['total']):,} sepeda disewa.")
