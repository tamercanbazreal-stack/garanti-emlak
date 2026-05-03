import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib

# 1. SAYFA AYARLARI
st.set_page_config(page_title="GARANTİ EMLAK | Kurumsal Panel", page_icon="🏢", layout="wide")

# Logo URL (Daha önce kullandığımız logo)
LOGO_URL = "https://i.hizliresim.com/iwyt3qr.png"
DB_FILE = "ilanlar_v2.csv"
USER_FILE = "kullanicilar.csv"

# 2. GÜVENLİK VE VERİ FONKSİYONLARI
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def verileri_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])

def kullanicilari_yukle():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    return pd.DataFrame(columns=["Kullanici", "Sifre", "Yetki"])

def format_para(sayi):
    try:
        temiz_sayi = int(''.join(filter(str.isdigit, str(sayi))))
        return f"{temiz_sayi:,}".replace(",", ".")
    except: return sayi

# 3. GELİŞMİŞ ANİMASYONLU TASARIM (CSS)
st.markdown(f"""
    <style>
    /* Arkaplan ve Genel */
    .stApp {{ background-color: #f8fafc; }}
    
    /* Giriş Ekranı Animasyonu */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .login-container {{
        animation: fadeIn 0.8s ease-out;
    }}

    /* Kart Animasyonları */
    .property-card {{
        background: white;
        padding: 22px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 8px solid #8CC63F;
        transition: all 0.3s ease;
    }}
    .property-card:hover {{
        transform: scale(1.02);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.2);
        border-left: 8px solid #4b8a00;
    }}

    /* Sidebar Tasarımı */
    .stSidebar {{ background-color: #0f172a !important; }}
    .stSidebar [data-testid="stMarkdownContainer"] p {{ color: #e2e8f0 !important; }}
    
    /* Buton Animasyonları */
    .stButton>button {{
        transition: all 0.2s ease;
        border-radius: 10px;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: #8CC63F !important;
        color: white !important;
        transform: translateY(-2px);
    }}

    /* Web Tapu Kartı Animasyonu */
    .tapu-card {{
        background: linear-gradient(135deg, #004a99, #002d5c);
        color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        transition: transform 0.4s;
    }}
    .tapu-card:hover {{ transform: rotate(1deg); }}
    </style>
    """, unsafe_allow_html=True)

# 4. OTURUM KONTROLÜ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.username = None

# --- GİRİŞ EKRANI (Logo ve Animasyon) ---
if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.image(LOGO_URL, use_container_width=True)
        st.markdown("<h2 style='text-align:center; color:#1e293b;'>Personel Giriş Paneli</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Oturum Aç", "📝 Personel Kayıt"])
        
        with tab1:
            u_name = st.text_input("Kullanıcı Adı")
            u_pass = st.text_input("Şifre", type="password")
            if st.button("Giriş Yap"):
                if u_name == "admin" and u_pass == "3363Garanti":
                    st.session_state.logged_in = True
                    st.session_state.user_type = "Yönetici"
                    st.session_state.username = "admin"
                    st.rerun()
                else:
                    users = kullanicilari_yukle()
                    hashed_pswd = make_hashes(u_pass)
                    user_record = users[(users['Kullanici'] == u_name) & (users['Sifre'] == hashed_pswd)]
                    if not user_record.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_type = "Danışman"
                        st.session_state.username = u_name
                        st.rerun()
                    else:
                        st.error("❌ Hatalı Kullanıcı Adı veya Şifre")
        
        with tab2:
            new_user = st.text_input("Yeni Personel Kullanıcı Adı")
            new_pass = st.text_input("Yeni Personel Şifresi", type="password")
            if st.button("Kaydı Onayla"):
                if len(new_pass) < 4:
                    st.error("Şifre çok kısa!")
                else:
                    users = kullanicilari_yukle()
                    if new_user in users['Kullanici'].values:
                        st.warning("Bu isimde bir personel zaten kayıtlı.")
                    else:
                        new_data = {"Kullanici": new_user, "Sifre": make_hashes(new_pass), "Yetki": "Danışman"}
                        users = pd.concat([users, pd.DataFrame([new_data])], ignore_index=True)
                        users.to_csv(USER_FILE, index=False)
                        st.success("✅ Kayıt başarılı! Giriş sekmesine geçebilirsiniz.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANA PANEL ---
else:
    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.markdown(f"<div style='text-align:center; color:white;'><b>{st.session_state.user_type}</b><br>{st.session_state.username}</div>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("DASHBOARD", ["📋 Portföyüm", "➕ Yeni İlan Ekle", "📄 Web Tapu", "🚪 Güvenli Çıkış"])

    # 1. PORTFÖYÜM (Animasyonlu Kartlar)
    if menu == "📋 Portföyüm":
        st.title("🏡 Gayrimenkul Listesi")
        df = verileri_yukle()
        
        # Filtreleme
        display_df = df if st.session_state.user_type == "Yönetici" else df[df['Sahip'] == st.session_state.username]
        
        if not display_df.empty:
            for i, r in display_df.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="property-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size:12px; color:#64748b;">👤 Danışman: {r['Sahip']} | 📅 {r['Tarih']}</span>
                        <span style="font-size:22px; color:#4b8a00; font-weight:800;">{r['Fiyat']} TL</span>
                    </div>
                    <h3 style="margin:10px 0; color:#0f172a;">{r['Baslik']}</h3>
                    <p style="color:#334155; font-weight:600;">📍 {r['Konum']}</p>
                    <div style="background:#f8fafc; padding:12px; border-radius:8px; color:#475569; font-size:14px;">
                        {r['Aciklama']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"İlanı Sil / Satıldı ✅", key=f"del_{r['ID']}"):
                    df = df.drop(i)
                    df.to_csv(DB_FILE, index=False)
                    st.rerun()
        else:
            st.info("Henüz eklenmiş bir ilan bulunmuyor.")

    # 2. YENİ İLAN EKLE
    elif menu == "➕ Yeni İlan Ekle":
        st.title("Yeni İlan Kaydı")
        with st.form("ilan_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                baslik = st.text_input("İlan Başlığı")
                fiyat = st.text_input("Fiyat (TL)")
            with c2:
                konum = st.text_input("Konum (Mahalle/Sokak)")
                tarih = st.date_input("Kayıt Tarihi")
            
            aciklama = st.text_area("İlan Detayları")
            if st.form_submit_button("İlanı Yayına Al"):
                df = verileri_yukle()
                yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
                yeni_veri = {
                    "ID": yeni_id, "Sahip": st.session_state.username, 
                    "Tarih": tarih.strftime("%d/%m/%Y"), "Baslik": baslik, 
                    "Fiyat": format_para(fiyat), "Konum": konum, "Aciklama": aciklama
                }
                df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("İlan başarıyla eklendi!")

    # 3. WEB TAPU (Efektli)
    elif menu == "📄 Web Tapu":
        st.markdown("""
        <div class="tapu-card">
            <h2>WEB TAPU PORTALI</h2>
            <p>Taşınmaz işlemleriniz için resmi bağlantıları kullanın.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        c1, c2 = st.columns(2)
        c1.link_button("🌐 Web Tapu Giriş", "https://webtapu.tkgm.gov.tr/")
        c2.link_button("📍 Parsel Sorgulama", "https://parselsorgu.tkgm.gov.tr/")

    # 4. ÇIKIŞ
    elif menu == "🚪 Güvenli Çıkış":
        st.session_state.logged_in = False
        st.rerun()
