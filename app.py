import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

def plot_metric(data, metric, title):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data["Tanggal"], data[metric], marker="o")
    ax.set_title(title)
    ax.set_xlabel("Tanggal")
    ax.set_ylabel(metric)
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    st.pyplot(fig)
    plt.close(fig)

df = load_data()

st.title("❤️ DHP-Lifes")
st.caption("Health database membaca langsung dari Google Sheet")

menu = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "❤️ Health", "☕ Coffee Lab", "🚗 Mobility", "🕌 Islamic Things"]
)

if menu == "🏠 Home":
    st.header("Selamat pagi, Deddy & Family")
    st.success("DHP-Lifes V5 Matplotlib aktif 🚀")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("👤 Deddy")
        deddy = df[df["Nama"] == "Deddy"]
        latest = deddy.iloc[-1]
        st.metric("Chol terakhir", int(latest["Chol"]))
        st.metric("UA terakhir", latest["UA"])
        st.metric("Glucose terakhir", int(latest["Glucose"]))

    with c2:
        st.subheader("👩 Istri")
        istri = df[df["Nama"] == "Istri"]
        latest = istri.iloc[-1]
        st.metric("Chol terakhir", int(latest["Chol"]))
        st.metric("UA terakhir", latest["UA"])
        st.metric("Glucose terakhir", int(latest["Glucose"]))

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

    st.subheader("📈 Grafik Tren")
    plot_metric(data, "Chol", "Trend Kolesterol")
    plot_metric(data, "UA", "Trend Asam Urat")
    plot_metric(data, "Glucose", "Trend Glucose")

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
