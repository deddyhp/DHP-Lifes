import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import date

# ============================================================
# DHP-Lifes V10
# - Read database from Google Sheet public CSV
# - Write new health data via Google Apps Script Web App
# ============================================================

st.set_page_config(
    page_title="DHP-Lifes",
    page_icon="❤️",
    layout="wide"
)

SHEET_ID = "1vEcgjWVTH5hSO-jYeI13BBD_1OFEPkiQpeENh2OfnjQ"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# NANTI DIISI setelah Google Apps Script Web App jadi.
# Contoh: "https://script.google.com/macros/s/AKfycbxxxxx/exec"
APPS_SCRIPT_URL = ""

@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(CSV_URL)

    required_cols = ["Nama", "Tanggal", "Chol", "UA", "Glucose"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"Kolom hilang di Google Sheet: {missing}")
        st.stop()

    df["Nama"] = df["Nama"].astype(str).str.strip()
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")

    for col in ["Chol", "UA", "Glucose"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["Nama", "Tanggal"]).sort_values(["Nama", "Tanggal"]).reset_index(drop=True)

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

def latest_row(data):
    if data.empty:
        return None
    return data.iloc[-1]

def plot_metric(data, metric, title):
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
        ax.axhline(7.5, linestyle="--", alpha=0.5)

    fig.autofmt_xdate()
    st.pyplot(fig)
    plt.close(fig)

def person_icon(nama):
    return "👤" if nama == "Deddy" else "👩"

def metric_cards(data, nama):
    latest = latest_row(data)
    if latest is None:
        st.warning(f"Belum ada data untuk {nama}.")
        return

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
    latest = latest_row(data)
    if latest is None:
        return "Belum ada data."

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

def save_to_google_sheet(nama, tanggal, chol, ua, glucose):
    if not APPS_SCRIPT_URL:
        return False, "APPS_SCRIPT_URL belum diisi di app.py."

    payload = {
        "Nama": nama,
        "Tanggal": str(tanggal),
        "Chol": int(chol),
        "UA": float(ua),
        "Glucose": int(glucose),
    }

    try:
        r = requests.post(APPS_SCRIPT_URL, json=payload, timeout=15)
        if r.status_code == 200:
            try:
                result = r.json()
                if result.get("status") == "success":
                    st.cache_data.clear()
                    return True, "Data berhasil disimpan ke Google Sheet."
                return False, str(result)
            except Exception:
                return True, "Data terkirim. Refresh dashboard dalam 30 detik."
        return False, f"HTTP error: {r.status_code} - {r.text[:200]}"
    except Exception as e:
        return False, f"Gagal konek ke Apps Script: {e}"

df = load_data()

st.title("❤️ DHP-Lifes")
st.caption("V10 — Google Sheet database + auto-save via Google Apps Script")

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Home",
        "❤️ Health",
        "➕ Tambah Data",
        "☕ Coffee Lab",
        "🚗 Mobility",
        "🕌 Islamic Things",
    ],
)

if menu == "🏠 Home":
    st.header("Selamat datang, Deddy & Family")
    st.success("DHP-Lifes V10 aktif 🚀")

    col_left, col_right = st.columns(2)

    for container, nama in zip([col_left, col_right], ["Deddy", "Istri"]):
        with container:
            data = df[df["Nama"] == nama].copy()
            st.subheader(f"{person_icon(nama)} {nama}")
            metric_cards(data, nama)

    st.divider()
    st.subheader("📌 Database Status")
    st.write(f"Total data terbaca: **{len(df)} baris**")
    st.write(f"Profil: **{', '.join(sorted(df['Nama'].dropna().unique()))}**")

elif menu == "❤️ Health":
    st.header("❤️ Health Dashboard")

    nama = st.selectbox("Pilih profil", sorted(df["Nama"].dropna().unique()))
    data = df[df["Nama"] == nama].copy()

    if data.empty:
        st.warning("Belum ada data.")
        st.stop()

    st.subheader(f"{person_icon(nama)} Ringkasan: {nama}")
    metric_cards(data, nama)

    st.divider()
    st.subheader("📌 Insight Singkat")
    st.info(health_insight(data, nama))

    st.divider()

    c_filter1, c_filter2 = st.columns(2)
    with c_filter1:
        metric = st.radio("Pilih grafik", ["Chol", "UA", "Glucose"], horizontal=True)
    with c_filter2:
        tampil = st.selectbox("Rentang data", ["Semua", "10 data terakhir", "20 data terakhir"])

    plot_data = data.copy()
    if tampil == "10 data terakhir":
        plot_data = plot_data.tail(10)
    elif tampil == "20 data terakhir":
        plot_data = plot_data.tail(20)

    title_map = {
        "Chol": "Trend Kolesterol",
        "UA": "Trend Asam Urat",
        "Glucose": "Trend Glucose",
    }

    plot_metric(plot_data, metric, title_map[metric])

    st.divider()
    st.subheader("📋 Data Riwayat")
    st.dataframe(
        data.sort_values("Tanggal", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

elif menu == "➕ Tambah Data":
    st.header("➕ Tambah Data Pemeriksaan")

    if APPS_SCRIPT_URL:
        st.success("Mode auto-save aktif. Data akan langsung masuk ke Google Sheet.")
    else:
        st.warning("APPS_SCRIPT_URL belum diisi. Mode auto-save belum aktif.")

    nama = st.selectbox("Nama", ["Deddy", "Istri"])
    tanggal = st.date_input("Tanggal", date.today())

    c1, c2, c3 = st.columns(3)
    with c1:
        chol = st.number_input("Chol", min_value=0, step=1)
        st.caption(status_chol(chol))
    with c2:
        ua = st.number_input("UA", min_value=0.0, step=0.1)
        st.caption(status_ua(ua, nama))
    with c3:
        glucose = st.number_input("Glucose", min_value=0, step=1)
        st.caption(status_glucose(glucose))

    st.divider()

    if st.button("💾 Simpan ke Google Sheet"):
        ok, msg = save_to_google_sheet(nama, tanggal, chol, ua, glucose)
        if ok:
            st.success(msg)
            st.info("Tunggu 30-60 detik lalu refresh dashboard jika data belum terlihat.")
        else:
            st.error(msg)

    st.subheader("Backup manual")
    row_tab = f"{nama}\t{tanggal}\t{chol}\t{ua}\t{glucose}"
    st.code(row_tab)

elif menu == "☕ Coffee Lab":
    st.header("☕ Coffee Lab")
    st.write("Nanti berisi log roasting, cupping, inventory green bean, dan profil Pagerwatu.")

elif menu == "🚗 Mobility":
    st.header("🚗 Mobility")
    st.write("Nanti berisi catatan J6, Tiggo 8 CSH, servis, pajak, charging, dan perjalanan.")

elif menu == "🕌 Islamic Things":
    st.header("🕌 Islamic Things")
    st.write("Nanti berisi Glory Morning Quran, Afternoon Hadits, doa, dzikir, dan renungan.")
