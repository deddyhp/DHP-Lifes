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
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    df["Chol"] = pd.to_numeric(df["Chol"], errors="coerce")
    df["UA"] = pd.to_numeric(df["UA"], errors="coerce")
    df["Glucose"] = pd.to_numeric(df["Glucose"], errors="coerce")
    df = df.dropna(subset=["Nama", "Tanggal"])
    return df.sort_values(["Nama", "Tanggal"])

df = load_data()

st.title("❤️ DHP-Lifes")
st.caption("Health database membaca langsung dari Google Sheet")

menu = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "❤️ Health", "☕ Coffee Lab", "🚗 Mobility", "🕌 Islamic Things"]
)

def latest_card(data, nama):
    st.subheader(nama)
    if data.empty:
        st.warning("Belum ada data.")
        return
    latest = data.iloc[-1]
    st.metric("Chol terakhir", int(latest["Chol"]))
    st.metric("UA terakhir", latest["UA"])
    st.metric("Glucose terakhir", int(latest["Glucose"]))

if menu == "🏠 Home":
    st.header("Selamat pagi, Deddy & Family")
    st.success("DHP-Lifes V4 stabil aktif 🚀")

    c1, c2 = st.columns(2)
    with c1:
        latest_card(df[df["Nama"] == "Deddy"], "👤 Deddy")
    with c2:
        latest_card(df[df["Nama"] == "Istri"], "👩 Istri")

if menu == "❤️ Health":
    st.header("❤️ Health Dashboard")

    nama = st.selectbox("Pilih profil", sorted(df["Nama"].dropna().unique()))
    data = df[df["Nama"] == nama].copy()

    latest = data.iloc[-1]

    st.subheader(f"Ringkasan: {nama}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Chol terakhir", int(latest["Chol"]))
    c2.metric("UA terakhir", latest["UA"])
    c3.metric("Glucose terakhir", int(latest["Glucose"]))

    st.divider()

    st.subheader("📈 Trend Kolesterol")
    chol_chart = data[["Tanggal", "Chol"]].set_index("Tanggal")
    st.line_chart(chol_chart, height=260)

    st.subheader("📈 Trend Asam Urat")
    ua_chart = data[["Tanggal", "UA"]].set_index("Tanggal")
    st.line_chart(ua_chart, height=260)

    st.subheader("📈 Trend Glucose")
    glucose_chart = data[["Tanggal", "Glucose"]].set_index("Tanggal")
    st.line_chart(glucose_chart, height=260)

    st.divider()

    st.subheader("📋 Data Riwayat")
    st.dataframe(
        data.sort_values("Tanggal", ascending=False),
        use_container_width=True,
        hide_index=True
    )

if menu == "☕ Coffee Lab":
    st.header("☕ Coffee Lab")
    st.write("Nanti berisi log roasting, cupping, dan inventory green bean.")

if menu == "🚗 Mobility":
    st.header("🚗 Mobility")
    st.write("Nanti berisi catatan J6, Tiggo 8 CSH, servis, pajak, dan perjalanan.")

if menu == "🕌 Islamic Things":
    st.header("🕌 Islamic Things")
    st.write("Nanti berisi Glory Morning Quran, Afternoon Hadits, doa, dzikir, dan renungan.")
