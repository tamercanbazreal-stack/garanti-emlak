import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# 1. SAYFA AYARLARI VE ANİMASYONLU GİRİŞ
st.set_page_config(page_title="GARANTİ EMLAK | Tarsus", page_icon="🏢", layout="wide")

# 2. ÖZEL TASARIM (CSS) - RENKLER, LOGO VE ANİMASYONLAR
st.markdown("""
    <style>
    /* Arka Plan ve Genel Renkler */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1c23 100%);
    }

    /* Logo ve Başlık Alanı */
    .logo-text {
        font-family: 'Arial Black', sans-serif;
        font-size: 50px;
        color: #FFD700;
        text-shadow: 2px 2px 4px #000000;
        animation: fadeInDown 1s ease-out;
    }

    /* İlan Kartları ve Animasyonu */
    .property-card {
        background-color: #252932;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid #3d424d;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: all 0.4s ease;
        animation: fadeInUp 0.5s ease-out forwards;
    }
    
    .property-card:hover {
        transform: scale(1.02);
        border-color: #FFD700;
        box-shadow: 0 10px 25px rgba(255, 215, 0, 0.2);
    }

    /* Fiyat Etiketi */
    .price-tag {
        color: #00ffcc;
        font-size: 26px;
        font-weight: 900;
        text-decoration: underline;
    }

    /* Animasyon Tanımları */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Buton Güzelleştirme */
    .stButton>button {
        background: linear-gradient(45deg, #FFD700, #FFA500) !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
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
    # --- LOGO BURAYA ---
    # Not: Kendi logonun internet linkini buraya koyabilirsin kanka. Şimdilik şık bir emlak ikonu koydum.
    st.image("https://i.hizliresim.com/iwyt3qr.png", width=120)
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>GARANTİ EMLAK</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    mod = st.radio("MENÜ", ["🔍 İlan Ara & Gör", "➕ Yeni İlan Ekle", "⚙️ Yönetici Paneli"])
    st.info("📍 Mersin / Tarsus")

# 4. YENİ İLAN EKLEME
if mod == "➕ Yeni İlan Ekle":
    st.markdown("<h2 class='logo-text'>Yeni Portföy Kaydı</h2>", unsafe_allow_html=True)
    with st.form("ekle_form", clear_on_submit=True):
        b = st.text_input("🏠 İlan Başlığı (Örn: Havuzlu Villa)")
        f = st.text_input("💰 Fiyat (TL)")
        k = st.selectbox("📍 Bölge", ["Tarsus Merkez", "Mersin Merkez", "Mezitli", "Erdemli", "Çamlıyayla", "Şahin Mahallesi", "Kırklarsırtı"])
        a = st.text_area("📝 Detaylı Açıklama")
        
        if st.form_submit_button("İlanı Yayına Al"):
            if b and f:
                with st.spinner('Kayıt yapılıyor...'):
                    time.sleep(1)
                    df = verileri_yukle()
                    yeni = {
                        "ID": datetime.now().strftime("%Y%m%d%H%M%S"), 
                        "Tarih": datetime.now().strftime("%d/%m/%Y"), 
                        "Baslik": b, "Fiyat": f, "Konum": k, "Aciklama": a
                    }
                    df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.balloons() # Animasyonlu kutlama
                    st.success("İlan başarıyla sisteme kaydedildi!")
            else:
                st.error("Lütfen başlık ve fiyat girin kanka!")

# 5. İLAN ARA VE GÖR
elif mod == "🔍 İlan Ara & Gör":
    st.markdown("<h1 class='logo-text'>GÜNCEL İLANLAR</h1>", unsafe_allow_html=True)
    
    df = verileri_yukle()
    
    # Arama Kutusu (Modern Tasarım)
    arama = st.text_input("🔍 İlanlarda Ara (Başlık, Bölge veya Açıklama yaz...)", "")
    
    if not df.empty:
        if arama:
            df = df[df['Baslik'].str.contains(arama, case=False) | 
                    df['Konum'].str.contains(arama, case=False) | 
                    df['Aciklama'].str.contains(arama, case=False)]
        
        for i, r in df.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="property-card">
                <div style="display: flex; justify-content: space-between;">
                    <span style="background: #FFD700; color: black; padding: 5px 15px; border-radius: 10px; font-weight: bold;">📍 {r['Konum']}</span>
                    <span style="color: #888;">📅 {r['Tarih']}</span>
                </div>
                <h2 style="color: white; margin-top: 15px;">{r['Baslik']}</h2>
                <div class="price-tag">{r['Fiyat']} TL</div>
                <hr style="border: 0.5px solid #444;">
                <p style="color: #ccc; font-size: 16px;">{r['Aciklama']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Henüz hiç ilan girilmemiş kanka.")

# 6. YÖNETİCİ PANELİ (SİLME)
elif mod == "⚙️ Yönetici Paneli":
    st.markdown("<h1 class='logo-text'>YÖNETİCİ PANELİ</h1>", unsafe_allow_html=True)
    sifre = st.text_input("🔒 Giriş Şifresi", type="password")
    
    if sifre == "tarsus33":
        df = verileri_yukle()
        if not df.empty:
            st.write("### İlanları Sil / Düzenle")
            for i, r in df.iterrows():
                col1, col2 = st.columns([5, 1])
                col1.markdown(f"**{r['Baslik']}** | {r['Konum']} | {r['Fiyat']} TL")
                if col2.button("🗑️ SİL", key=f"sil_{r['ID']}"):
                    df = df.drop(i)
                    df.to_csv(DB_FILE, index=False)
                    st.toast(f"{r['Baslik']} silindi.")
                    time.sleep(1)
                    st.rerun()
        else:
            st.info("Silinecek ilan yok.")
    elif sifre:
        st.error("Şifre Yanlış!")
