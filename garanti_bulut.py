import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(page_title="GARANTİ EMLAK | Tarsus", page_icon="🏠", layout="wide")

# 2. MODERN GRİ KONSEPT VE GELİŞMİŞ ANİMASYONLAR (CSS)
st.markdown("""
    <style>
    /* Ana Arka Plan - Siyah değil, Şık bir Gri */
    .stApp {
        background-color: #2b2d33;
    }
    
    /* İlan Kartları ve Giriş Animasyonu */
    .property-card {
        background-color: #383b42;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid #4a4e59;
        border-left: 8px solid #8CC63F; /* Logonun yeşili */
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        
        /* Animasyon: Aşağıdan yukarı süzülerek gelme */
        animation: fadeInUp 0.8s ease-out forwards;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    /* Kartın üzerine gelince parlama ve büyüme efekti */
    .property-card:hover {
        transform: translateY(-8px) scale(1.01);
        border-left: 8px solid #ffffff;
        box-shadow: 0 12px 30px rgba(140, 198, 63, 0.25);
        background-color: #40444d;
    }

    /* Başlık Animasyonu */
    .main-title {
        color: #ffffff;
        font-family: 'Arial Black', sans-serif;
        animation: fadeInDown 1s ease-out;
    }

    /* Fiyat ve Badge Stilleri */
    .price-tag {
        color: #8CC63F;
        font-size: 28px;
        font-weight: 900;
        letter-spacing: 1px;
    }
    
    .location-badge {
        background: linear-gradient(90deg, #8CC63F, #7ab334);
        color: #000000;
        padding: 5px 15px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(140, 198, 63, 0.3);
    }

    /* KEYFRAMES (Hareketler) */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Sidebar Tasarımı */
    section[data-testid="stSidebar"] {
        background-color: #1e2025 !important;
        border-right: 1px solid #3d424d;
    }

    /* Buton Güzelleştirme */
    .stButton>button {
        background: linear-gradient(45deg, #8CC63F, #7ab334) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 12px !important;
        height: 50px !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        filter: brightness(1.1);
        box-shadow: 0 5px 15px rgba(140, 198, 63, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ilanlar.csv"

def verileri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])

# 3. YAN PANEL (SIDEBAR)
with st.sidebar:
    # Logonun linkini buraya yapıştır kanka
    st.image("https://i.ibb.co/ZztYhP0/garanti-logo-transparan.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #8CC63F;'>KONTROL PANELİ</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    secim = st.radio("MENÜ", ["🏠 İlanları İncele", "➕ Yeni Kayıt Oluştur", "🔐 Yönetici Girişi"])
    st.markdown("---")
    st.write(f"📍 **Mersin / Tarsus**")
    st.write(f"📅 {datetime.now().strftime('%d.%m.%Y')}")

# 4. YENİ İLAN KAYDI
if secim == "➕ Yeni Kayıt Oluştur":
    st.markdown("<h1 class='main-title' style='color: #8CC63F;'>Yeni Portföy Girişi</h1>", unsafe_allow_html=True)
    with st.form("modern_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            baslik = st.text_input("🏠 İlan Başlığı")
            fiyat = st.text_input("💰 Fiyat (TL)")
        with c2:
            konum = st.text_input("📍 Konum / Mahalle")
            tarih = datetime.now().strftime("%d/%m/%Y")
        
        aciklama = st.text_area("📝 İlan Detaylı Açıklaması")
        
        if st.form_submit_button("İlanı Yayına Al"):
            if baslik and fiyat:
                with st.spinner('Veriler işleniyor...'):
                    time.sleep(1)
                    df = verileri_yukle()
                    yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
                    yeni_data = {"ID": yeni_id, "Tarih": tarih, "Baslik": baslik, "Fiyat": fiyat, "Konum": konum, "Aciklama": aciklama}
                    df = pd.concat([df, pd.DataFrame([yeni_data])], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.balloons()
                    st.success("İlan başarıyla yayına alındı!")
            else:
                st.error("Başlık ve Fiyat kısımlarını boş geçme kanka!")

# 5. İLAN LİSTESİ (ANİMASYONLU KARTLAR)
elif secim == "🏠 İlanları İncele":
    st.markdown("<h1 class='main-title'>GARANTİ <span style='color: #8CC63F;'>EMLAK</span> TARSUS</h1>", unsafe_allow_html=True)
    
    df = verileri_yukle()
    
    # ARA ÇUBUĞU
    ara = st.text_input("🔍 Aradığınız mülkün özelliklerini buraya yazın...", placeholder="Örn: 3+1, Kırklarsırtı, 2.500.000")
    
    if not df.empty:
        if ara:
            df = df[df.apply(lambda row: row.astype(str).str.contains(ara, case=False).any(), axis=1)]
        
        for i, r in df.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="property-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="location-badge">📍 {r['Konum']}</span>
                    <span style="color: #999; font-size: 13px;">📅 {r['Tarih']}</span>
                </div>
                <h2 style="margin: 15px 0 5px 0; color: white; font-size: 24px;">{r['Baslik']}</h2>
                <div class="price-tag">{r['Fiyat']} TL</div>
                <div style="height: 1px; background: #4a4e59; margin: 15px 0;"></div>
                <p style="color: #d1d1d1; line-height: 1.6;">{r['Aciklama']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Portföyde henüz aktif ilan bulunmuyor.")

# 6. YÖNETİCİ PANELİ (SİLME)
elif secim == "🔐 Yönetici Girişi":
    st.markdown("<h1 class='main-title'>Sistem Yönetimi</h1>", unsafe_allow_html=True)
    pw = st.text_input("Erişim Şifresi", type="password")
    
    if pw == "tarsus33":
        df = verileri_yukle()
        st.write("### Mevcut İlanları Kaldır")
        for i, r in df.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"**{r['Baslik']}** | {r['Fiyat']} TL")
            if c2.button("🗑️ SİL", key=f"del_{r['ID']}"):
                df = df.drop(i)
                df.to_csv(DB_FILE, index=False)
                st.toast(f"{r['Baslik']} silindi.")
                time.sleep(0.5)
                st.rerun()
    elif pw:
        st.error("Hatalı şifre denemesi!")
