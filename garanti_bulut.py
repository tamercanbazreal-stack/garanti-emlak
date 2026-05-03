import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib
import random

# 1. SAYFA AYARLARI VE DOSYALAR
st.set_page_config(page_title="GARANTİ EMLAK | Yönetim Paneli", page_icon="🏠", layout="wide")
LOGO_URL = "https://i.hizliresim.com/iwyt3qr.png"

DB_FILE = "ilanlar_v3.csv"
USER_FILE = "kullanicilar_v3.csv"
SHARED_FILE = "paylasimlar.csv"
RANDEVU_FILE = "randevular_v2.csv"

# 2. FONKSİYONLAR
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def verileri_yukle(dosya, sutunlar):
    if os.path.exists(dosya):
        try:
            return pd.read_csv(dosya)
        except:
            return pd.DataFrame(columns=sutunlar)
    return pd.DataFrame(columns=sutunlar)

def portfoy_no_uret():
    return str(random.randint(100000, 999999))

def format_para(sayi):
    try:
        temiz = ''.join(filter(str.isdigit, str(sayi)))
        return f"{int(temiz):,}".replace(",", ".")
    except: return sayi

# 3. TASARIM
st.markdown("""
    <style>
    .property-card {
        background: white; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px;
        border-left: 5px solid #8CC63F;
    }
    .share-card {
        background: #f0f7ff; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px;
        border-left: 5px solid #007bff;
    }
    .p-no { background: #333; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 4. OTURUM YÖNETİMİ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.image(LOGO_URL, use_container_width=True)
        tab1, tab2 = st.tabs(["🔐 Giriş Yap", "📝 Personel Kaydı"])
        with tab1:
            u_name = st.text_input("Kullanıcı Adı")
            u_pass = st.text_input("Şifre", type="password")
            if st.button("Sisteme Giriş", key="login_btn", use_container_width=True):
                if u_name == "admin" and u_pass == "3363Garanti":
                    st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Yönetici", "admin"
                    st.rerun()
                else:
                    users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                    if not users[(users['Kullanici'] == u_name) & (users['Sifre'] == make_hashes(u_pass))].empty:
                        st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Danışman", u_name
                        st.rerun()
                    else: st.error("Giriş bilgileri hatalı!")
        with tab2:
            st.info("Yeni personel hesabı oluşturun.")
            new_u = st.text_input("Yeni Kullanıcı Adı")
            new_p = st.text_input("Yeni Şifre", type="password")
            if st.button("Kayıt Ol", use_container_width=True):
                users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                if new_u in users['Kullanici'].values:
                    st.warning("Bu kullanıcı adı zaten var.")
                elif new_u and new_p:
                    yeni_user = pd.DataFrame([{"Kullanici": new_u, "Sifre": make_hashes(new_p), "Yetki": "Danışman"}])
                    pd.concat([users, yeni_user]).to_csv(USER_FILE, index=False)
                    st.success("Kayıt başarılı!")

# --- ANA PANEL ---
else:
    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.write(f"👤 **{st.session_state.username}**")
        st.divider()
        menu = ["📋 Portföy & Paylaşım", "➕ İlan Ekle", "📅 Özel Randevular"]
        if st.session_state.user_type == "Yönetici": menu.append("⚙️ Yönetici")
        secim = st.radio("MENÜ", menu)
        st.divider()
        if st.button("🚪 Çıkış Yap"):
            st.session_state.logged_in = False
            st.rerun()

    # 1. PORTFÖY VE PAYLAŞIM
    if secim == "📋 Portföy & Paylaşım":
        st.title("🏡 Gayrimenkul Yönetimi")
        
        df = verileri_yukle(DB_FILE, ["ID", "P_No", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
        paylasimlar = verileri_yukle(SHARED_FILE, ["IlanID", "Paylasan", "Paylasilan"])
        
        # Paylaşılan ilanların IDsini al
        pay_idleri = paylasimlar[paylasimlar['Paylasilan'] == st.session_state.username]['IlanID'].astype(str).tolist()
        
        # İstatistik Sayacı
        c1, c2 = st.columns(2)
        c1.metric("Kendi İlanlarım", len(df[df['Sahip'] == st.session_state.username]))
        c2.metric("Sizinle Paylaşılanlar", len(pay_idleri))
        
        st.divider()
        
        t1, t2 = st.tabs(["📂 Benim Portföyüm", "🔗 Paylaşılan İlanlar"])
        
        with t1:
            kendi_df = df[df['Sahip'] == st.session_state.username]
            if kendi_df.empty: st.info("Henüz ilan eklemediniz.")
            for i, r in kendi_df.iloc[::-1].iterrows():
                with st.container():
                    st.markdown(f"""<div class="property-card">
                        <span class="p-no">No: {r['P_No']}</span><br>
                        <b>{r['Baslik']}</b> | <span style="color:green;">{r['Fiyat']} TL</span><br>
                        <small>📍 {r['Konum']} | 🗓 {r['Tarih']}</small>
                    </div>""", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 3])
                    if col1.button("🗑️ Sil", key=f"d_{r['ID']}"):
                        df[df['ID'] != r['ID']].to_csv(DB_FILE, index=False)
                        st.rerun()
                    with col2:
                        u_list = verileri_yukle(USER_FILE, ["Kullanici"])['Kullanici'].tolist()
                        digerleri = [u for u in u_list if u != st.session_state.username]
                        if digerleri:
                            target = st.selectbox("Paylaşılacak Kişi:", digerleri, key=f"s_{r['ID']}")
                            if st.button("Danışmana Gönder", key=f"p_{r['ID']}"):
                                pd.concat([paylasimlar, pd.DataFrame([{"IlanID": r['ID'], "Paylasan": st.session_state.username, "Paylasilan": target}])]).to_csv(SHARED_FILE, index=False)
                                st.success("Paylaşıldı!")

        with t2:
            paylasilan_df = df[df['ID'].astype(str).isin(pay_idleri)]
            if paylasilan_df.empty: st.info("Sizinle paylaşılan bir ilan yok.")
            for i, r in paylasilan_df.iloc[::-1].iterrows():
                paylasan_kisi = paylasimlar[paylasimlar['IlanID'].astype(str) == str(r['ID'])]['Paylasan'].values[0]
                st.markdown(f"""<div class="share-card">
                    <span class="p-no">No: {r['P_No']}</span><br>
                    <b>{r['Baslik']}</b> | <span style="color:green;">{r['Fiyat']} TL</span><br>
                    <small>📍 {r['Konum']} | 👤 Gönderen: {paylasan_kisi}</small><br>
                    <p style='font-size:13px; color:#555;'>{r['Aciklama']}</p>
                </div>""", unsafe_allow_html=True)

    # 2. İLAN EKLE (Öncekiyle aynı)
    elif secim == "➕ İlan Ekle":
        with st.form("ilan_ekle"):
            st.subheader("Yeni Portföy Kaydı")
            b = st.text_input("Başlık"); f = st.text_input("Fiyat"); k = st.text_input("Konum"); a = st.text_area("Açıklama")
            if st.form_submit_button("Kaydet"):
                df = verileri_yukle(DB_FILE, ["ID", "P_No", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
                yeni = {"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "P_No": portfoy_no_uret(), "Sahip": st.session_state.username, "Tarih": datetime.now().strftime("%d/%m/%Y"), "Baslik": b, "Fiyat": format_para(f), "Konum": k, "Aciklama": a}
                pd.concat([df, pd.DataFrame([yeni])]).to_csv(DB_FILE, index=False)
                st.success(f"İlan {yeni['P_No']} no ile eklendi!")

    # 3. ÖZEL RANDEVULAR
    elif secim == "📅 Özel Randevular":
        st.title("Müşteri Takvimi")
        r_df = verileri_yukle(RANDEVU_FILE, ["Ekleyen", "Tarih", "Saat", "Musteri", "Ilan_No"])
        df_ilanlar = verileri_yukle(DB_FILE, ["P_No", "Baslik"])
        ilan_secenekleri = [f"{row['P_No']} - {row['Baslik']}" for _, row in df_ilanlar.iterrows()]
        
        with st.expander("➕ Yeni Randevu Ekle"):
            with st.form("r_form"):
                d = st.date_input("Gün"); s = st.time_input("Saat"); m = st.text_input("Müşteri"); secilen_ilan = st.selectbox("İlan No", ilan_secenekleri)
                if st.form_submit_button("Kaydet"):
                    p_no = secilen_ilan.split(" - ")[0]
                    yeni_r = pd.DataFrame([{"Ekleyen": st.session_state.username, "Tarih": str(d), "Saat": str(s), "Musteri": m, "Ilan_No": p_no}])
                    pd.concat([r_df, yeni_r]).to_csv(RANDEVU_FILE, index=False)
                    st.rerun()
        
        display_r = r_df if st.session_state.user_type == "Yönetici" else r_df[r_df['Ekleyen'] == st.session_state.username]
        st.table(display_r)

    # 4. YÖNETİCİ
    elif secim == "⚙️ Yönetici" and st.session_state.user_type == "Yönetici":
        st.title("Yönetici Paneli")
        st.table(verileri_yukle(USER_FILE, ["Kullanici", "Yetki"]))
