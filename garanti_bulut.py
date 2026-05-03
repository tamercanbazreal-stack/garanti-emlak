import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib

# 1. SAYFA AYARLARI
st.set_page_config(page_title="GARANTİ EMLAK | Kurumsal Panel", page_icon="🏢", layout="wide")

# Veritabanı Dosyaları
DB_FILE = "ilanlar_v2.csv"
USER_FILE = "kullanicilar.csv"

# 2. GÜVENLİK VE ŞİFRELEME
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# 3. VERİ YÖNETİMİ
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

# 4. TASARIM (CSS)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stSidebar { background-color: #1e293b !important; color: white !important; }
    .stSidebar [data-testid="stMarkdownContainer"] p { color: white !important; font-weight: 600; }
    
    .user-badge {
        padding: 5px 12px;
        border-radius: 20px;
        background-color: #e2e8f0;
        color: #475569;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 20px;
        display: inline-block;
    }
    
    .property-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 6px solid #10b981;
    }
    </style>
    """, unsafe_allow_html=True)

# 5. OTURUM YÖNETİMİ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.username = None

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.image("https://i.hizliresim.com/iwyt3qr.png", width=200)
        tab1, tab2 = st.tabs(["🔐 Giriş Yap", "📝 Personel Kaydı"])
        
        with tab1:
            u_name = st.text_input("Kullanıcı Adı", key="login_user")
            u_pass = st.text_input("Şifre", type="password", key="login_pass")
            if st.button("Sisteme Gir"):
                users = kullanicilari_yukle()
                hashed_pswd = make_hashes(u_pass)
                
                # Admin Kontrolü
                if u_name == "admin" and u_pass == "3363Garanti":
                    st.session_state.logged_in = True
                    st.session_state.user_type = "Yönetici"
                    st.session_state.username = "admin"
                    st.rerun()
                
                # Personel Kontrolü
                user_record = users[(users['Kullanici'] == u_name) & (users['Sifre'] == hashed_pswd)]
                if not user_record.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_type = "Danışman"
                    st.session_state.username = u_name
                    st.rerun()
                else:
                    st.error("Hatalı giriş!")

        with tab2:
            new_user = st.text_input("Yeni Kullanıcı Adı")
            new_pass = st.text_input("Yeni Şifre", type="password")
            confirm_pass = st.text_input("Şifre Tekrar", type="password")
            if st.button("Kaydı Tamamla"):
                if new_pass == confirm_pass:
                    users = kullanicilari_yukle()
                    if new_user in users['Kullanici'].values or new_user == "admin":
                        st.warning("Bu kullanıcı adı zaten alınmış.")
                    else:
                        new_data = {"Kullanici": new_user, "Sifre": make_hashes(new_pass), "Yetki": "Danışman"}
                        users = pd.concat([users, pd.DataFrame([new_data])], ignore_index=True)
                        users.to_csv(USER_FILE, index=False)
                        st.success("Kaydınız oluşturuldu. Giriş yapabilirsiniz.")
                else:
                    st.error("Şifreler uyuşmuyor!")

# --- ANA PANEL ---
else:
    with st.sidebar:
        st.markdown(f"### 🏢 GARANTİ EMLAK")
        st.markdown(f"<div class='user-badge'>{st.session_state.user_type}: {st.session_state.username}</div>", unsafe_allow_html=True)
        
        # MENÜ TASARIMI
        st.markdown("---")
        menu = st.radio("ANA MENÜ", 
                        ["📋 İlan Portföyü", "➕ İlan Ekle", "🗺️ Web Tapu", "🚪 Oturumu Kapat"])
        
        if st.session_state.user_type == "Yönetici":
            st.markdown("---")
            admin_menu = st.checkbox("⚙️ Yönetim Paneli")

    # 1. İLAN PORTFÖYÜ
    if menu == "📋 İlan Portföyü":
        st.title("🏡 Gayrimenkul Portföyü")
        df = verileri_yukle()
        
        # Filtreleme: Admin her şeyi görür, personel sadece kendi ilanlarını
        if st.session_state.user_type == "Danışman":
            user_df = df[df['Sahip'] == st.session_state.username]
            st.info(f"Kendi portföyünüzde {len(user_df)} ilan listeleniyor.")
        else:
            user_df = df
            st.info(f"Sistem genelinde toplam {len(user_df)} ilan bulunuyor.")

        if not user_df.empty:
            for i, r in user_df.iloc[::-1].iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="property-card">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color:#666; font-size:12px;">👤 Ekleyen: {r['Sahip']} | 📅 {r['Tarih']}</span>
                            <span style="color:#10b981; font-weight:bold; font-size:20px;">{r['Fiyat']} TL</span>
                        </div>
                        <h3 style="margin: 10px 0;">{r['Baslik']}</h3>
                        <p style="color:#475569;">📍 {r['Konum']}</p>
                        <p style="font-size:14px; color:#1e293b; background:#f1f5f9; padding:10px; border-radius:5px;">{r['Aciklama']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"İlanı Sil / Satıldı", key=f"del_{r['ID']}"):
                        df = df.drop(i)
                        df.to_csv(DB_FILE, index=False)
                        st.rerun()
        else:
            st.write("Henüz ilan eklenmemiş.")

    # 2. İLAN EKLE
    elif menu == "➕ İlan Ekle":
        st.title("Yeni Portföy Girişi")
        with st.form("ilan_form"):
            c1, c2 = st.columns(2)
            with c1:
                baslik = st.text_input("İlan Başlığı")
                fiyat = st.text_input("Fiyat")
            with c2:
                konum = st.text_input("Mahalle / Bölge")
                tarih = st.date_input("Kayıt Tarihi")
            
            aciklama = st.text_area("İlan Detayları")
            
            if st.form_submit_button("Portföye Kaydet"):
                df = verileri_yukle()
                yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
                yeni_veri = {
                    "ID": yeni_id,
                    "Sahip": st.session_state.username,
                    "Tarih": tarih.strftime("%d/%m/%Y"),
                    "Baslik": baslik,
                    "Fiyat": format_para(fiyat),
                    "Konum": konum,
                    "Aciklama": aciklama
                }
                df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("İlan başarıyla kendi portföyünüze eklendi!")

    # 3. WEB TAPU
    elif menu == "🗺️ Web Tapu":
        st.title("Tapu İşlemleri")
        st.link_button("🌐 Web Tapu Portal", "https://webtapu.tkgm.gov.tr/")
        st.link_button("🗺️ Parsel Sorgulama", "https://parselsorgu.tkgm.gov.tr/")

    # 4. YÖNETİCİ ÖZEL PANELİ
    if st.session_state.user_type == "Yönetici" and admin_menu:
        st.divider()
        st.subheader("👥 Personel Yönetimi")
        users = kullanicilari_yukle()
        st.dataframe(users[["Kullanici", "Yetki"]], use_container_width=True)
        if st.button("Tüm İlanları Sıfırla (Kritik)"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

    # 5. ÇIKIŞ
    if menu == "🚪 Oturumu Kapat":
        st.session_state.logged_in = False
        st.rerun()
