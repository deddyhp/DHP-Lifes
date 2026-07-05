import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="DHP-Lifes",
    page_icon="❤️",
    layout="wide"
)

SHEET_ID = "1vEcgjWVTH5hSO-jYeI13BBD_1OFEPkiQpeENh2OfnjQ"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df["Chol"] = pd.to_numeric(df["Chol"], errors="coerce")
    df["UA"] = pd.to_numeric(df["UA"], errors="coerce")
    df["Glucose"] = pd.to_numeric(df["Glucose"], errors="coerce")
    return df.sort_values("Tanggal")

df = load_data()

st.title("❤️ DHP-Lifes")
st.caption("Dashboard keluarga untuk kesehatan, kopi, mobilitas, dan Islamic Things")

menu = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "❤️ Health", "☕ Coffee Lab", "🚗 Mobility", "🕌 Islamic Things"]
)

if menu == "🏠 Home":
    st.header("Selamat pagi, Deddy & Family")
    st.success("DHP-Lifes V3 aktif — Health database sudah membaca Google Sheet 🚀")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 Deddy")
        deddy = df[df["Nama"] == "Deddy"]
        if not deddy.empty:
            latest = deddy.iloc[-1]
            st.metric("Chol terakhir", int(latest["Chol"]))
            st.metric("UA terakhir", latest["UA"])
            st.metric("Glucose terakhir", int(latest["Glucose"]))

    with col2:
        st.subheader("👩 Istri")
        istri = df[df["Nama"] == "Istri"]
        if not istri.empty:
            latest = istri.iloc[-1]
            st.metric("Chol terakhir", int(latest["Chol"]))
            st.metric("UA terakhir", latest["UA"])
            st.metric("Glucose terakhir", int(latest["Glucose"]))

if menu == "❤️ Health":
    st.header("❤️ Health Dashboard")

    nama = st.selectbox("Pilih profil", sorted(df["Nama"].unique()))
    data = df[df["Nama"] == nama].copy()

    st.subheader(f"Ringkasan: {nama}")

    latest = data.iloc[-1]
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Chol terakhir", int(latest["Chol"]))
    with c2:
        st.metric("UA terakhir", latest["UA"])
    with c3:
        st.metric("Glucose terakhir", int(latest["Glucose"]))

    st.divider()

    st.subheader("📈 Grafik Tren")

    chart_data = data.set_index("Tanggal")[["Chol", "UA", "Glucose"]]

    st.line_chart(chart_data["Chol"])
    st.caption("Trend Kolesterol")

    st.line_chart(chart_data["UA"])
    st.caption("Trend Asam Urat")

    st.line_chart(chart_data["Glucose"])
    st.caption("Trend Glucose")

    st.divider()

    st.subheader("📋 Data Riwayat")
    st.dataframe(data, use_container_width=True)

if menu == "☕ Coffee Lab":
    st.header("☕ Coffee Lab")
    st.write("Nanti berisi log roasting, cupping, dan inventory green bean.")

if menu == "🚗 Mobility":
    st.header("🚗 Mobility")
    st.write("Nanti berisi catatan J6, Tiggo 8 CSH, servis, pajak, dan perjalanan.")

if menu == "🕌 Islamic Things":
    st.header("🕌 Islamic Things")
    st.write("Nanti berisi Glory Morning Quran, Afternoon Hadits, doa, dzikir, dan renungan.")
