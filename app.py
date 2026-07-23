import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

st.set_page_config(page_title="DHP-Lifes", page_icon="❤️", layout="wide", initial_sidebar_state="collapsed")

APP_VERSION = "V13.3 MOBILE UI"
SHEET_ID = "1vEcgjWVTH5hSO-jYeI13BBD_1OFEPkiQpeENh2OfnjQ"
HEALTH_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Health"
ISLAMIC_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Islamic"

HEALTH_API_URL = "https://script.google.com/macros/s/AKfycbzG9Wf3MFQQegujmubT2NW_U53DdbuqPU22UrI43FVPl5FE8X-L_D9D8fuQ1k7pSITxow/exec"
ISLAMIC_API_URL = "https://script.google.com/macros/s/AKfycbyblLjqJ6iF383GdW-n3ZpS3UQUvLdFK3891F7thZobeyMFLjXPSJDAx1x4a3-j4gInBw/exec"
DEFAULT_TIMEZONE = "Asia/Jakarta"

st.markdown("""
<style>
:root {--dhp-bg:#fbfaf8;--dhp-card:rgba(255,255,255,.96);--dhp-text:#242736;--dhp-muted:#767986;--dhp-line:#ece8e4;--dhp-pink:#ef4f78;--dhp-pink-soft:#fff0f4;--dhp-gold:#d99535;--dhp-gold-soft:#fff8eb;}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}
.stApp{background:linear-gradient(180deg,#fff 0%,var(--dhp-bg) 100%);color:var(--dhp-text)}
.main .block-container{padding-top:.8rem;padding-bottom:5rem;max-width:820px}
[data-testid="stHeader"]{background:rgba(255,255,255,.78);backdrop-filter:blur(12px)}
[data-testid="stSidebar"]{width:min(84vw,320px)!important;background:#fff;border-right:1px solid var(--dhp-line)}
[data-testid="stSidebar"]>div:first-child{width:min(84vw,320px)!important;padding:1rem .85rem}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p{font-size:1rem!important}
[data-testid="stSidebar"] div[role="radiogroup"] label{border-radius:14px;padding:.65rem .75rem!important;margin:.12rem 0}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){background:var(--dhp-pink-soft);color:var(--dhp-pink);font-weight:750}
h1{font-size:2.25rem!important;font-weight:850!important;letter-spacing:-.04em;margin-bottom:.2rem!important}h2{font-size:1.75rem!important;font-weight:830!important}h3{font-size:1.25rem!important;font-weight:780!important}hr{border-color:var(--dhp-line)!important;margin:1.35rem 0!important}
.dhp-hero{padding:.4rem 0 .9rem}.dhp-subtitle{color:var(--dhp-muted);font-size:1rem;margin-top:-.15rem}.dhp-version{display:inline-flex;margin-top:.65rem;padding:.34rem .75rem;border-radius:999px;border:1px solid var(--dhp-line);background:#fff;color:var(--dhp-muted);font-size:.78rem;font-weight:650;letter-spacing:.03em}
.dhp-section{background:var(--dhp-card);border:1px solid var(--dhp-line);border-radius:24px;padding:1rem;margin:.85rem 0 1rem;box-shadow:0 10px 28px rgba(41,35,30,.055)}.dhp-section-title{display:flex;align-items:center;gap:.6rem;font-size:1.35rem;font-weight:850;letter-spacing:-.02em;margin-bottom:.85rem}.dhp-icon{width:42px;height:42px;display:inline-flex;align-items:center;justify-content:center;border-radius:14px;font-size:1.35rem;background:var(--dhp-pink-soft)}.dhp-icon.gold{background:var(--dhp-gold-soft)}
.dhp-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.7rem}.dhp-stat{border:1px solid var(--dhp-line);border-radius:18px;padding:.85rem;min-height:126px;background:#fff}.dhp-stat-label{font-size:.78rem;color:var(--dhp-muted);font-weight:700;margin-bottom:.3rem}.dhp-stat-value{font-size:1.72rem;font-weight:880;letter-spacing:-.035em;line-height:1.1}.dhp-stat-delta{display:inline-block;margin-top:.5rem;padding:.18rem .45rem;border-radius:999px;font-size:.72rem;font-weight:750;background:#f4f5f7;color:#676b76}.dhp-stat-status{margin-top:.45rem;font-size:.78rem;color:var(--dhp-muted)}
.dhp-insight{background:linear-gradient(135deg,#eef7ff,#f6fbff);border:1px solid #dcecf9;border-radius:18px;padding:.9rem 1rem;color:#275f8f;line-height:1.55}.dhp-callout{background:linear-gradient(135deg,var(--dhp-pink-soft),#fff);border:1px solid #f6dbe4;border-radius:18px;padding:.9rem 1rem}.dhp-score{font-size:2.7rem;font-weight:900;line-height:1;letter-spacing:-.05em}.small-muted{color:var(--dhp-muted);font-size:.86rem}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--dhp-line);padding:.8rem;border-radius:18px}[data-testid="stMetricValue"]{font-size:1.65rem}.stButton>button{border-radius:14px;min-height:42px;font-weight:750;border:1px solid var(--dhp-line)}.stButton>button[kind="primary"]{background:var(--dhp-pink);color:#fff;border:none}.stSelectbox div[data-baseweb="select"]>div,.stDateInput input,.stNumberInput input,.stTextArea textarea{border-radius:14px!important;background:#f7f7f9!important;border-color:transparent!important}.stRadio div[role="radiogroup"]{gap:.35rem;flex-wrap:wrap}.stRadio div[role="radiogroup"] label{background:#f6f6f8;border-radius:999px;padding:.32rem .65rem;border:1px solid transparent}.stRadio div[role="radiogroup"] label:has(input:checked){background:var(--dhp-pink-soft);border-color:#f3b6c7;color:var(--dhp-pink);font-weight:750}[data-testid="stDataFrame"]{border:1px solid var(--dhp-line);border-radius:18px;overflow:hidden}[data-testid="stExpander"]{border:1px solid var(--dhp-line);border-radius:18px;background:#fff}
@media(max-width:640px){.main .block-container{padding:.65rem .85rem 5.5rem;max-width:100%}h1{font-size:2rem!important}h2{font-size:1.55rem!important}.dhp-section{border-radius:20px;padding:.85rem}.dhp-grid{gap:.45rem}.dhp-stat{padding:.7rem .55rem;min-height:118px}.dhp-stat-label{font-size:.67rem}.dhp-stat-value{font-size:1.35rem}.dhp-stat-delta,.dhp-stat-status{font-size:.64rem}[data-testid="column"]{min-width:0!important}.stHorizontalBlock{gap:.45rem}[data-testid="stMetric"]{padding:.65rem .55rem}[data-testid="stMetricLabel"]{font-size:.72rem}[data-testid="stMetricValue"]{font-size:1.35rem}button{font-size:.9rem!important}}
</style>
""", unsafe_allow_html=True)


# =========================
# LOCAL TIMEZONE
# =========================
def detect_device_timezone():
    components.html(
        """
        <script>
        const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const parentUrl = new URL(window.parent.location.href);
        if (!parentUrl.searchParams.get("tz") && tz) {
            parentUrl.searchParams.set("tz", tz);
            window.parent.location.replace(parentUrl.toString());
        }
        </script>
        """,
        height=0,
    )

    tz_name = st.query_params.get("tz", DEFAULT_TIMEZONE)
    try:
        ZoneInfo(tz_name)
        return tz_name
    except ZoneInfoNotFoundError:
        return DEFAULT_TIMEZONE


DEVICE_TIMEZONE = detect_device_timezone()


def local_now():
    return datetime.now(ZoneInfo(DEVICE_TIMEZONE))


def local_today():
    return local_now().date()


# =========================
# DATA
# =========================
ISLAMIC_ITEMS = [
    "Tahajud", "Witir", "Dhuha", "DzikirPagi", "DzikirPetang",
    "Tahlil100", "Sholawat100", "GMQ", "AHD", "Sedekah", "Tilawah"
]

ISLAMIC_LABELS = {
    "Tahajud": "Tahajud",
    "Witir": "Witir",
    "Dhuha": "Dhuha",
    "DzikirPagi": "Dzikir Pagi",
    "DzikirPetang": "Dzikir Petang",
    "Tahlil100": "Dzikir Tauhid",
    "Sholawat100": "Dzikir Sholawat",
    "GMQ": "Kajian Quran",
    "AHD": "Kajian Hadits",
    "Sedekah": "Sedekah",
    "Tilawah": "Tilawah",
}


def to_bool(value):
    if value is True:
        return True
    if value is False:
        return False
    return str(value).strip().lower() in {"true", "yes", "1", "done", "checked", "y"}


@st.cache_data(ttl=30)
def load_health_data():
    df = pd.read_csv(HEALTH_CSV_URL)
    required = ["Nama", "Tanggal", "Chol", "UA", "Glucose"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom Health hilang: {missing}")

    df = df[required].copy()
    df["Nama"] = df["Nama"].astype(str).str.strip()
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")

    for col in ["Chol", "UA", "Glucose"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Nama", "Tanggal"])
    return df.sort_values(["Nama", "Tanggal"]).reset_index(drop=True)


@st.cache_data(ttl=30)
def load_islamic_data():
    try:
        df = pd.read_csv(ISLAMIC_CSV_URL)
    except Exception:
        return pd.DataFrame()

    required = [
        "Nama", "Tanggal", "Tahajud", "Witir", "Dhuha", "DzikirPagi",
        "DzikirPetang", "Sholawat100", "Tahlil100", "GMQ", "AHD",
        "Sedekah", "Tilawah", "Catatan"
    ]
    if any(col not in df.columns for col in required):
        return pd.DataFrame()

    df = df[required].copy()
    df["Nama"] = df["Nama"].astype(str).str.strip()
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")

    for col in ISLAMIC_ITEMS:
        df[col] = df[col].apply(to_bool)

    df["IstiqamahIndex"] = df[ISLAMIC_ITEMS].sum(axis=1) / len(ISLAMIC_ITEMS) * 100
    df = df.dropna(subset=["Nama", "Tanggal"])

    # Defensive cleanup: 1 date = 1 final record.
    df = (
        df.sort_values(["Nama", "Tanggal"])
          .drop_duplicates(subset=["Nama", "Tanggal"], keep="last")
          .reset_index(drop=True)
    )
    return df


def refresh_data():
    st.cache_data.clear()
    st.rerun()


# =========================
# HEALTH RULES
# =========================
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
    if len(clean) < 2:
        return None
    diff = clean.iloc[-1][col] - clean.iloc[-2][col]
    return "0.0" if diff == 0 else f"{diff:+.1f}"


# =========================
# API
# =========================
def post_to_api(api_url, payload):
    try:
        response = requests.post(api_url, json=payload, timeout=20)

        if response.status_code != 200:
            return False, f"HTTP {response.status_code}: {response.text[:180]}"

        text = response.text.strip()
        if not text:
            st.cache_data.clear()
            return True, "Data terkirim."

        try:
            result = response.json()
        except Exception:
            return False, f"Respons API bukan JSON: {text[:180]}"

        if result.get("status") == "success":
            st.cache_data.clear()
            action = result.get("action")
            if action == "update":
                return True, "Revisi hari ini berhasil disimpan."
            return True, result.get("message", "Data berhasil disimpan.")

        return False, result.get("message", str(result))

    except Exception as err:
        return False, f"Gagal terhubung ke API: {err}"


def save_health(nama, tanggal, chol, ua, glucose):
    return post_to_api(
        HEALTH_API_URL,
        {
            "Nama": nama,
            "Tanggal": str(tanggal),
            "Chol": int(chol),
            "UA": float(ua),
            "Glucose": int(glucose),
        },
    )


def save_islamic(tanggal, checklist, catatan):
    payload = {
        "Nama": "Deddy",
        "Tanggal": str(tanggal),
        "Catatan": catatan or "",
    }
    payload.update(checklist)
    return post_to_api(ISLAMIC_API_URL, payload)


# =========================
# CHARTS
# =========================
def plot_home_health(data):
    chart = data.dropna(subset=["Tanggal"]).sort_values("Tanggal").tail(20)
    if chart.empty:
        st.info("Belum ada data Health.")
        return

    fig, ax = plt.subplots(figsize=(10.5, 3.2))
    ax.plot(chart["Tanggal"], chart["Chol"], marker="o", linewidth=1.8, label="Chol")
    ax.plot(chart["Tanggal"], chart["UA"], marker="o", linewidth=1.8, label="UA")
    ax.plot(chart["Tanggal"], chart["Glucose"], marker="o", linewidth=1.8, label="Glucose")
    ax.set_title("Health Trend")
    ax.set_xlabel("")
    ax.grid(True, alpha=.25)
    ax.legend()
    fig.autofmt_xdate()
    st.pyplot(fig)
    plt.close(fig)


def plot_home_islamic(data):
    chart = data.dropna(subset=["IstiqamahIndex"]).sort_values("Tanggal").tail(30)
    if chart.empty:
        st.info("Belum ada data Istiqamah.")
        return

    fig, ax = plt.subplots(figsize=(10.5, 3.0))
    ax.plot(chart["Tanggal"], chart["IstiqamahIndex"], marker="o", linewidth=2)
    ax.set_title("Istiqamah Trend")
    ax.set_xlabel("")
    ax.set_ylabel("%")
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=.25)
    fig.autofmt_xdate()
    st.pyplot(fig)
    plt.close(fig)


def plot_health_metric(data, metric, title, nama):
    chart = data.dropna(subset=[metric]).sort_values("Tanggal")
    if chart.empty:
        st.info(f"Belum ada data {metric}.")
        return

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(chart["Tanggal"], chart[metric], marker="o", linewidth=2)
    ax.set_title(title)
    ax.set_xlabel("Tanggal")
    ax.set_ylabel(metric)
    ax.grid(True, alpha=.3)

    if metric == "Chol":
        ax.axhline(200, linestyle="--", alpha=.5)
    elif metric == "Glucose":
        ax.axhline(70, linestyle="--", alpha=.35)
        ax.axhline(100, linestyle="--", alpha=.5)
        ax.axhline(126, linestyle="--", alpha=.5)
    elif metric == "UA":
        ax.axhline(6.0 if nama == "Istri" else 7.5, linestyle="--", alpha=.5)

    fig.autofmt_xdate()
    st.pyplot(fig)
    plt.close(fig)


def plot_istiqamah(data):
    chart = data.dropna(subset=["IstiqamahIndex"]).sort_values("Tanggal")
    if chart.empty:
        st.info("Belum ada data Istiqamah.")
        return

    fig, ax = plt.subplots(figsize=(11, 4.3))
    ax.plot(chart["Tanggal"], chart["IstiqamahIndex"], marker="o", linewidth=2)
    ax.set_title("Trend Istiqamah Index")
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("%")
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=.3)
    fig.autofmt_xdate()
    st.pyplot(fig)
    plt.close(fig)


# =========================
# UI HELPERS
# =========================
def _status_text(raw):
    return raw.split(" ", 1)[1] if " " in raw else raw


def _delta_badge(delta):
    if delta is None:
        return "Belum ada pembanding"
    try:
        value = float(delta)
    except Exception:
        return str(delta)
    arrow = "↑" if value > 0 else "↓" if value < 0 else "→"
    return f"{arrow} {abs(value):.1f}"


def health_cards(data, nama):
    if data.empty:
        st.warning(f"Belum ada data untuk {nama}.")
        return
    latest = data.iloc[-1]
    cards = [
        ("Cholesterol", int(latest["Chol"]), _delta_badge(delta_value(data, "Chol")), _status_text(status_chol(latest["Chol"]))),
        ("Uric Acid", f"{latest['UA']:.1f}", _delta_badge(delta_value(data, "UA")), _status_text(status_ua(latest["UA"], nama))),
        ("Glucose", int(latest["Glucose"]), _delta_badge(delta_value(data, "Glucose")), _status_text(status_glucose(latest["Glucose"]))),
    ]
    html = '<div class="dhp-grid">'
    for label, value, delta, status in cards:
        html += f'<div class="dhp-stat"><div class="dhp-stat-label">{label}</div><div class="dhp-stat-value">{value}</div><div class="dhp-stat-delta">{delta}</div><div class="dhp-stat-status">{status}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


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
            f"Glucose {latest['Glucose'] - prev['Glucose']:+.1f}."
        )
    return text


def istiqamah_status(index):
    if index >= 95: return "🤲 Semoga Allah Menjaga Istiqamahmu"
    if index >= 80: return "🌺 Sangat Konsisten"
    if index >= 60: return "🌳 Menuju Istiqamah"
    if index >= 40: return "🌿 Terus Bertumbuh"
    return "🌱 Awal Perjalanan"


def existing_islamic_for_date(df, tanggal):
    if df.empty:
        return None

    target = pd.to_datetime(str(tanggal)).date()
    found = df[
        (df["Nama"] == "Deddy") &
        (df["Tanggal"].dt.date == target)
    ]

    return None if found.empty else found.iloc[-1]


# =========================
# APP
# =========================
try:
    health_df = load_health_data()
except Exception as err:
    st.error(f"Gagal membaca Health: {err}")
    health_df = pd.DataFrame(columns=["Nama", "Tanggal", "Chol", "UA", "Glucose"])

islamic_df = load_islamic_data()
islamic_deddy = (
    islamic_df[islamic_df["Nama"] == "Deddy"].copy()
    if not islamic_df.empty else pd.DataFrame()
)

st.markdown(
    f"""
    <div class="dhp-hero">
      <h1>❤️ DHP-Lifes</h1>
      <div class="dhp-subtitle">Grow Dashboard</div>
      <span class="dhp-version">{APP_VERSION}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

menu = st.sidebar.radio(
    "DHP-Lifes",
    ["🏠 Home", "❤️ Health Monitoring", "🕌 Islamic Things", "⚙️ Settings"],
)

if menu == "🏠 Home":
    st.markdown('<div class="dhp-section-title"><span class="dhp-icon">❤️</span>Health Monitoring</div>', unsafe_allow_html=True)
    home_profile = st.radio("Health profile", ["Deddy", "Istri"], horizontal=True, label_visibility="collapsed")
    home_health = health_df[health_df["Nama"] == home_profile].copy()
    health_cards(home_health, home_profile)
    if not home_health.empty:
        st.caption(f"Data terakhir: {home_health.iloc[-1]['Tanggal'].date()}")
    plot_home_health(home_health)

    st.markdown('<div class="dhp-section-title"><span class="dhp-icon gold">🕌</span>Islamic Things</div>', unsafe_allow_html=True)
    if not islamic_deddy.empty:
        latest_i = islamic_deddy.sort_values("Tanggal").iloc[-1]
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f'<div class="dhp-section"><div class="small-muted">Istiqamah Score</div><div class="dhp-score">{latest_i["IstiqamahIndex"]:.0f}%</div><div class="small-muted">{istiqamah_status(latest_i["IstiqamahIndex"])}</div></div>', unsafe_allow_html=True)
        with c2:
            plot_home_islamic(islamic_deddy)
    else:
        st.info("Belum ada data Istiqamah.")

elif menu == "❤️ Health Monitoring":
    st.markdown('<div class="dhp-section-title"><span class="dhp-icon">❤️</span>Health Monitoring</div>', unsafe_allow_html=True)
    nama = st.radio("Pilih profil", ["Deddy", "Istri"], horizontal=True)
    if st.button("🔄 Refresh Data", use_container_width=True):
        refresh_data()
    data = health_df[health_df["Nama"] == nama].copy()
    health_cards(data, nama)

    st.markdown("### 📌 Insight")
    insight_html = health_insight(data, nama).replace("\n", "<br>")
    st.markdown(f'<div class="dhp-insight">{insight_html}</div>', unsafe_allow_html=True)
    st.markdown("### 📈 Trend")
    metric = st.radio("Pilih trend", ["Chol", "UA", "Glucose"], horizontal=True, label_visibility="collapsed")
    rentang = st.selectbox("Rentang data", ["10 data terakhir", "20 data terakhir", "Semua"])
    plot_data = data.copy()
    if rentang == "10 data terakhir":
        plot_data = plot_data.tail(10)
    elif rentang == "20 data terakhir":
        plot_data = plot_data.tail(20)
    title_map = {"Chol": "Trend Kolesterol", "UA": "Trend Asam Urat", "Glucose": "Trend Glucose"}
    plot_health_metric(plot_data, metric, title_map[metric], nama)

    with st.expander("➕ Tambah Data Health", expanded=False):
        tanggal_health = st.date_input("Tanggal", value=local_today(), key="health_date")
        chol = st.number_input("Chol", min_value=0, step=1, value=0)
        st.caption(status_chol(chol))
        ua = st.number_input("UA", min_value=0.0, step=0.1, value=0.0)
        st.caption(status_ua(ua, nama))
        glucose = st.number_input("Glucose", min_value=0, step=1, value=0)
        st.caption(status_glucose(glucose))
        if st.button("💾 Simpan Data Health", type="primary", use_container_width=True):
            if chol == 0 and ua == 0 and glucose == 0:
                st.error("Data masih kosong.")
            else:
                ok, message = save_health(nama, tanggal_health, chol, ua, glucose)
                st.success(message) if ok else st.error(message)
    with st.expander("📋 Riwayat Health", expanded=False):
        st.dataframe(data.sort_values("Tanggal", ascending=False), use_container_width=True, hide_index=True)

elif menu == "🕌 Islamic Things":
    st.markdown('<div class="dhp-section-title"><span class="dhp-icon gold">🕌</span>Islamic Things</div>', unsafe_allow_html=True)
    st.caption("Your Journey Companion")
    tanggal_islamic = st.date_input("Tanggal", value=local_today(), key="islamic_date")
    if st.button("🔄 Refresh Data", key="refresh_islamic", use_container_width=True):
        refresh_data()
    existing = existing_islamic_for_date(islamic_deddy, tanggal_islamic)
    is_revision = existing is not None
    if is_revision:
        st.info("✏️ Data tanggal ini sudah ada. Simpan akan merevisi data yang sama.")
    checklist = {}
    cols = st.columns(2)
    for index, item in enumerate(ISLAMIC_ITEMS):
        default = bool(existing[item]) if is_revision else False
        with cols[index % 2]:
            checklist[item] = st.checkbox(ISLAMIC_LABELS[item], value=default, key=f"{item}_{tanggal_islamic}")
    default_note = str(existing["Catatan"]) if is_revision and pd.notna(existing["Catatan"]) else ""
    catatan = st.text_area("Catatan", value=default_note, placeholder="Catatan singkat jika ada...")
    done = sum(1 for value in checklist.values() if value)
    istiqamah_index = round(done / len(ISLAMIC_ITEMS) * 100)
    c1, c2 = st.columns(2)
    c1.metric("Done", f"{done} / {len(ISLAMIC_ITEMS)}")
    c2.metric("Istiqamah Index", f"{istiqamah_index}%")
    st.markdown(f'<div class="dhp-callout"><b>{istiqamah_status(istiqamah_index)}</b><br><span class="small-muted">Dashboard ini hanya saksi perjalananmu menuju Allah.</span></div>', unsafe_allow_html=True)
    confirmed = st.checkbox("Saya sudah memeriksa kembali catatan hari ini.", key=f"confirm_{tanggal_islamic}")
    button_text = "✏️ Revisi Hari Ini" if is_revision else "💾 Simpan Hari Ini"
    if st.button(button_text, disabled=not confirmed, type="primary", use_container_width=True):
        ok, message = save_islamic(tanggal_islamic, checklist, catatan)
        st.success(message) if ok else st.error(message)
    st.markdown("### 📈 Trend Istiqamah")
    plot_istiqamah(islamic_deddy)
    with st.expander("📋 Riwayat Islamic", expanded=False):
        if islamic_deddy.empty:
            st.info("Belum ada riwayat Islamic.")
        else:
            st.dataframe(islamic_deddy.sort_values("Tanggal", ascending=False), use_container_width=True, hide_index=True)

elif menu == "⚙️ Settings":
    st.markdown('<div class="dhp-section-title"><span class="dhp-icon">⚙️</span>Settings</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dhp-section"><b>System</b><br><span class="small-muted">Version: {APP_VERSION}<br>Device timezone: {DEVICE_TIMEZONE}<br>Local date: {local_today()}<br>Day change: 00:00 local time</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dhp-section"><b>Backend</b><br><span class="small-muted">Health API: Separate endpoint<br>Islamic API: Separate endpoint — UPSERT<br>Database: Google Sheet</span></div>', unsafe_allow_html=True)
    if st.button("🔄 Clear cache & refresh", use_container_width=True):
        refresh_data()
    st.caption("DHP-Lifes · 2026 Grow Dashboard — Healthy Body. Peaceful Soul")
