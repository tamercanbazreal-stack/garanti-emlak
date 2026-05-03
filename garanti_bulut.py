import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib
from fpdf import FPDF # PDF için bu kütüphaneyi kurmalısın: pip install fpdf2

# 1. SAYFA AYARLARI
st.set_page_config(page_title="GARANTİ EMLAK | Profesyonel", page_icon="🏢", layout="wide")

LOGO_URL = "https://i.hizliresim.com/iwyt3qr.png"
DB_FILE = "ilanlar_v3.csv"
USER_FILE = "kullanicilar_v3.csv"
SHARED_FILE = "paylasimlar.csv" # Paylaşılan portföyler için

# 2. VERİ YÖNETİMİ
def verileri_yukle():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])

def kullanicilari_yukle():
    if os.path.exists(USER_FILE): return pd.read_csv(USER_FILE)
    return pd.DataFrame(columns=["Kullanici", "Sifre", "Yetki"])

def paylasimlari_yukle():
    if os.path.exists(SHARED_FILE): return pd.read_csv(SHARED_FILE)
    return pd.DataFrame(columns=["IlanID", "Paylasan", "Paylasilan"])

# 3. PDF KATALOG OLUŞTURUCU
def pdf_olustur(ilan_verisi):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="GARANTI EMLAK PORTFOY KATALOGU", ln=True, align='C')
    pdf.ln(10)
    
    for _, r in ilan_verisi.iterrows():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, txt=f"{r['Baslik']} - {r['Fiyat']} TL", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, txt=f"Konum: {r['Konum']}\nAciklama: {r['Aciklama']}\nDanisman: {r['Sahip']}\n")
        pdf.ln(5)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 4. TASARIM (CSS)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f1f3f5 !important; }
    .stButton>button { border-radius: 8px; transition: 0.3s; }
    .share-card { background: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #2196f3; }
    </style>
    """, unsafe_allow_html=True)

# 5. OTURUM VE GİRİŞ (Önceki kodla aynı mantık...)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ANA PANEL ---
if st.session_state.logged_in:
    with st.sidebar:
        st.image(LOGO_URL)
        menu = st.radio("MENÜ", ["📋 Portföy & Paylaşım", "📅 Randevu Takvimi", "📄 Sözleşme Hazırla", "⚙️ Admin Paneli", "🚪 Çıkış"])

    # 1. PORTFÖY VE ÖZEL PAYLAŞIM
    if menu == "📋 Portföy & Paylaşım":
        st.title("🏡 Portföy Yönetimi ve İşbirliği")
        df = verileri_yukle()
        paylasimlar = paylasimlari_yukle()
        
        # Paylaşılan ilanları bul
        paylasilan_idleri = paylasimlar[paylasimlar['Paylasilan'] == st.session_state.username]['IlanID'].tolist()
        
        # Görünecek ilanlar: Kendi ilanlarım + Bana paylaşılanlar
        display_df = df[(df['Sahip'] == st.session_state.username) | (df['ID'].isin(paylasilan_idleri))]
        
        if not display_df.empty:
            for i, r in display_df.iterrows():
                is_shared = r['ID'] in paylasilan_idleri
                label = "🔗 Paylaşılan İlan" if is_shared else "🏠 Benim İlanım"
                
                with st.expander(f"{label} | {r['Baslik']} - {r['Fiyat']}"):
                    st.write(f"**Konum:** {r['Konum']} | **Ekleyen:** {r['Sahip']}")
                    st.write(r['Aciklama'])
                    
                    # Paylaşma Bölümü (Sadece kendi ilanını paylaşabilir)
                    if not is_shared:
                        users = kullanicilari_yukle()
                        diger_uyeler = users[users['Kullanici'] != st.session_state.username]['Kullanici'].tolist()
                        secilen_uye = st.selectbox("Paylaşılacak Kişi", diger_uyeler, key=f"sel_{r['ID']}")
                        if st.button("Yetki Ver / Paylaş", key=f"btn_{r['ID']}"):
                            yeni_p = pd.DataFrame([{"IlanID": r['ID'], "Paylasan": st.session_state.username, "Paylasilan": secilen_uye}])
                            pd.concat([paylasimlar, yeni_p]).to_csv(SHARED_FILE, index=False)
                            st.success(f"Portföy {secilen_uye} ile paylaşıldı!")
            
            # PDF ÇIKTISI ALMA
            st.divider()
            if st.button("📂 Seçili Portföyü PDF Katalog Yap"):
                pdf_data = pdf_olustur(display_df)
                st.download_button("📥 Kataloğu İndir", pdf_data, "garanti_emlak_katalog.pdf", "application/pdf")

    # 2. RANDEVU TAKVİMİ
    elif menu == "📅 Randevu Takvimi":
        st.title("🕒 Yer Gösterme ve Randevu Takvimi")
        with st.form("randevu_form"):
            r_tarih = st.date_input("Randevu Tarihi")
            r_saat = st.time_input("Saat")
            r_musteri = st.text_input("Müşteri Adı")
            r_ilan = st.text_input("Gidilecek Emlak/Yer")
            if st.form_submit_button("Randevu Oluştur"):
                st.success(f"{r_tarih} saat {r_saat} için {r_musteri} randevusu kaydedildi (Veritabanına bağlanacak).")

    # 3. SÖZLEŞME HAZIRLAYICI
    elif menu == "📄 Sözleşme Hazırla":
        st.title("✍️ Matbu Form Oluşturucu")
        form_tipi = st.selectbox("Form Tipi", ["Yer Gösterme Belgesi", "Kiralama Sözleşmesi", "Satış Protokolü"])
        m_ad = st.text_input("Müşteri Ad Soyad")
        m_tc = st.text_input("TC Kimlik No")
        if st.button("Sözleşmeyi PDF Olarak Taslakla"):
            st.info("Bu özellik seçilen verilere göre resmi formatta PDF doldurur.")

    # 4. ÇIKIŞ (En altta)
    elif menu == "🚪 Çıkış":
        st.session_state.logged_in = False
        st.rerun()
