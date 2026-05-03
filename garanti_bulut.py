import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(page_title="GARANTİ EMLAK | Tarsus", page_icon="🏠", layout="wide")

# 2. TEMİZ VE HIZLI TASARIM (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    .property-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #8CC63F;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    h2 { margin: 0; font-size: 20px !important; color: #2b2d33 !important; }
    .price-tag { color: #4b8a00 !important; font-size: 24px !important; font-weight: 800; }
    .loc-text { color: #666 !important; font-size: 14px; margin-bottom: 10px; }
    .desc-text { color: #444 !important; font-size: 15px; line-height: 1.5; }

    section[data-testid="stSidebar"] { background-color: #f1f3f5 !important; }
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ilanlar.csv"

def verileri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])

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

# 4. YENİ İLAN EKLEME (Görsel Bölümü Kaldırıldı)
if secim == "➕ Yeni İlan Ekle":
    st.markdown("<h1 style='color: #4b8a00;'>Yeni Portföy Kaydı</h1>", unsafe_allow_html=True)
    with st.form("ekle_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            baslik = st.text_input("İlan Başlığı")
            fiyat_input = st.text_input("Fiyat (Sadece Rakam)")
        with col2:
            konum = st.text_input("Bölge / Mahalle")
            tarih_manuel = st.date_input("İlan Tarihi", datetime.now())
        
        aciklama = st.text_area("İlan Detayları (Metrekare, Oda Sayısı vb.)")
        
        if st.form_submit_button("İlanı Portföye Ekle"):
            if baslik and fiyat_input:
                df = verileri_yukle()
                yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
                
                yeni_veri = {
                    "ID": yeni_id, 
                    "Tarih": tarih_manuel.strftime("%d/%m/%Y"), 
                    "Baslik": baslik, 
                    "Fiyat": format_para(fiyat_input), 
                    "Konum": konum, 
                    "Aciklama": aciklama
                }
                df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("İlan başarıyla eklendi!")
                st.rerun()

# 5. İLAN LİSTESİ (Saf Bilgi Odaklı)
elif secim == "🏠 İlan Listesi":
    st.markdown("<h1 style='color: #2b2d33;'>GÜNCEL PORTFÖYÜMÜZ</h1>", unsafe_allow_html=True)
    df = verileri_yukle()
    
    # Arama Kutusu
    ara = st.text_input("🔍 İlanlarda ara (Mahalle veya özellik yazın...)")
    
    if not df.empty:
        if ara:
            df = df[df.apply(lambda row: row.astype(str).str.contains(ara, case=False).any(), axis=1)]
        
        for i, r in df.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="property-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <p class="loc-text">📍 {r['Konum']} | 📅 {r['Tarih']}</p>
                        <h2>{r['Baslik']}</h2>
                    </div>
                    <div class="price-tag">{r['Fiyat']} TL</div>
                </div>
                <hr style="margin: 15px 0; border: none; border-top: 1px dashed #ddd;">
                <p class="desc-text">{r['Aciklama']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sistemde kayıtlı ilan bulunamadı.")

# 6. YÖNETİCİ PANELİ
elif secim == "🔐 Yönetici Girişi":
    sifre = st.text_input("Şifre", type="password")
    if sifre == "3363Garanti":
        st.write("### İlan Yönetimi")
        df = verileri_yukle()
        if not df.empty:
            for i, r in df.iterrows():
                col_y, col_b = st.columns([4, 1])
                col_y.write(f"**{r['Baslik']}** - {r['Fiyat']} TL")
                if col_b.button("SİL", key=f"del_{r['ID']}"):
                    df = df.drop(i)
                    df.to_csv(DB_FILE, index=False)
                    st.rerun()
