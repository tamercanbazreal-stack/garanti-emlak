import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. SAYFA AYARLARI
st.set_page_config(page_title="GARANTİ EMLAK | Yönetim", page_icon="🏠", layout="wide")

# 2. ÖZEL TASARIM (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .property-card {
        background-color: #1d2129;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #FFD700;
    }
    .price-tag { color: #00ffcc; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ilanlar.csv"

def verileri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])

# 3. YAN PANEL (EKLEME VE YÖNETİCİ GİRİŞİ)
with st.sidebar:
    st.title("🏠 Garanti Emlak")
    mod = st.radio("İşlem Seçin", ["İlanları Gör", "Yeni İlan Ekle", "Yönetici Paneli (Silme)"])
    
    if mod == "Yeni İlan Ekle":
        with st.form("ekle_form", clear_on_submit=True):
            b = st.text_input("İlan Başlığı")
            f = st.text_input("Fiyat")
            k = st.text_input("Konum")
            a = st.text_area("Açıklama")
            if st.form_submit_button("Kaydet"):
                df = verileri_yukle()
                yeni = {"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "Tarih": datetime.now().strftime("%d/%m/%Y"), "Baslik": b, "Fiyat": f, "Konum": k, "Aciklama": a}
                df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("İlan eklendi!")

# 4. ANA EKRAN (LİSTELEME VE SİLME)
df = verileri_yukle()

if mod == "İlanları Gör":
    st.header("📋 Güncel Portföy")
    for i, r in df.iloc[::-1].iterrows():
        st.markdown(f'<div class="property-card"><h3>{r["Baslik"]}</h3><p>📍 {r["Konum"]} | 📅 {r["Tarih"]}</p><div class="price-tag">{r["Fiyat"]} TL</div><p>{r["Aciklama"]}</p></div>', unsafe_allow_html=True)

elif mod == "Yönetici Paneli (Silme)":
    st.header("⚙️ İlan Yönetimi")
    sifre = st.text_input("Yönetici Şifresi", type="password")
    if sifre == "tarsus33": # ŞİFREN BU KANKA
        for i, r in df.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.write(f"**{r['Baslik']}** ({r['Fiyat']} TL)")
            if col2.button("SİL", key=r['ID']):
                df = df.drop(i)
                df.to_csv(DB_FILE, index=False)
                st.rerun()
    elif sifre:
        st.error("Şifre Yanlış!")
