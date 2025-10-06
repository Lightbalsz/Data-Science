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

# Ubah kategori musim
all_data_df['season'] = all_data_df['season'].astype('category')
all_data_df['season'] = all_data_df['season'].cat.rename_categories({
    1: 'Winter',
    2: 'Spring',
    3: 'Summer',
    4: 'Autumn'
})

# Mapping cuaca ke Bahasa Indonesia
weather_map = {
    1: 'Cerah / Sedikit Berawan',
    2: 'Berkabut / Berawan',
    3: 'Hujan Ringan / Salju Ringan',
    4: 'Hujan Lebat / Badai / Kabut'
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
# === 1️⃣ Bagaimana tren penyewaan sepeda berubah berdasarkan musim, cuaca, atau waktu?
st.markdown("### 🌤️ Bagaimana tren penyewaan sepeda berubah berdasarkan musim, cuaca, atau waktu?")
if not filtered_df.empty:
    df = filtered_df[['season', 'casual', 'registered']]
    melted_df = pd.melt(df, id_vars='season', var_name='status', value_name='sewa per hari')

    fig4, ax4 = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=melted_df, x='season', y='sewa per hari', hue='status', showfliers=False, palette='Set2')
    plt.title('Perbandingan Sewa Sepeda per Musim antara Pengguna Casual & Registered')
    st.pyplot(fig4)
else:
    st.warning("Tidak ada data yang tersedia untuk analisis tren musiman dan status pengguna.")

# === 2️⃣ Bagaimana pengaruh penyewaan sepeda terhadap hari kerja dengan hari libur?
st.markdown("### 🗓️ Bagaimana pengaruh penyewaan sepeda terhadap hari kerja dengan hari libur?")
if not filtered_df.empty:
    mask1 = ((filtered_df['workingday'] == 0) | (filtered_df['holiday'] == 1))
    df1 = filtered_df[mask1]

    mask2 = ((filtered_df['workingday'] == 1) & (filtered_df['holiday'] == 0))
    df2 = filtered_df[mask2]

    columns = ['total', 'casual', 'registered']
    color_palette = sns.color_palette("Set2")

    fig5, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)

    # Hari libur
    for i, col in enumerate(columns):
        sns.lineplot(x='hour', y=col, data=df1, label=col, color=color_palette[i], ax=axes[0])
    axes[0].set_title('Sewa Sepeda di Hari Libur')
    axes[0].set_xlabel('Jam')
    axes[0].set_ylabel('Jumlah Penyewa')
    axes[0].legend()

    # Hari kerja
    for i, col in enumerate(columns):
        sns.lineplot(x='hour', y=col, data=df2, label=col, color=color_palette[i], ax=axes[1])
    axes[1].set_title('Sewa Sepeda pada Hari Kerja')
    axes[1].set_xlabel('Jam')
    axes[1].set_ylabel('Jumlah Penyewa')
    axes[1].legend()

    plt.tight_layout()
    st.pyplot(fig5)
else:
    st.warning("Tidak ada data yang tersedia untuk analisis hari kerja dan hari libur.")

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
    sns.lineplot(x='date', y='total', data=daily_total, color='steelblue')
    plt.axvline(peak_day['date'], color='red', linestyle='--', label='Puncak Tertinggi')
    plt.legend()
    plt.title('Tren Penyewaan Harian & Puncak Tertinggi')
    st.pyplot(fig1)
else:
    st.warning("Tidak ada data dalam rentang filter yang dipilih.")

# === Pertanyaan 2: Frekuensi Penyewaan antar Musim (Frequency)
st.markdown("### 🔁 Bagaimana perbandingan frekuensi penyewaan antar musim?")
if not filtered_df.empty:
    season_freq = filtered_df.groupby('season')['total'].mean().sort_values(ascending=False)

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    season_freq.plot(kind='bar', color='orange', ax=ax2)
    plt.title('Frequency: Rata-rata Penyewaan per Musim')
    plt.ylabel('Rata-rata Penyewaan')
    plt.xlabel('Musim')
    st.pyplot(fig2)

    st.write("**Rata-rata penyewaan per musim:**")
    st.dataframe(season_freq)
else:
    st.warning("Tidak ada data untuk menampilkan perbandingan musim.")

# === Pertanyaan 3: Cuaca dengan Penyewaan Tertinggi (Monetary)
st.markdown("### 💰 Cuaca seperti apa yang menghasilkan total penyewaan tertinggi?")
if not filtered_df.empty:
    weather_total = filtered_df.groupby('weather_desc')['total'].sum().sort_values(ascending=False)

    fig3, ax3 = plt.subplots(figsize=(8, 4))
    weather_total.plot(kind='bar', color='skyblue', ax=ax3)
    plt.title('Monetary: Total Penyewaan per Kondisi Cuaca')
    plt.ylabel('Total Penyewaan')
    plt.xlabel('Kondisi Cuaca')
    st.pyplot(fig3)

    top_weather = weather_total.index[0]
    top_value = weather_total.iloc[0]
    st.success(f"🌤️ {top_weather} — total {int(top_value):,} sepeda disewa.")
else:
    st.warning("Tidak ada data untuk menampilkan hasil cuaca.")