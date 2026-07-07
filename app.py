import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import date

st.set_page_config(page_title="DHP-Lifes", page_icon="❤️", layout="wide")

APP_VERSION = "V12 STABLE CANDIDATE"
SHEET_ID = "1vEcgjWVTH5hSO-jYeI13BBD_1OFEPkiQpeENh2OfnjQ"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzG9Wf3MFQQegujmubT2NW_U53DdbuqPU22UrI43FVPl5FE8X-L_D9D8fuQ1k7pSITxow/exec"

st.markdown("""
<style>
.main .block-container {padding-top:1.1rem; max-width:1200px;}
[data-testid="stSidebar"] {min-width:280px;}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] div {
    font-size:1.22rem !important;
}
div[role="radiogroup"] label {font-size:1.30rem !important; padding:0.28rem 0;}
h1 {font-size:2.65rem !important; font-weight:850 !important;}
h2 {font-size:2.10rem !important; font-weight:800 !important;}
h3 {font-size:1.65rem !important; font-weight:760 !important;}
.dhp-card {
    border:1px solid rgba(128,128,128,.25);
    border-radius:22px;
    padding:22px;
    margin-bottom:18px;
    background:rgba(255,255,255,.04);
    box-shadow:0 4px 18px rgba(0,0,0,.08);
}
.dhp-profile-name {
    font-size:2.35rem;
    font-weight:900;
    letter-spacing:.02em;
    margin-bottom:.1rem;
}
.dhp-small {opacity:.75; font-size:.95rem;}
.dhp-version {
    padding:.25rem .7rem;
    border-radius:999px;
    border:1px solid rgba(128,128,128,.35);
    font-size:.9rem;
    opacity:.82;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(CSV_URL)
    required = ["Nama", "Tanggal", "Chol", "UA", "Glucose"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Kolom hilang di Google Sheet: {missing}")
        st.stop()
    df = df[required].copy()
    df["Nama"] = df["Nama"].astype(str).str.strip()
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    for col in ["Chol", "UA", "Glucose"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Nama", "Tanggal"]).sort_values(["Nama", "Tanggal"]).reset_index(drop=True)

def refresh_data():
    st.cache_data.clear()
    st.rerun()

def status_chol(v):
    if pd.isna(v): return "⚪ No data"
    if v < 200: return "🟢 Normal"
    if v < 240: return "🟡 Waspada"
    return "🔴 Tinggi"

def status_glucose(v):
    if pd.isna(v): return "⚪ No data"
    if v < 70: return "🔵 Very Low"
    if v < 100: return "🟢 Ideal"
    if v < 126: return "🟡 Waspada"
    return "🔴 Tinggi"

def status_ua(v, nama):
    if pd.isna(v): return "⚪ No data"
    if nama == "Istri":
        if v <= 6.0: return "🟢 Normal"
        if v <= 7.0: return "🟡 Waspada"
        return "🔴 Tinggi"
    if v <= 7.5: return "🟢 Normal"
    if v <= 8.0: return "🟡 Waspada"
    return "🔴 Tinggi"

def delta_value(data, col):
    clean = data.dropna(subset=[col])
    if len(clean) < 2: return None
    diff = clean.iloc[-1][col] - clean.iloc[-2][col]
    if diff == 0: return "0.0"
    return f"{diff:+.1f}"

def save_to_google_sheet(nama, tanggal, chol, ua, glucose):
    payload = {"Nama": nama, "Tanggal": str(tanggal), "Chol": int(chol), "UA": float(ua), "Glucose": int(glucose)}
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

def profile_name(nama):
    icon = "👤" if nama == "Deddy" else "👩"
    return f"{icon} {nama.upper()}"

def open_card(nama, data):
    last_update = "Belum ada data"
    if not data.empty:
        last_update = str(data.iloc[-1]["Tanggal"].date())
    st.markdown(f"""
    <div class="dhp-card">
      <div class="dhp-profile-name">{profile_name(nama)}</div>
      <div class="dhp-small">Last update: {last_update}</div>
    """, unsafe_allow_html=True)

def close_card():
    st.markdown("</div>", unsafe_allow_html=True)

def metric_cards(data, nama):
    if data.empty:
        st.warning(f"Belum ada data untuk {nama}.")
        return
    latest = data.iloc[-1]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Chol", int(latest["Chol"]), delta_value(data, "Chol"), delta_color="inverse")
        st.caption(status_chol(latest["Chol"]))
    with c2:
        st.metric("UA", latest["UA"], delta_value(data, "UA"), delta_color="inverse")
        st.caption(status_ua(latest["UA"], nama))
    with c3:
        st.metric("Glucose", int(latest["Glucose"]), delta_value(data, "Glucose"), delta_color="inverse")
        st.caption(status_glucose(latest["Glucose"]))

def health_insight(data, nama):
    if data.empty:
        return "Belum ada data."
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
            f"Glucose {latest['Glucose'] - prev['Glucose']:+.1f}. "
            "Untuk parameter ini, angka turun biasanya lebih baik selama tidak terlalu rendah."
        )
    return text

df = load_data()

st.title("❤️ DHP-Lifes")
st.caption("V12 STABLE CANDIDATE — Foundation Lock")
st.markdown(f'<span class="dhp-version">{APP_VERSION}</span>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "❤️ Health", "➕ Tambah Data", "🎯 Target", "⚙️ Settings", "☕ Coffee Lab", "🚗 Mobility", "🕌 Islamic Things"],
)

if st.sidebar.button("🔄 Refresh data"):
    refresh_data()

if menu == "🏠 Home":
    st.header("Home Dashboard")
    st.success("DHP-Lifes V12 Stable Candidate aktif — foundation lock running 🚀")
    col_left, col_right = st.columns(2)
    for container, nama in zip([col_left, col_right], ["Deddy", "Istri"]):
        with container:
            data = df[df["Nama"] == nama].copy()
            open_card(nama, data)
            metric_cards(data, nama)
            close_card()
    st.divider()
    st.subheader("📌 Database Status")
    st.write(f"Total data terbaca: **{len(df)} baris**")
    st.write(f"Profil: **{', '.join(sorted(df['Nama'].dropna().unique()))}**")
    st.caption("Sumber data: Google Sheet Health")

elif menu == "❤️ Health":
    st.header("Health Dashboard")
    nama = st.selectbox("Pilih profil", sorted(df["Nama"].dropna().unique()))
    data = df[df["Nama"] == nama].copy()
    if data.empty:
        st.warning("Belum ada data.")
        st.stop()
    open_card(nama, data)
    metric_cards(data, nama)
    st.caption("Delta: ↑ angka naik, ↓ angka turun. Warna hijau berarti arah membaik.")
    close_card()
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
    title_map = {"Chol": "Trend Kolesterol", "UA": "Trend Asam Urat", "Glucose": "Trend Glucose"}
    plot_metric(plot_data, metric, title_map[metric], nama)
    st.divider()
    st.subheader("📋 Data Riwayat")
    st.dataframe(data.sort_values("Tanggal", ascending=False), use_container_width=True, hide_index=True)

elif menu == "➕ Tambah Data":
    st.header("Tambah Data Pemeriksaan")
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
    st.header("Target & Rules")
    st.info("""
**Target dashboard:**

- Chol: 🟢 <200 Normal | 🟡 200–239 Waspada | 🔴 ≥240 Tinggi
- Glucose: 🔵 <70 Very Low | 🟢 70–99 Ideal | 🟡 100–125 Waspada | 🔴 ≥126 Tinggi
- UA Deddy: 🟢 ≤7.5 Normal | 🟡 7.6–8.0 Waspada | 🔴 >8.0 Tinggi
- UA Istri: 🟢 ≤6.0 Normal | 🟡 6.1–7.0 Waspada | 🔴 >7.0 Tinggi

**Delta color:**
- Angka naik ditampilkan merah untuk Chol, UA, dan Glucose.
- Angka turun ditampilkan hijau.
- Panah tetap menunjukkan arah data sebenarnya.
""")

elif menu == "⚙️ Settings":
    st.header("Settings")
    st.subheader("Application")
    st.write(f"Version: **{APP_VERSION}**")
    st.write("Database: **Google Sheet Health**")
    st.write("Write mode: **Google Apps Script Web App**")
    st.write("Status: **Foundation Lock Candidate**")
    st.divider()
    if st.button("Clear cache & refresh"):
        refresh_data()
    st.caption("V12 fokus mengunci fondasi sebelum modul Coffee Lab, Mobility, dan Islamic Things.")

elif menu == "☕ Coffee Lab":
    st.header("Coffee Lab")
    st.write("Foundation ready. Nanti berisi import Artisan, roast log, cupping, green bean, dan profile intelligence.")

elif menu == "🚗 Mobility":
    st.header("Mobility")
    st.write("Foundation ready. Nanti berisi J6, Tiggo 8 CSH, servis, pajak, charging, dan perjalanan.")

elif menu == "🕌 Islamic Things":
    st.header("Islamic Things")
    st.write("Foundation ready. Nanti berisi Glory Morning Quran, Afternoon Hadits, doa, dzikir, dan renungan.")
