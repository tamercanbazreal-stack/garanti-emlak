import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time
from PIL import Image

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(page_title="GARANTİ EMLAK | Tarsus", page_icon="🏠", layout="wide")

# 2. TASARIM AYARLARI (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .property-card {
        background-color: #f8f9fa;
        border-radius: 15px;
        margin-bottom: 30px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        overflow: hidden;
    }
    .card-content { padding: 20px; }
    h1, h2, h3, p, span { color: #2b2d33 !important; }
    .price-tag { color: #4b8a00 !important; font-size: 26px; font-weight: 900; }
    .location-badge {
        background-color: #8CC63F;
        color: #ffffff !important;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: bold;
    }
    .cover-img { width: 100%; height: 250px; object-fit: cover; }
    section[data-testid="stSidebar"] { background-color: #f1f3f5 !important; border-right: 1px solid #dee2e6; }
    .stButton>button {
        background: linear-gradient(45deg, #8CC63F, #7ab334) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        height: 45px !important;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ilanlar.csv"
IMG_FOLDER = "ilan_resimleri" # Resimlerin saklanacağı klasör adı

# Resim klasörü yoksa oluştur
if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

def verileri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama", "Foto_Yolu"])

def format_para(sayi):
    try:
        temiz_sayi = int(''.join(filter(str.isdigit, str(sayi))))
        return f"{temiz_sayi:,}".replace(",", ".")
    except:
        return sayi

# 3. YAN PANEL
with st.sidebar:
    st.image("https://i.hizliresim.com/iwyt3qr.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>YÖNETİM PANELİ</h3>", unsafe_allow_html=True)
    st.markdown("---")
    secim = st.radio("MENÜ", ["🏠 İlan Listesi", "➕ Yeni İlan Ekle", "🔐 Yönetici Girişi"])

# 4. YENİ İLAN EKLEME (GALERİDEN SEÇME ÖZELLİĞİ)
if secim == "➕ Yeni İlan Ekle":
    st.markdown("<h1 style='color: #4b8a00;'>Yeni Portföy Kaydı</h1>", unsafe_allow_html=True)
    with st.form("ekle_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            baslik = st.text_input("İlan Başlığı")
            fiyat_input = st.text_input("Fiyat (Sadece Rakam)")
        with col2:
            konum = st.text_input("Bölge / Mahalle")
            # --- GALERİDEN SEÇME BURADA ---
            yuklenen_dosya = st.file_uploader("Kapak Fotoğrafı Seç", type=['png', 'jpg', 'jpeg'])
        
        aciklama = st.text_area("İlan Detayları")
        
        if st.form_submit_button("İlanı Kaydet"):
            if baslik and fiyat_input:
                df = verileri_yukle()
                yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
                
                # Resim İşleme
                resim_yolu = ""
                if yuklenen_dosya is not None:
                    # Resmi klasöre kaydet
                    resim_adi = f"{yeni_id}.jpg"
                    resim_yolu = os.path.join(IMG_FOLDER, resim_adi)
                    with open(resim_yolu, "wb") as f:
                        f.write(yuklenen_dosya.getbuffer())
                
                yeni_veri = {
                    "ID": yeni_id, 
                    "Tarih": datetime.now().strftime("%d/%m/%Y"), 
                    "Baslik": baslik, 
                    "Fiyat": format_para(fiyat_input), 
                    "Konum": konum, 
                    "Aciklama": aciklama,
                    "Foto_Yolu": resim_yolu
                }
                df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.balloons()
                st.success("İlan ve fotoğraf başarıyla eklendi!")
            else:
                st.error("Lütfen gerekli alanları doldurun.")

# 5. İLAN LİSTESİ
elif secim == "🏠 İlan Listesi":
    st.markdown("<h1 style='color: #2b2d33;'>GARANTİ <span style='color: #8CC63F;'>EMLAK</span> PORTFÖY</h1>", unsafe_allow_html=True)
    df = verileri_yukle()
    if not df.empty:
        for i, r in df.iloc[::-1].iterrows():
            # Resim varsa göster, yoksa varsayılan koy
            display_img = r['Foto_Yolu'] if str(r['Foto_Yolu']) != 'nan' and os.path.exists(str(r['Foto_Yolu'])) else "https://via.placeholder.com/1000x250?text=Resim+Yok"
            
            st.markdown(f"""
            <div class="property-card">
                <div class="card-content">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="location-badge">📍 {r['Konum']}</span>
                        <span style="color: #666; font-size: 13px;">📅 {r['Tarih']}</span>
                    </div>
                    <h2 style="margin: 15px 0 5px 0;">{r['Baslik']}</h2>
                    <div class="price-tag">{r['Fiyat']} TL</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # Streamlit'in kendi resim bileşenini kullanıyoruz (Yerel dosyayı okuması için)
            st.image(display_img, use_container_width=True)
            st.markdown(f'<div class="card-content"><p style="color: #444;">{r["Aciklama"]}</p></div></div>', unsafe_allow_html=True)
    else:
        st.info("İlan bulunmuyor.")

# 6. YÖNETİCİ PANELİ
elif secim == "🔐 Yönetici Girişi":
    sifre = st.text_input("Şifre", type="password")
    if sifre == "3363Garanti":
        df = verileri_yukle()
        for i, r in df.iterrows():
            col1, col2 = st.columns([5, 1])
            col1.write(f"**{r['Baslik']}**")
            if col2.button("SİL", key=f"del_{r['ID']}"):
                # Resmi de klasörden sil (opsiyonel)
                if str(r['Foto_Yolu']) != 'nan' and os.path.exists(str(r['Foto_Yolu'])):
                    os.remove(r['Foto_Yolu'])
                df = df.drop(i)
                df.to_csv(DB_FILE, index=False)
                st.rerun()
