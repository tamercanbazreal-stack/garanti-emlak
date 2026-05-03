import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(page_title="GARANTİ EMLAK | Tarsus", page_icon="🏠", layout="wide")

# 2. KURUMSAL TASARIM (LOGONUN YEŞİLİ VE SİYAH KONSEPTİ)
st.markdown("""
    <style>
    /* Ana Renkler ve Arka Plan */
    .stApp {
        background-color: #0e1117;
    }
    
    /* İlan Kartları */
    .property-card {
        background-color: #1d2129;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 25px;
        border-left: 6px solid #8CC63F; /* Logonun yeşili */
        transition: all 0.4s ease;
        animation: slideIn 0.5s ease-out;
    }
    
    .property-card:hover {
        transform: scale(1.01);
        box-shadow: 0 10px 20px rgba(140, 198, 63, 0.15);
        border-left: 6px solid #ffffff;
    }

    /* Başlık ve Fiyat Stilleri */
    .price-tag {
        color: #8CC63F;
        font-size: 26px;
        font-weight: 900;
    }
    
    .location-badge {
        background-color: #8CC63F;
        color: #000000;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 14px;
    }

    /* Animasyonlar */
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* Sidebar ve Butonlar */
    .stButton>button {
        background: linear-gradient(45deg, #8CC63F, #7ab334) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        height: 45px !important;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ilanlar.csv"

def verileri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])

# 3. YAN PANEL (LOGO VE NAVİGASYON)
with st.sidebar:
    # BURAYA LOGONUN LINKINI KOYMAYI UNUTMA KANKA
    st.image("https://i.ibb.co/ZztYhP0/garanti-logo-transparan.png", use_container_width=True) 
    st.markdown("<h2 style='text-align: center; color: white;'>Yönetim Paneli</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    secim = st.selectbox("Gitmek İstediğiniz Yer:", ["🏠 İlan Listesi", "➕ Yeni İlan Gir", "🔐 Yönetici Girişi"])
    st.write(f"📍 **Mersin / Tarsus**")
    st.write(f"📅 {datetime.now().strftime('%d.%m.%Y')}")

# 4. YENİ İLAN GİRİŞİ
if secim == "➕ Yeni İlan Gir":
    st.markdown("<h1 style='color: #8CC63F;'>Yeni Portföy Kaydı</h1>", unsafe_allow_html=True)
    with st.form("yeni_ilan_formu", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            baslik = st.text_input("İlan Başlığı")
            fiyat = st.text_input("Fiyat (TL)")
        with col2:
            konum = st.text_input("Bölge / Mahalle")
            tarih = datetime.now().strftime("%d/%m/%Y")
        
        aciklama = st.text_area("İlan Detayları")
        
        if st.form_submit_button("İlanı Portföye Ekle"):
            if baslik and fiyat:
                df = verileri_yukle()
                yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
                yeni_veri = {"ID": yeni_id, "Tarih": tarih, "Baslik": baslik, "Fiyat": fiyat, "Konum": konum, "Aciklama": aciklama}
                df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.balloons()
                st.success("Hayırlı olsun kanka, ilan yayında!")
            else:
                st.warning("Eksik bilgi bırakma kanka!")

# 5. İLAN LİSTESİ VE ARAMA
elif secim == "🏠 İlan Listesi":
    st.markdown("<h1 style='color: white;'>GARANTİ <span style='color: #8CC63F;'>EMLAK</span> PORTFÖY</h1>", unsafe_allow_html=True)
    
    df = verileri_yukle()
    
    # ARA ÇUBUĞU
    ara = st.text_input("🔍 İlanlarda Ara (Kelime, Fiyat veya Konum yazın...)", "")
    
    if not df.empty:
        if ara:
            df = df[df.apply(lambda row: row.astype(str).str.contains(ara, case=False).any(), axis=1)]
        
        for i, r in df.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="property-card">
                <div style="display: flex; justify-content: space-between;">
                    <span class="location-badge">📍 {r['Konum']}</span>
                    <span style="color: #888; font-size: 14px;">{r['Tarih']}</span>
                </div>
                <h2 style="margin: 15px 0 5px 0; color: white;">{r['Baslik']}</h2>
                <div class="price-tag">{r['Fiyat']} TL</div>
                <p style="color: #bbb; margin-top: 10px; font-size: 15px;">{r['Aciklama']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Henüz ilan girilmemiş kanka.")

# 6. YÖNETİCİ PANELİ (SİLME)
elif secim == "🔐 Yönetici Girişi":
    st.markdown("<h1>Sistem Yönetimi</h1>", unsafe_allow_html=True)
    pw = st.text_input("Şifre Giriniz", type="password")
    
    if pw == "tarsus33":
        df = verileri_yukle()
        st.write("### Kayıtlı İlanları Yönet")
        for i, r in df.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(f"**{r['Baslik']}** - {r['Fiyat']} TL")
            if c2.button("🗑️ SİL", key=f"btn_{r['ID']}"):
                df = df.drop(i)
                df.to_csv(DB_FILE, index=False)
                st.rerun()
    elif pw:
        st.error("Şifre yanlış kanka!")
