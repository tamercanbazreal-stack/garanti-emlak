import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(page_title="GARANTİ EMLAK | Tarsus", page_icon="🏠", layout="wide")

# 2. AYDINLIK TEMA VE TASARIM AYARLARI (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    .property-card {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 0px; /* Fotoğraf için padding'i sıfırladık */
        margin-bottom: 30px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        animation: fadeInUp 0.6s ease-out forwards;
        transition: all 0.3s ease;
        overflow: hidden;
    }
    
    .property-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(140, 198, 63, 0.25);
    }

    .card-content { padding: 20px; }

    h1, h2, h3, p, span { color: #2b2d33 !important; }

    .price-tag {
        color: #4b8a00 !important;
        font-size: 26px;
        font-weight: 900;
    }
    
    .location-badge {
        background-color: #8CC63F;
        color: #ffffff !important;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    section[data-testid="stSidebar"] {
        background-color: #f1f3f5 !important;
        border-right: 1px solid #dee2e6;
    }

    .stButton>button {
        background: linear-gradient(45deg, #8CC63F, #7ab334) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        height: 45px !important;
        border: none !important;
    }
    
    /* Resim Stilini Sabitleme */
    .cover-img {
        width: 100%;
        height: 250px;
        object-fit: cover;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ilanlar.csv"

def verileri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    # Fotoğraf (Foto) sütununu ekledik
    return pd.DataFrame(columns=["ID", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama", "Foto"])

def format_para(sayi):
    try:
        # Gelen verideki noktaları/virgülleri temizleyip sayıya çevir ve formatla
        temiz_sayi = int(''.join(filter(str.isdigit, str(sayi))))
        return f"{temiz_sayi:,}".replace(",", ".")
    except:
        return sayi

# 3. YAN PANEL
with st.sidebar:
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
            # Fiyat girişi (Otomatik virgül için sayı alıyoruz)
            fiyat_input = st.text_input("Fiyat (Sadece Rakam Girin)")
        with col2:
            konum = st.text_input("Bölge / Mahalle")
            foto_link = st.text_input("Kapak Fotoğraf Linki (URL)")
        
        aciklama = st.text_area("İlan Detayları")
        
        if st.form_submit_button("İlanı Kaydet"):
            if baslik and fiyat_input:
                df = verileri_yukle()
                yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
                # Fiyatı formatla
                formatli_fiyat = format_para(fiyat_input)
                # Foto boşsa varsayılan resim koy
                final_foto = foto_link if foto_link else "https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80"
                
                yeni_veri = {
                    "ID": yeni_id, 
                    "Tarih": datetime.now().strftime("%d/%m/%Y"), 
                    "Baslik": baslik, 
                    "Fiyat": formatli_fiyat, 
                    "Konum": konum, 
                    "Aciklama": aciklama,
                    "Foto": final_foto
                }
                df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.balloons()
                st.success(f"İlan {formatli_fiyat} TL fiyatıyla eklendi!")
            else:
                st.error("Lütfen başlık ve fiyat alanlarını doldurun.")

# 5. İLAN LİSTESİ
elif secim == "🏠 İlan Listesi":
    st.markdown("<h1 style='color: #2b2d33;'>GARANTİ <span style='color: #8CC63F;'>EMLAK</span> PORTFÖY</h1>", unsafe_allow_html=True)
    
    df = verileri_yukle()
    ara = st.text_input("🔍 İlanlarda Ara...", placeholder="Örn: 3+1, Tarsus, 2.500.000")
    
    if not df.empty:
        if ara:
            df = df[df.apply(lambda row: row.astype(str).str.contains(ara, case=False).any(), axis=1)]
        
        for i, r in df.iloc[::-1].iterrows():
            # Fotoğraf kontrolü (Eski ilanlar için sütun kontrolü)
            img_url = r['Foto'] if 'Foto' in r and str(r['Foto']) != 'nan' else "https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80"
            
            st.markdown(f"""
            <div class="property-card">
                <img src="{img_url}" class="cover-img">
                <div class="card-content">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="location-badge">📍 {r['Konum']}</span>
                        <span style="color: #666; font-size: 13px;">📅 {r['Tarih']}</span>
                    </div>
                    <h2 style="margin: 15px 0 5px 0; font-size: 22px;">{r['Baslik']}</h2>
                    <div class="price-tag">{r['Fiyat']} TL</div>
                    <p style="color: #444; margin-top: 10px; border-top: 1px solid #eee; padding-top: 10px; font-size: 15px;">{r['Aciklama']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Henüz ilan bulunmuyor.")

# 6. YÖNETİCİ PANELİ
elif secim == "🔐 Yönetici Girişi":
    st.header("Sistem Yönetimi")
    # YENİ ŞİFRE: 3363Garanti
    sifre = st.text_input("Yönetici Şifresi", type="password")
    
    if sifre == "3363Garanti":
        df = verileri_yukle()
        if not df.empty:
            for i, r in df.iterrows():
                col1, col2 = st.columns([5, 1])
                col1.write(f"**{r['Baslik']}** ({r['Fiyat']} TL)")
                if col2.button("SİL", key=f"del_{r['ID']}"):
                    df = df.drop(i)
                    df.to_csv(DB_FILE, index=False)
                    st.rerun()
        else:
            st.info("Silinecek ilan yok.")
    elif sifre:
        st.error("Şifre Yanlış kanka!")
