import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(page_title="GARANTİ EMLAK | Tarsus", page_icon="🏠", layout="wide")

# 2. SAHİBİNDEN TARZI MODERN TASARIM (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    /* İlan Kartı Düzeni */
    .property-card {
        background-color: #fcfcfc;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #e0e2e6;
        display: flex;
        flex-direction: row; /* Yan yana dizilim */
        overflow: hidden;
        transition: all 0.3s ease;
        height: 180px; /* Sabit yükseklik ile daha düzenli */
    }
    
    .property-card:hover {
        border-color: #8CC63F;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    /* Görsel Alanı (Küçük ve Sabit) */
    .img-container {
        width: 240px;
        min-width: 240px;
        height: 100%;
        background-color: #eee;
    }
    
    .thumb-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* İçerik Alanı */
    .info-container {
        padding: 15px 20px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    h2 { margin: 0; font-size: 18px !important; color: #2b2d33 !important; }
    .price-text { color: #4b8a00 !important; font-size: 22px !important; font-weight: 800; }
    .loc-text { color: #666 !important; font-size: 14px; }
    .desc-text { color: #444 !important; font-size: 14px; line-height: 1.4; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

    section[data-testid="stSidebar"] { background-color: #f1f3f5 !important; }
    
    /* Mobil Uyum */
    @media (max-width: 768px) {
        .property-card { flex-direction: column; height: auto; }
        .img-container { width: 100%; height: 200px; }
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ilanlar.csv"
IMG_FOLDER = "ilan_resimleri"

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
    except: return sayi

# 3. YAN PANEL
with st.sidebar:
    st.image("https://i.hizliresim.com/iwyt3qr.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>GARANTİ EMLAK</h3>", unsafe_allow_html=True)
    st.markdown("---")
    secim = st.radio("MENÜ", ["🏠 İlan Listesi", "➕ Yeni İlan Ekle", "🔐 Yönetici Girişi"])

# 4. YENİ İLAN EKLEME
if secim == "➕ Yeni İlan Ekle":
    st.markdown("<h1 style='color: #4b8a00;'>Yeni Portföy Kaydı</h1>", unsafe_allow_html=True)
    with st.form("ekle_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            baslik = st.text_input("İlan Başlığı")
            fiyat_input = st.text_input("Fiyat (Sadece Rakam)")
        with col2:
            konum = st.text_input("Bölge / Mahalle")
            yuklenen_dosya = st.file_uploader("Daire Görseli Seç", type=['png', 'jpg', 'jpeg'])
        
        aciklama = st.text_area("İlan Detayları")
        
        if st.form_submit_button("İlanı Kaydet"):
            if baslik and fiyat_input:
                df = verileri_yukle()
                yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
                resim_yolu = ""
                if yuklenen_dosya:
                    resim_adi = f"{yeni_id}.jpg"
                    resim_yolu = os.path.join(IMG_FOLDER, resim_adi)
                    with open(resim_yolu, "wb") as f:
                        f.write(yuklenen_dosya.getbuffer())
                
                yeni_veri = {"ID": yeni_id, "Tarih": datetime.now().strftime("%d/%m/%Y"), "Baslik": baslik, "Fiyat": format_para(fiyat_input), "Konum": konum, "Aciklama": aciklama, "Foto_Yolu": resim_yolu}
                df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("İlan eklendi!")
                st.rerun()

# 5. İLAN LİSTESİ (SAHİBİNDEN STİLİ)
elif secim == "🏠 İlan Listesi":
    st.markdown("<h1 style='color: #2b2d33;'>PORTFÖYÜMÜZ</h1>", unsafe_allow_html=True)
    df = verileri_yukle()
    ara = st.text_input("🔍 Kelime veya konum ile ara...")
    
    if not df.empty:
        if ara:
            df = df[df.apply(lambda row: row.astype(str).str.contains(ara, case=False).any(), axis=1)]
        
        for i, r in df.iloc[::-1].iterrows():
            img_path = r['Foto_Yolu'] if str(r['Foto_Yolu']) != 'nan' and os.path.exists(str(r['Foto_Yolu'])) else "https://via.placeholder.com/240x180?text=Goruntu+Yok"
            
            # Kart Yapısı
            st.markdown(f"""
            <div class="property-card">
                <div class="img-container">
                    <img src="data:image/png;base64," class="thumb-img" id="img_{r['ID']}">
                </div>
                <div class="info-container">
                    <div>
                        <h2>{r['Baslik']}</h2>
                        <p class="loc-text">📍 {r['Konum']} | 📅 {r['Tarih']}</p>
                    </div>
                    <p class="desc-text">{r['Aciklama']}</p>
                    <div class="price-text">{r['Fiyat']} TL</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # Resim streamlit üzerinden gösteriliyor (Local dosya erişimi için)
            with st.container():
                cols = st.columns([1.5, 3])
                with cols[0]:
                    st.image(img_path, use_container_width=True)
                with cols[1]:
                    st.empty() # Düzeni korumak için

# 6. YÖNETİCİ PANELİ
elif secim == "🔐 Yönetici Girişi":
    sifre = st.text_input("Şifre", type="password")
    if sifre == "3363Garanti":
        df = verileri_yukle()
        for i, r in df.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(f"**{r['Baslik']}** ({r['Fiyat']} TL)")
            if c2.button("SİL", key=f"del_{r['ID']}"):
                if str(r['Foto_Yolu']) != 'nan' and os.path.exists(str(r['Foto_Yolu'])):
                    os.remove(r['Foto_Yolu'])
                df = df.drop(i)
                df.to_csv(DB_FILE, index=False)
                st.rerun()
