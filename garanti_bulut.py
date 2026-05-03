import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(page_title="GARANTİ EMLAK | Tarsus", page_icon="🏠", layout="wide")

# 2. GELİŞMİŞ TASARIM (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    /* İlan Kartları */
    .property-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #8CC63F;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .price-tag { color: #4b8a00 !important; font-size: 24px !important; font-weight: 800; }
    
    /* Web Tapu ve Butonlar */
    .web-tapu-card {
        background: linear-gradient(135deg, #004a99, #003366);
        color: white !important;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
    }
    .stButton>button { width: 100%; border-radius: 8px; height: 45px; font-weight: bold; }
    
    /* Yönetici Giriş Alanı */
    .admin-box {
        max-width: 400px;
        margin: 50px auto;
        padding: 30px;
        border: 1px solid #ddd;
        border-radius: 15px;
        background-color: #f9f9f9;
        text-align: center;
    }
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

# Session State ile Giriş Kontrolü
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# 3. YAN PANEL (SIDEBAR)
with st.sidebar:
    st.image("https://i.hizliresim.com/iwyt3qr.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>GARANTİ EMLAK</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Menü Seçenekleri (Giriş durumuna göre değişir)
    menu_options = ["🏠 Ana Sayfa / Portföy", "📄 Web Tapu İşlemleri"]
    if st.session_state.admin_logged_in:
        menu_options.append("➕ Yeni İlan Ekle")
        menu_options.append("⚙️ İlan Yönetimi")
        menu_options.append("🚪 Çıkış Yap")
    else:
        menu_options.append("🔐 Yönetici Girişi")
        
    secim = st.radio("MENÜ", menu_options)

# 4. ANA SAYFA / PORTFÖY
if secim == "🏠 Ana Sayfa / Portföy":
    st.markdown("<h1 style='color: #2b2d33;'>Tarsus Güncel Emlak Portföyü</h1>", unsafe_allow_html=True)
    df = verileri_yukle()
    ara = st.text_input("🔍 İlanlarda ara (Mahalle, oda sayısı vb. yazın...)")
    
    if not df.empty:
        if ara:
            df = df[df.apply(lambda row: row.astype(str).str.contains(ara, case=False).any(), axis=1)]
        
        for i, r in df.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="property-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <p style="color:#666; font-size:13px; margin:0;">📍 {r['Konum']} | 📅 {r['Tarih']}</p>
                        <h2 style="margin-top:5px;">{r['Baslik']}</h2>
                    </div>
                    <div class="price-tag">{r['Fiyat']} TL</div>
                </div>
                <hr style="margin: 12px 0; border: none; border-top: 1px dashed #ccc;">
                <p style="color:#444;">{r['Aciklama']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Şu an yayında ilan bulunmamaktadır.")

# 5. WEB TAPU ÖZELLİĞİ
elif secim == "📄 Web Tapu İşlemleri":
    st.markdown("<h1 style='color: #004a99;'>Web Tapu Sistemi</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="web-tapu-card">
        <h3>TKGM Web Tapu Portalı</h3>
        <p>Tapu ve Kadastro Genel Müdürlüğü sistemine hızlı erişim sağlayarak randevu alabilir veya taşınmaz bilgilerinizi sorgulayabilirsiniz.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button("🌐 Web Tapu Giriş", "https://webtapu.tkgm.gov.tr/")
    with col2:
        st.link_button("🗺️ Parsel Sorgu", "https://parselsorgu.tkgm.gov.tr/")
    with col3:
        st.link_button("📅 Randevu Al", "https://randevu.tkgm.gov.tr/")
        
    st.info("💡 Not: Bu işlemler için e-Devlet şifreniz gerekmektedir.")

# 6. YÖNETİCİ GİRİŞİ (Geliştirilmiş)
elif secim == "🔐 Yönetici Girişi":
    st.markdown("<div class='admin-box'>", unsafe_allow_html=True)
    st.subheader("Yönetici Girişi")
    kullanici = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap"):
        # Şifre bilgini buradan güncelleyebilirsin kanka
        if kullanici == "admin" and sifre == "3363Garanti":
            st.session_state.admin_logged_in = True
            st.success("Giriş Başarılı! Menüden 'Yeni İlan Ekle' seçeneğine gidebilirsiniz.")
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre!")
    st.markdown("</div>", unsafe_allow_html=True)

# 7. YENİ İLAN EKLEME (Sadece Giriş Yapılmışsa)
elif secim == "➕ Yeni İlan Ekle" and st.session_state.admin_logged_in:
    st.markdown("<h1 style='color: #4b8a00;'>Yeni Portföy Kaydı</h1>", unsafe_allow_html=True)
    with st.form("yeni_ilan_form"):
        c1, c2 = st.columns(2)
        with c1:
            baslik = st.text_input("İlan Başlığı")
            fiyat = st.text_input("Fiyat")
        with c2:
            konum = st.text_input("Konum (Mahalle/İlçe)")
            tarih = st.date_input("İlan Tarihi")
            
        aciklama = st.text_area("İlan Detayları")
        if st.form_submit_button("Sisteme Kaydet"):
            df = verileri_yukle()
            yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
            yeni_veri = {"ID": yeni_id, "Tarih": tarih.strftime("%d/%m/%Y"), "Baslik": baslik, "Fiyat": format_para(fiyat), "Konum": konum, "Aciklama": aciklama}
            df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("İlan eklendi!")

# 8. İLAN YÖNETİMİ / SİLME
elif secim == "⚙️ İlan Yönetimi" and st.session_state.admin_logged_in:
    st.subheader("İlanları Düzenle / Sil")
    df = verileri_yukle()
    if not df.empty:
        for i, r in df.iterrows():
            col_ad, col_sil = st.columns([6, 1])
            col_ad.write(f"**{r['Baslik']}** ({r['Fiyat']} TL)")
            if col_sil.button("❌", key=f"sil_{r['ID']}"):
                df = df.drop(i)
                df.to_csv(DB_FILE, index=False)
                st.rerun()
    else:
        st.write("Silinecek ilan yok.")

# 9. ÇIKIŞ YAP
elif secim == "🚪 Çıkış Yap":
    st.session_state.admin_logged_in = False
    st.rerun()
