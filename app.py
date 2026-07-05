import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import date

st.set_page_config(page_title="DHP-Lifes", page_icon="❤️", layout="wide")

APP_VERSION = "V11 FINAL"
SHEET_ID = "1vEcgjWVTH5hSO-jYeI13BBD_1OFEPkiQpeENh2OfnjQ"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzG9Wf3MFQQegujmubT2NW_U53DdbuqPU22UrI43FVPl5FE8X-L_D9D8fuQ1k7pSITxow/exec"

@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(CSV_URL)
    required_cols = ["Nama", "Tanggal", "Chol", "UA", "Glucose"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"Kolom hilang di Google Sheet: {missing}")
        st.stop()

    df = df[required_cols].copy()
    df["Nama"] = df["Nama"].astype(str).str.strip()
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")

    for col in ["Chol", "UA", "Glucose"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["Nama", "Tanggal"]).sort_values(["Nama", "Tanggal"]).reset_index(drop=True)

def refresh_data():
    st.cache_data.clear()
    st.rerun()

def status_chol(v):
    if pd.isna(v):
        return "⚪ No data"
    if v < 200:
        return "🟢 Normal"
    if v < 240:
        return "🟡 Waspada"
    return "🔴 Tinggi"

def status_glucose(v):
    if pd.isna(v):
        return "⚪ No data"
    if v < 70:
        return "🔵 Very Low"
    if v < 100:
        return "🟢 Ideal"
    if v < 126:
        return "🟡 Waspada"
    return "🔴 Tinggi"

def status_ua(v, nama):
    if pd.isna(v):
        return "⚪ No data"
    if nama == "Istri":
        if v <= 6.0:
            return "🟢 Normal"
        if v <= 7.0:
            return "🟡 Waspada"
        return "🔴 Tinggi"
    if v <= 7.5:
        return "🟢 Normal"
    if v <= 8.0:
        return "🟡 Waspada"
    return "🔴 Tinggi"

def delta_text(data, col):
    clean = data.dropna(subset=[col])
    if len(clean) < 2:
        return None
    diff = clean.iloc[-1][col] - clean.iloc[-2][col]
    if diff > 0:
        return f"Naik {diff:.1f}"
    if diff < 0:
        return f"Turun {abs(diff):.1f}"
    return "Tetap"

def save_to_google_sheet(nama, tanggal, chol, ua, glucose):
    payload = {
        "Nama": nama,
        "Tanggal": str(tanggal),
        "Chol": int(chol),
        "UA": float(ua),
        "Glucose": int(glucose),
    }

    try:
        r = requests.post(APPS_SCRIPT_URL, json=payload, timeout=20)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}: {r.text[:250]}"

        try:
            result = r.json()
        except Exception:
            st.cache_data.clear()
            return True, "Data terkirim. Respons bukan JSON, tapi request berhasil."

        if result.get("status") == "success":
            st.cache_data.clear()
            return True, "Data berhasil disimpan ke Google Sheet."

        return False, f"Apps Script error: {result}"

    except Exception as e:
        return False, f"Gagal konek ke Apps Script: {e}"

def plot_metric(data, metric, title, nama):
    chart = data.dropna(subset=[metric]).copy()
    if chart.empty:
        st.warning(f"Belum ada data untuk {metric}.")
        return

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(chart["Tanggal"], chart[metric], marker="o", linewidth=2)
    ax.set_title(title)
    ax.set_xlabel("Tanggal")
    ax.set_ylabel(metric)
    ax.grid(True, alpha=0.3)

    if metric == "Chol":
        ax.axhline(200, linestyle="--", alpha=0.5)
    elif metric == "Glucose":
        ax.axhline(70, linestyle="--", alpha=0.4)
        ax.axhline(100, linestyle="--", alpha=0.5)
        ax.axhline(126, linestyle="--", alpha=0.5)
    elif metric == "UA":
        ax.axhline(6.0 if nama == "Istri" else 7.5, linestyle="--", alpha=0.5)

    fig.autofmt_xdate()
    st.pyplot(fig)
    plt.close(fig)

def metric_cards(data, nama):
    latest = data.iloc[-1]
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Chol", int(latest["Chol"]), delta_text(data, "Chol"))
        st.caption(status_chol(latest["Chol"]))

    with c2:
        st.metric("UA", latest["UA"], delta_text(data, "UA"))
        st.caption(status_ua(latest["UA"], nama))

    with c3:
        st.metric("Glucose", int(latest["Glucose"]), delta_text(data, "Glucose"))
        st.caption(status_glucose(latest["Glucose"]))

def health_insight(data, nama):
    latest = data.iloc[-1]
    text = (
        f"Data terakhir {nama} tanggal {latest['Tanggal'].date()}: "
        f"Chol {int(latest['Chol'])} ({status_chol(latest['Chol'])}), "
        f"UA {latest['UA']} ({status_ua(latest['UA'], nama)}), "
        f"Glucose {int(latest['Glucose'])} ({status_glucose(latest['Glucose'])})."
    )

    if len(data) >= 2:
        prev = data.iloc[-2]
        text += (
            "\n\nPerubahan dari pemeriksaan sebelumnya: "
            f"Chol {latest['Chol'] - prev['Chol']:+.1f}, "
            f"UA {latest['UA'] - prev['UA']:+.1f}, "
            f"Glucose {latest['Glucose'] - prev['Glucose']:+.1f}."
        )
    return text

df = load_data()

st.title("❤️ DHP-Lifes")
st.caption("V11 FINAL — Health database + direct Google Sheet auto-save")

menu = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "❤️ Health", "➕ Tambah Data", "🎯 Target", "☕ Coffee Lab", "🚗 Mobility", "🕌 Islamic Things"],
)

if st.sidebar.button("🔄 Refresh data"):
    refresh_data()

if menu == "🏠 Home":
    st.header("Selamat datang, Deddy & Family")
    st.success("DHP-Lifes V11 FINAL aktif — auto-save ready 🚀")

    col_left, col_right = st.columns(2)
    for container, nama in zip([col_left, col_right], ["Deddy", "Istri"]):
        with container:
            data = df[df["Nama"] == nama].copy()
            st.subheader(("👤 " if nama == "Deddy" else "👩 ") + nama)
            if data.empty:
                st.warning("Belum ada data.")
            else:
                metric_cards(data, nama)

    st.divider()
    st.subheader("📌 Database Status")
    st.write(f"Total data terbaca: **{len(df)} baris**")
    st.write(f"Profil: **{', '.join(sorted(df['Nama'].dropna().unique()))}**")
    st.caption("Sumber data: Google Sheet Health")

elif menu == "❤️ Health":
    st.header("❤️ Health Dashboard")

    nama = st.selectbox("Pilih profil", sorted(df["Nama"].dropna().unique()))
    data = df[df["Nama"] == nama].copy()

    if data.empty:
        st.warning("Belum ada data.")
        st.stop()

    st.subheader(f"Ringkasan: {nama}")
    metric_cards(data, nama)

    st.divider()
    st.subheader("📌 Insight Singkat")
    st.info(health_insight(data, nama))

    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        metric = st.radio("Pilih grafik", ["Chol", "UA", "Glucose"], horizontal=True)
    with c2:
        rentang = st.selectbox("Rentang data", ["Semua", "10 data terakhir", "20 data terakhir"])

    plot_data = data.copy()
    if rentang == "10 data terakhir":
        plot_data = plot_data.tail(10)
    elif rentang == "20 data terakhir":
        plot_data = plot_data.tail(20)

    title_map = {
        "Chol": "Trend Kolesterol",
        "UA": "Trend Asam Urat",
        "Glucose": "Trend Glucose",
    }
    plot_metric(plot_data, metric, title_map[metric], nama)

    st.divider()
    st.subheader("📋 Data Riwayat")
    st.dataframe(data.sort_values("Tanggal", ascending=False), use_container_width=True, hide_index=True)

elif menu == "➕ Tambah Data":
    st.header("➕ Tambah Data Pemeriksaan")
    st.success("Mode auto-save aktif. Data akan langsung masuk ke Google Sheet.")

    nama = st.selectbox("Nama", ["Deddy", "Istri"])
    tanggal = st.date_input("Tanggal", date.today())

    c1, c2, c3 = st.columns(3)
    with c1:
        chol = st.number_input("Chol", min_value=0, step=1, value=0)
        st.caption(status_chol(chol))
    with c2:
        ua = st.number_input("UA", min_value=0.0, step=0.1, value=0.0)
        st.caption(status_ua(ua, nama))
    with c3:
        glucose = st.number_input("Glucose", min_value=0, step=1, value=0)
        st.caption(status_glucose(glucose))

    st.divider()
    st.write(f"Preview: **{nama} | {tanggal} | Chol {chol} | UA {ua} | Glucose {glucose}**")

    if st.button("💾 Simpan ke Google Sheet"):
        if chol == 0 and ua == 0 and glucose == 0:
            st.error("Data masih kosong. Isi nilai pemeriksaan dulu.")
        else:
            ok, msg = save_to_google_sheet(nama, tanggal, chol, ua, glucose)
            if ok:
                st.success(msg)
                st.info("Klik Refresh data di sidebar atau tunggu 30 detik lalu refresh halaman.")
            else:
                st.error(msg)

    st.divider()
    st.subheader("Backup manual")
    st.code(f"{nama}\t{tanggal}\t{chol}\t{ua}\t{glucose}")

elif menu == "🎯 Target":
    st.header("🎯 Target & Rules")
    st.info(
        """
**Target dashboard:**

- Chol: 🟢 <200 Normal | 🟡 200–239 Waspada | 🔴 ≥240 Tinggi
- Glucose: 🔵 <70 Very Low | 🟢 70–99 Ideal | 🟡 100–125 Waspada | 🔴 ≥126 Tinggi
- UA Deddy: 🟢 ≤7.5 Normal | 🟡 7.6–8.0 Waspada | 🔴 >8.0 Tinggi
- UA Istri: 🟢 ≤6.0 Normal | 🟡 6.1–7.0 Waspada | 🔴 >7.0 Tinggi
        """
    )

elif menu == "☕ Coffee Lab":
    st.header("☕ Coffee Lab")
    st.write("Nanti berisi log roasting, cupping, inventory green bean, dan profil Pagerwatu.")

elif menu == "🚗 Mobility":
    st.header("🚗 Mobility")
    st.write("Nanti berisi catatan J6, Tiggo 8 CSH, servis, pajak, charging, dan perjalanan.")

elif menu == "🕌 Islamic Things":
    st.header("🕌 Islamic Things")
    st.write("Nanti berisi Glory Morning Quran, Afternoon Hadits, doa, dzikir, dan renungan.")
