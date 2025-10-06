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
""")

# ==============================
# 📦 Load Data
# ==============================
all_data_df = pd.read_csv('all_data.csv')

# ==============================
# 🧹 Data Cleaning
# ==============================
st.subheader("🧹 Data Cleaning")

# Rename kolom
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

# Info missing & duplicate
st.write("**Cek Missing Values:**")
st.write(all_data_df.isna().sum())
st.write("**Cek Duplikasi:**", all_data_df.duplicated().sum(), "baris duplikat ditemukan.")

# ==============================
# 🌦️ RFM-Style Analysis Section
# ==============================
st.subheader("📊 Analisis RFM-Style")

# === Pertanyaan 1: Lonjakan Penyewaan (Recency)
st.markdown("### 🕒 Kapan terakhir kali terjadi lonjakan penyewaan sepeda yang signifikan?")
daily_total = all_data_df.groupby('date')['total'].sum().reset_index()
daily_total['date'] = pd.to_datetime(daily_total['date'])
peak_day = daily_total.loc[daily_total['total'].idxmax()]

st.write(f"📅 Lonjakan tertinggi terjadi pada **{peak_day['date'].date()}** dengan total penyewaan **{peak_day['total']:,} sepeda.**")

fig1, ax1 = plt.subplots(figsize=(10, 4))
sns.lineplot(x='date', y='total', data=daily_total, color='blue')
plt.axvline(peak_day['date'], color='red', linestyle='--', label='Puncak Tertinggi')
plt.legend()
plt.title('Tren Penyewaan Harian & Puncak Tertinggi')
st.pyplot(fig1)

# === Pertanyaan 2: Frekuensi Penyewaan antar Musim (Frequency)
st.markdown("### 🔁 Bagaimana perbandingan frekuensi penyewaan antar musim?")
fig2, ax2 = plt.subplots(figsize=(8, 4))
sns.boxplot(x='season', y='total', data=all_data_df, palette='Set2')
plt.title('Distribusi Frekuensi Penyewaan per Musim')
st.pyplot(fig2)

season_avg = all_data_df.groupby('season')['total'].mean().sort_values(ascending=False)
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
all_data_df['weather_desc'] = all_data_df['weathersit'].map(weather_map)
weather_total = all_data_df.groupby('weather_desc')['total'].sum().sort_values(ascending=False).reset_index()

fig3, ax3 = plt.subplots(figsize=(8, 4))
sns.barplot(x='total', y='weather_desc', data=weather_total, palette='coolwarm')
plt.title('Total Penyewaan Berdasarkan Cuaca')
st.pyplot(fig3)

st.write("**Kondisi cuaca dengan total penyewaan tertinggi:**")
st.success(f"{weather_total.iloc[0]['weather_desc']} — total {int(weather_total.iloc[0]['total']):,} sepeda disewa.")
