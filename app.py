import streamlit as st
from datetime import date

st.set_page_config(
    page_title="DHP-Lifes",
    page_icon="❤️",
    layout="wide"
)

st.title("❤️ DHP-Lifes")
st.caption("Dashboard keluarga untuk kesehatan, kopi, mobilitas, dan Islamic Things")

menu = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "❤️ Health", "☕ Coffee Lab", "🚗 Mobility", "🕌 Islamic Things"]
)

if menu == "🏠 Home":
    st.header("Selamat pagi, Deddy & Family")
    st.success("DHP-Lifes V2 mulai dibangun 🚀")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👤 Deddy")
        st.write("Health dashboard siap dikembangkan.")
    with c2:
        st.subheader("👩 Istri")
        st.write("Data kesehatan akan dibuat terpisah.")

if menu == "❤️ Health":
    st.header("❤️ Health Dashboard")

    user = st.selectbox("Pilih profil", ["Deddy", "Istri"])
    st.subheader(f"Input data kesehatan: {user}")

    tanggal = st.date_input("Tanggal", date.today())
    gula = st.number_input("Gula darah", min_value=0)
    sistole = st.number_input("Sistole", min_value=0)
    diastole = st.number_input("Diastole", min_value=0)
    kolesterol = st.number_input("Kolesterol", min_value=0)
    asam_urat = st.number_input("Asam urat", min_value=0.0, step=0.1)
    berat = st.number_input("Berat badan", min_value=0.0, step=0.1)
    catatan = st.text_area("Catatan")

    if st.button("Simpan sementara"):
        st.success(f"Data {user} tanggal {tanggal} berhasil diinput sementara.")
        st.info("Tahap berikutnya: data ini akan disimpan ke Google Sheets.")

if menu == "☕ Coffee Lab":
    st.header("☕ Coffee Lab")
    st.write("Nanti berisi log roasting, cupping, dan inventory green bean.")

if menu == "🚗 Mobility":
    st.header("🚗 Mobility")
    st.write("Nanti berisi catatan J6, Tiggo 8 CSH, servis, pajak, dan perjalanan.")

if menu == "🕌 Islamic Things":
    st.header("🕌 Islamic Things")
    st.write("Nanti berisi Glory Morning Quran, Afternoon Hadits, doa, dzikir, dan renungan.")
