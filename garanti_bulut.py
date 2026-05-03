import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib
import subprocess
import sys

# --- OTOMATİK KÜTÜPHANE YÜKLEME (FAIL-SAFE) ---
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from fpdf import FPDF
except ImportError:
    with st.spinner('Sistem ilk kurulumu yapıyor, lütfen bekleyin...'):
        install_package("fpdf2")
        from fpdf import FPDF

# 1. SAYFA AYARLARI
st.set_page_config(page_title="GARANTİ EMLAK | Yönetim", page_icon="🏠", layout="wide")
LOGO_URL = "https://i.hizliresim.com/iwyt3qr.png"

# Dosya Yolları
DB_FILE = "ilanlar_v3.csv"
USER_FILE = "kullanicilar_v3.csv"
SHARED_FILE = "paylasimlar.csv"
RANDEVU_FILE = "randevular.csv"

# 2. VERİ FONKSİYONLARI
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def verileri_yukle(dosya, sutunlar):
    if os.path.exists(dosya):
        return pd.read_csv(dosya)
    return pd.DataFrame(columns=sutunlar)

# 3. TASARIM (CSS)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f1f3f5 !important; }
    .property-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 15px;
        border-left: 5px solid #8CC63F;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. OTURUM KONTROLÜ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.image(LOGO_URL, use_container_width=True)
        u_name = st.text_input("Kullanıcı Adı")
        u_pass = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş", use_container_width=True):
            if u_name == "admin" and u_pass == "3363Garanti":
                st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Yönetici", "admin"
                st.rerun()
            else:
                users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                if not users[(users['Kullanici'] == u_name) & (users['Sifre'] == make_hashes(u_pass))].empty:
                    st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Danışman", u_name
                    st.rerun()
                else: st.error("Hatalı Giriş!")

# --- ANA PANEL ---
else:
    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.write(f"👤 **{st.session_state.username}**")
        st.divider()
        menu = st.radio("MENÜ", ["📋 Portföy", "➕ İlan Ekle", "📅 Randevular", "📄 Sözleşme", "🚪 Çıkış"])
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.rerun()

    # 1. PORTFÖY VE PAYLAŞIM
    if menu == "📋 Portföy":
        st.title("🏡 Gayrimenkul Portföyü")
        df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
        paylasimlar = verileri_yukle(SHARED_FILE, ["IlanID", "Paylasan", "Paylasilan"])
        
        pay_idleri = paylasimlar[paylasimlar['Paylasilan'] == st.session_state.username]['IlanID'].astype(str).tolist()
        display_df = df[(df['Sahip'] == st.session_state.username) | (df['ID'].astype(str).isin(pay_idleri))]
        
        for i, r in display_df.iterrows():
            st.markdown(f'<div class="property-card"><b>{r["Baslik"]}</b><br>{r["Fiyat"]} TL - {r["Konum"]}</div>', unsafe_allow_html=True)
            if st.button(f"Sil", key=f"del_{r['ID']}"):
                df[df['ID'] != r['ID']].to_csv(DB_FILE, index=False)
                st.rerun()
        
        if st.button("📂 Katalog İndir (PDF)"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "GARANTI EMLAK PORTFOY", ln=True, align='C')
            for _, row in display_df.iterrows():
                pdf.ln(10)
                pdf.set_font("Arial", size=12)
                pdf.cell(0, 10, f"{row['Baslik']} - {row['Fiyat']} TL", ln=True)
            st.download_button("📥 PDF İndir", pdf.output(dest='S').encode('latin-1', 'ignore'), "katalog.pdf")

    # 2. İLAN EKLE
    elif menu == "➕ İlan Ekle":
        with st.form("yeni_ilan"):
            baslik = st.text_input("Başlık")
            fiyat = st.text_input("Fiyat")
            konum = st.text_input("Konum")
            detay = st.text_area("Açıklama")
            if st.form_submit_button("Kaydet"):
                df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
                yeni = {"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "Sahip": st.session_state.username, "Tarih": datetime.now().strftime("%d/%m/%Y"), "Baslik": baslik, "Fiyat": fiyat, "Konum": konum, "Aciklama": detay}
                pd.concat([df, pd.DataFrame([yeni])]).to_csv(DB_FILE, index=False)
                st.success("Eklendi!")

    # 3. RANDEVULAR
    elif menu == "📅 Randevular":
        r_df = verileri_yukle(RANDEVU_FILE, ["Tarih", "Saat", "Musteri", "Ilan"])
        with st.form("r_form"):
            d = st.date_input("Gün"); s = st.time_input("Saat")
            m = st.text_input("Müşteri"); i = st.text_input("İlan")
            if st.form_submit_button("Kaydet"):
                pd.concat([r_df, pd.DataFrame([{"Tarih": str(d), "Saat": str(s), "Musteri": m, "Ilan": i}])]).to_csv(RANDEVU_FILE, index=False)
                st.rerun()
        st.table(r_df)

    # 4. SÖZLEŞME
    elif menu == "📄 Sözleşme":
        isim = st.text_input("Müşteri Adı")
        if st.button("PDF Sözleşme Oluştur"):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"GARANTI EMLAK - SOZLESME", ln=True, align='C')
            pdf.ln(10); pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, f"Sayin {isim}, Garanti Emlak hizmet belgesidir.")
            st.download_button("📥 İndir", pdf.output(dest='S').encode('latin-1', 'ignore'), "sozlesme.pdf")
