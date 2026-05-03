import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib

# 1. SAYFA AYARLARI
st.set_page_config(page_title="GARANTİ EMLAK | Yönetim", page_icon="🏠", layout="wide")

LOGO_URL = "https://i.hizliresim.com/iwyt3qr.png"
DB_FILE = "ilanlar_v2.csv"
USER_FILE = "kullanicilar.csv"

# 2. FONKSİYONLAR
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

# 3. TASARIM VE ESKİ MENÜ RENGİ (CSS)
st.markdown(f"""
    <style>
    /* Menü Rengi (Eski Gri/Beyaz Tonu) */
    [data-testid="stSidebar"] {{
        background-color: #f1f3f5 !important;
    }}
    
    /* Kart ve Animasyonlar */
    .property-card {{
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 5px solid #8CC63F;
        transition: 0.3s;
    }}
    .property-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}

    /* Çıkış Butonu Stili (En Altta) */
    .logout-area {{
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 260px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. OTURUM YÖNETİMİ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.username = None

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.image(LOGO_URL, use_container_width=True)
        tab1, tab2 = st.tabs(["🔐 Oturum Aç", "📝 Kayıt Ol"])
        with tab1:
            u_name = st.text_input("Kullanıcı Adı")
            u_pass = st.text_input("Şifre", type="password")
            if st.button("Giriş Yap", use_container_width=True):
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
                        st.error("Hatalı giriş!")
        with tab2:
            new_user = st.text_input("Personel Adı")
            new_pass = st.text_input("Şifre Belirle", type="password")
            if st.button("Kaydet", use_container_width=True):
                users = kullanicilari_yukle()
                if new_user in users['Kullanici'].values:
                    st.warning("Bu kullanıcı adı alınmış.")
                else:
                    new_data = {"Kullanici": new_user, "Sifre": make_hashes(new_pass), "Yetki": "Danışman"}
                    users = pd.concat([users, pd.DataFrame([new_data])], ignore_index=True)
                    users.to_csv(USER_FILE, index=False)
                    st.success("Kayıt tamamlandı!")

# --- ANA PANEL ---
else:
    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.markdown(f"👤 **{st.session_state.username}** ({st.session_state.user_type})")
        st.divider()
        
        # Ana Menü
        ana_menu = ["📋 İlan Portföyü", "➕ Yeni İlan Ekle", "🗺️ Web Tapu Sorgu"]
        if st.session_state.user_type == "Yönetici":
            ana_menu.append("⚙️ Yönetici Paneli")
        
        secim = st.radio("MENÜ", ana_menu)
        
        # En Altta Çıkış Yap
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # 1. İLAN PORTFÖYÜ
    if secim == "📋 İlan Portföyü":
        st.title("🏡 Gayrimenkul Listesi")
        df = verileri_yukle()
        display_df = df if st.session_state.user_type == "Yönetici" else df[df['Sahip'] == st.session_state.username]
        
        if not display_df.empty:
            for i, r in display_df.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="property-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-size:12px; color:gray;">👤 {r['Sahip']} | 📅 {r['Tarih']}</span>
                        <span style="color:#4b8a00; font-weight:bold; font-size:18px;">{r['Fiyat']} TL</span>
                    </div>
                    <h4>{r['Baslik']}</h4>
                    <p><b>📍 {r['Konum']}</b></p>
                    <p style="font-size:14px; color:#555;">{r['Aciklama']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Sil / Satıldı ✅", key=f"del_{r['ID']}"):
                    df = df.drop(i)
                    df.to_csv(DB_FILE, index=False)
                    st.rerun()
        else:
            st.info("Gösterilecek ilan yok.")

    # 2. YENİ İLAN EKLE
    elif secim == "➕ Yeni İlan Ekle":
        st.title("İlan Girişi")
        with st.form("yeni_ilan"):
            b, f = st.columns(2)
            baslik = b.text_input("İlan Başlığı")
            fiyat = f.text_input("Fiyat")
            k, t = st.columns(2)
            konum = k.text_input("Konum")
            tarih = t.date_input("Tarih")
            detay = st.text_area("Detaylı Açıklama")
            if st.form_submit_button("Portföye Ekle"):
                df = verileri_yukle()
                yeni = {"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "Sahip": st.session_state.username, 
                        "Tarih": tarih.strftime("%d/%m/%Y"), "Baslik": baslik, "Fiyat": format_para(fiyat), 
                        "Konum": konum, "Aciklama": detay}
                df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("Eklendi!")

    # 3. YÖNETİCİ PANELİ (Sadece Admin)
    elif secim == "⚙️ Yönetici Paneli" and st.session_state.user_type == "Yönetici":
        st.title("Admin Kontrol Paneli")
        
        tab_ilan, tab_uye = st.tabs(["🗑️ Tüm İlanları Yönet", "👥 Üye Yönetimi"])
        
        with tab_ilan:
            df_all = verileri_yukle()
            if not df_all.empty:
                for i, r in df_all.iterrows():
                    c1, c2 = st.columns([5, 1])
                    c1.write(f"**{r['Sahip']}**: {r['Baslik']} - {r['Fiyat']} TL")
                    if c2.button("SİL", key=f"adm_del_{r['ID']}"):
                        df_all = df_all.drop(i)
                        df_all.to_csv(DB_FILE, index=False)
                        st.rerun()
            else: st.write("İlan yok.")

        with tab_uye:
            users = kullanicilari_yukle()
            if not users.empty:
                for i, r in users.iterrows():
                    c1, c2 = st.columns([5, 1])
                    c1.write(f"👤 **{r['Kullanici']}** - Yetki: {r['Yetki']}")
                    if c2.button("ÜYEYİ SİL", key=f"usr_del_{r['Kullanici']}"):
                        users = users.drop(i)
                        users.to_csv(USER_FILE, index=False)
                        st.rerun()
            else: st.write("Üye yok.")

    # 4. WEB TAPU
    elif secim == "🗺️ Web Tapu Sorgu":
        st.title("Tapu Sorgulama")
        st.link_button("🌐 Web Tapu Portal", "https://webtapu.tkgm.gov.tr/")
        st.link_button("📍 Parsel Sorgulama", "https://parselsorgu.tkgm.gov.tr/")
