import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

st.set_page_config(page_title="DHP-Lifes", page_icon="❤️", layout="wide")

APP_VERSION = "V13.2 GROW DASHBOARD"
SHEET_ID = "1vEcgjWVTH5hSO-jYeI13BBD_1OFEPkiQpeENh2OfnjQ"
HEALTH_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Health"
ISLAMIC_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Islamic"

HEALTH_API_URL = "https://script.google.com/macros/s/AKfycbzG9Wf3MFQQegujmubT2NW_U53DdbuqPU22UrI43FVPl5FE8X-L_D9D8fuQ1k7pSITxow/exec"
ISLAMIC_API_URL = "https://script.google.com/macros/s/AKfycbyblLjqJ6iF383GdW-n3ZpS3UQUvLdFK3891F7thZobeyMFLjXPSJDAx1x4a3-j4gInBw/exec"
DEFAULT_TIMEZONE = "Asia/Jakarta"

st.markdown("""
<style>
.main .block-container {padding-top:1.05rem; max-width:1200px;}
[data-testid="stSidebar"] {min-width:280px;}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] div {font-size:1.22rem !important;}
div[role="radiogroup"] label {font-size:1.28rem !important; padding:.28rem 0;}
h1 {font-size:2.60rem !important; font-weight:850 !important;}
h2 {font-size:2.05rem !important; font-weight:800 !important;}
h3 {font-size:1.55rem !important; font-weight:760 !important;}
.dhp-card {
    border:1px solid rgba(128,128,128,.25);
    border-radius:22px;
    padding:20px;
    margin-bottom:18px;
    background:rgba(255,255,255,.035);
    box-shadow:0 4px 18px rgba(0,0,0,.08);
}
.dhp-profile {
    font-size:2.15rem;
    font-weight:900;
    margin-bottom:.15rem;
}
.dhp-version {
    padding:.22rem .65rem;
    border-radius:999px;
    border:1px solid rgba(128,128,128,.35);
    font-size:.85rem;
    opacity:.82;
}
.istiqamah-index {
    font-size:3.15rem;
    font-weight:900;
    line-height:1;
}
.small-muted {opacity:.72; font-size:.92rem;}
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
def health_cards(data, nama):
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

st.title("❤️ DHP-Lifes")
st.caption("Grow Dashboard")
st.markdown(f'<span class="dhp-version">{APP_VERSION}</span>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "❤️ Health Monitoring", "🕌 Islamic Things", "⚙️ Settings"],
)


# HOME
if menu == "🏠 Home":
    st.header("Grow Dashboard")

    st.subheader("❤️ Health Monitoring")
    home_profile = st.radio(
        "Health profile",
        ["Deddy", "Istri"],
        horizontal=True,
        label_visibility="collapsed",
    )
    home_health = health_df[health_df["Nama"] == home_profile].copy()
    plot_home_health(home_health)

    st.divider()
    st.subheader("🕌 Islamic Things")
    plot_home_islamic(islamic_deddy)


# HEALTH
elif menu == "❤️ Health Monitoring":
    st.header("❤️ Health Monitoring")

    top1, top2 = st.columns([4, 1])
    with top1:
        nama = st.selectbox("Pilih profil", ["Deddy", "Istri"])
    with top2:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh"):
            refresh_data()

    data = health_df[health_df["Nama"] == nama].copy()

    health_cards(data, nama)

    st.divider()
    st.subheader("📌 Insight")
    st.info(health_insight(data, nama))

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        metric = st.radio("Pilih trend", ["Chol", "UA", "Glucose"], horizontal=True)
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
    plot_health_metric(plot_data, metric, title_map[metric], nama)

    st.divider()
    with st.expander("➕ Tambah Data Health", expanded=False):
        tanggal_health = st.date_input(
            "Tanggal",
            value=local_today(),
            key="health_date",
        )

        x1, x2, x3 = st.columns(3)
        with x1:
            chol = st.number_input("Chol", min_value=0, step=1, value=0)
            st.caption(status_chol(chol))
        with x2:
            ua = st.number_input("UA", min_value=0.0, step=0.1, value=0.0)
            st.caption(status_ua(ua, nama))
        with x3:
            glucose = st.number_input("Glucose", min_value=0, step=1, value=0)
            st.caption(status_glucose(glucose))

        if st.button("💾 Simpan Data Health"):
            if chol == 0 and ua == 0 and glucose == 0:
                st.error("Data masih kosong.")
            else:
                ok, message = save_health(nama, tanggal_health, chol, ua, glucose)
                if ok:
                    st.success(message)
                else:
                    st.error(message)

    st.divider()
    st.subheader("📋 Riwayat")
    st.dataframe(
        data.sort_values("Tanggal", ascending=False),
        use_container_width=True,
        hide_index=True,
    )


# ISLAMIC
elif menu == "🕌 Islamic Things":
    st.header("🕌 Islamic Things")
    st.caption("Your Journey Companion")

    top1, top2 = st.columns([4, 1])
    with top1:
        tanggal_islamic = st.date_input(
            "Tanggal",
            value=local_today(),
            key="islamic_date",
        )
    with top2:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh", key="refresh_islamic"):
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
            checklist[item] = st.checkbox(
                ISLAMIC_LABELS[item],
                value=default,
                key=f"{item}_{tanggal_islamic}",
            )

    default_note = (
        str(existing["Catatan"])
        if is_revision and pd.notna(existing["Catatan"])
        else ""
    )
    catatan = st.text_area(
        "Catatan",
        value=default_note,
        placeholder="Catatan singkat jika ada...",
    )

    done = sum(1 for value in checklist.values() if value)
    istiqamah_index = round(done / len(ISLAMIC_ITEMS) * 100)

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Done", f"{done} / {len(ISLAMIC_ITEMS)}")
    c2.metric("🕌 Istiqamah Index", f"{istiqamah_index}%")
    c3.write(istiqamah_status(istiqamah_index))

    st.divider()
    st.subheader("🤲 Muhasabah")
    st.info(
        "Dashboard ini bukan untuk dinilai siapa pun. "
        "Ia hanya saksi perjalananmu menuju Allah. "
        "Sudahkah catatan hari ini benar?"
    )
    confirmed = st.checkbox(
        "Saya sudah memeriksa kembali catatan hari ini.",
        key=f"confirm_{tanggal_islamic}",
    )

    button_text = "✏️ Revisi Hari Ini" if is_revision else "💾 Simpan Hari Ini"
    if st.button(button_text, disabled=not confirmed):
        ok, message = save_islamic(tanggal_islamic, checklist, catatan)
        if ok:
            st.success(message)
        else:
            st.error(message)

    st.divider()
    st.subheader("📈 Trend Istiqamah")
    plot_istiqamah(islamic_deddy)

    st.divider()
    st.subheader("📋 Riwayat")
    if islamic_deddy.empty:
        st.info("Belum ada riwayat Islamic.")
    else:
        st.dataframe(
            islamic_deddy.sort_values("Tanggal", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


# SETTINGS
elif menu == "⚙️ Settings":
    st.header("⚙️ Settings")

    st.subheader("System")
    st.write(f"Version: **{APP_VERSION}**")
    st.write(f"Device timezone: **{DEVICE_TIMEZONE}**")
    st.write(f"Local date: **{local_today()}**")
    st.write("Day change: **00:00 local time**")

    st.divider()
    st.subheader("Backend")
    st.write("Health API: **Separate endpoint**")
    st.write("Islamic API: **Separate endpoint — UPSERT**")
    st.write("Database: **Google Sheet**")

    st.divider()
    st.subheader("Maintenance")
    if st.button("🔄 Clear cache & refresh"):
        refresh_data()

    st.divider()
    st.subheader("About")
    st.write("**DHP-Lifes**")
    st.caption("2026 Grow Dashboard — Healthy Body. Peaceful Soul")
