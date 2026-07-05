import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="DHP-Lifes", page_icon="❤️", layout="wide")

SHEET_ID = "1vEcgjWVTH5hSO-jYeI13BBD_1OFEPkiQpeENh2OfnjQ"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    for col in ["Chol", "UA", "Glucose"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Nama", "Tanggal"])
    return df.sort_values(["Nama", "Tanggal"])

def status_chol(v):
    if v < 200:
        return "🟢 Normal"
    if v < 240:
        return "🟡 Waspada"
    return "🔴 Tinggi"

def status_ua(v):
    if v <= 7.5:
        return "🟢 Normal"
    return "🔴 Tinggi"

def status_glucose(v):
    if v <= 100:
        return "🟢 Normal"
    if v <= 125:
        return "🟡 Waspada"
    return "🔴 Tinggi"

def delta_text(data, col):
    if len(data) < 2:
        return "Belum ada pembanding"
    now = data.iloc[-1][col]
    prev = data.iloc[-2][col]
    diff = now - prev
    if diff > 0:
        return f"Naik {diff:.1f}"
    if diff < 0:
        return f"Turun {abs(diff):.1f}"
    return "Tetap"

def plot_metric(data, metric, title):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data["Tanggal"], data[metric], marker="o", linewidth=2)
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
    st.success("DHP-Lifes V6 Health Status aktif 🚀")

    c1, c2 = st.columns(2)

    for col, nama in zip([c1, c2], ["Deddy", "Istri"]):
        with col:
            data = df[df["Nama"] == nama]
            latest = data.iloc[-1]
            st.subheader(f"{'👤' if nama == 'Deddy' else '👩'} {nama}")
            st.metric("Chol", int(latest["Chol"]), delta_text(data, "Chol"))
            st.write(status_chol(latest["Chol"]))
            st.metric("UA", latest["UA"], delta_text(data, "UA"))
            st.write(status_ua(latest["UA"]))
            st.metric("Glucose", int(latest["Glucose"]), delta_text(data, "Glucose"))
            st.write(status_glucose(latest["Glucose"]))

if menu == "❤️ Health":
    st.header("❤️ Health Dashboard")

    nama = st.selectbox("Pilih profil", sorted(df["Nama"].dropna().unique()))
    data = df[df["Nama"] == nama].copy()
    latest = data.iloc[-1]

    st.subheader(f"Ringkasan: {nama}")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Chol terakhir", int(latest["Chol"]), delta_text(data, "Chol"))
        st.write(status_chol(latest["Chol"]))
    with c2:
        st.metric("UA terakhir", latest["UA"], delta_text(data, "UA"))
        st.write(status_ua(latest["UA"]))
    with c3:
        st.metric("Glucose terakhir", int(latest["Glucose"]), delta_text(data, "Glucose"))
        st.write(status_glucose(latest["Glucose"]))

    st.divider()

    st.subheader("📌 Insight Singkat")
    st.info(
        f"""
        Data terakhir {nama}: Chol {int(latest['Chol'])}, UA {latest['UA']}, Glucose {int(latest['Glucose'])}.
        Chol: {status_chol(latest['Chol'])} | UA: {status_ua(latest['UA'])} | Glucose: {status_glucose(latest['Glucose'])}
        """
    )

    st.divider()

    metric = st.radio(
        "Pilih grafik",
        ["Chol", "UA", "Glucose"],
        horizontal=True
    )

    title_map = {
        "Chol": "Trend Kolesterol",
        "UA": "Trend Asam Urat",
        "Glucose": "Trend Glucose"
    }

    plot_metric(data, metric, title_map[metric])

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
