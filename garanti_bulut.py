import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(page_title="GARANTİ EMLAK | Tarsus", page_icon="🏠", layout="wide")

# 2. AYDINLIK TEMA VE OKUNAKLILIK AYARLARI (CSS)
st.markdown("""
    <style>
    /* Ana Arka Plan - Tertemiz Beyaz */
    .stApp {
        background-color: #ffffff;
    }
    
    /* İlan Kartları - Beyaz üzerine hafif gölgeli ve belirgin */
    .property-card {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid #e0e0e0;
        border-left: 8px solid #8CC63F; /* Logonun yeşili */
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        animation: fadeInUp 0.6s ease-out forwards;
        transition: all 0.3s ease;
    }
    
    .property-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(140, 198, 63, 0.2);
        background-color: #ffffff;
    }

    /* Yazı Renkleri - Maksimum Okunabilirlik */
    h1, h2, h3, p, span {
        color: #2b2d33 !important; /* Koyu Gri/Siyah yazı */
    }

    .price-tag {
        color: #4b8a00 !important; /* Daha koyu ve okunaklı bir yeşil */
        font-size: 28px;
        font-weight: 900;
    }
    
    .location-badge {
        background-color: #8CC63F;
        color: #ffffff !important; /* Yeşil üstüne beyaz yazı */
        padding: 5px 15px;
        border-radius: 8px;
        font-weight: bold;
    }

    /* Animasyonlar */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Sidebar (Yan Panel) - Hafif Gri */
    section[data-testid="stSidebar"] {
        background-color: #f1f3f5 !important;
        border-right: 1px solid #dee2e6;
    }

    /* Butonlar */
    .stButton>button {
        background: linear-gradient(45deg, #8CC63F, #7ab334) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        height: 48px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ilanlar.csv"

def verileri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])

# 3. YAN PANEL (LOGO VE MENÜ)
with st.sidebar:
    # Logonu buraya ekledim kanka
    st.image("https://i.hizliresim.com/iwyt3qr.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #2b2d33;'>YÖNETİM PANELİ</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    secim = st.radio("MENÜ", ["🏠 İlan Listesi", "➕ Yeni İlan Ekle", "🔐 Yönetici Girişi"])
    st.markdown("---")
    st.write("📍 **Tarsus / Mersin**")

# 4. YENİ İLAN EKLEME
if secim == "➕ Yeni İlan Ekle":
    st.markdown("<h1 style='color: #4b8a00;'>Yeni Portföy Kaydı</h1>", unsafe_allow_html=True)
    with st.form("ekle_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            baslik = st.text_input("İlan Başlığı")
            fiyat = st.text_input("Fiyat (TL)")
        with col2:
            konum = st.text_input("Bölge / Mahalle")
            tarih = datetime.now().strftime("%d/%m/%Y")
        
        aciklama = st.text_area("İlan Detayları")
        
        if st.form_submit_button("İlanı Kaydet"):
            if baslik and fiyat:
                df = verileri_yukle()
                yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
                yeni_veri = {"ID": yeni_id, "Tarih": tarih, "Baslik": baslik, "Fiyat": fiyat, "Konum": konum, "Aciklama": aciklama}
                df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.balloons()
                st.success("İlan başarıyla eklendi!")
            else:
                st.error("Lütfen başlık ve fiyat alanlarını doldurun.")

# 5. İLAN LİSTESİ
elif secim == "🏠 İlan Listesi":
    st.markdown("<h1 style='color: #2b2d33;'>GARANTİ <span style='color: #8CC63F;'>EMLAK</span> PORTFÖY</h1>", unsafe_allow_html=True)
    
    df = verileri_yukle()
    
    ara = st.text_input("🔍 İlanlarda Ara...", placeholder="Örn: 3+1, Tarsus, Acil")
    
    if not df.empty:
        if ara:
            df = df[df.apply(lambda row: row.astype(str).str.contains(ara, case=False).any(), axis=1)]
        
        for i, r in df.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="property-card">
                <div style="display: flex; justify-content: space-between;">
                    <span class="location-badge">📍 {r['Konum']}</span>
                    <span style="color: #666; font-size: 14px;">📅 {r['Tarih']}</span>
                </div>
                <h2 style="margin: 10px 0;">{r['Baslik']}</h2>
                <div class="price-tag">{r['Fiyat']} TL</div>
                <p style="color: #444; margin-top: 10px; border-top: 1px solid #eee; padding-top: 10px;">{r['Aciklama']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Henüz ilan bulunmuyor.")

# 6. YÖNETİCİ PANELİ
elif secim == "🔐 Yönetici Girişi":
    st.header("Sistem Yönetimi")
    sifre = st.text_input("Yönetici Şifresi", type="password")
    
    if sifre == "tarsus33":
        df = verileri_yukle()
        for i, r in df.iterrows():
            col1, col2 = st.columns([5, 1])
            col1.write(f"**{r['Baslik']}** ({r['Fiyat']} TL)")
            if col2.button("SİL", key=f"del_{r['ID']}"):
                df = df.drop(i)
                df.to_csv(DB_FILE, index=False)
                st.rerun()
