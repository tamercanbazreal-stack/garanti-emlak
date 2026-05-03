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

def portfoy_no_uret():
    return str(random.randint(100000, 999999))

def verileri_yukle(dosya, sutunlar):
    if os.path.exists(dosya):
        try:
            df = pd.read_csv(dosya)
            for col in sutunlar:
                if col not in df.columns:
                    if col == "P_No":
                        df[col] = [portfoy_no_uret() for _ in range(len(df))]
                    else:
                        df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=sutunlar)
    return pd.DataFrame(columns=sutunlar)

def format_para(sayi):
    try:
        temiz = ''.join(filter(str.isdigit, str(sayi)))
        return f"{int(temiz):,}".replace(",", ".")
    except: return sayi

# 3. TASARIM (İLAN NUMARALARI BÜYÜTÜLDÜ)
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
    .p-no-big { 
        background: #333; color: white; padding: 5px 12px; 
        border-radius: 6px; font-size: 20px; font-weight: bold;
        display: inline-block; margin-bottom: 10px;
    }
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
            u_name = st.text_input("Kullanıcı Adı", key="login_user")
            u_pass = st.text_input("Şifre", type="password", key="login_pass")
            if st.button("Sisteme Giriş", use_container_width=True):
                if u_name == "admin" and u_pass == "3363Garanti":
                    st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Yönetici", "admin"
                    st.rerun()
                else:
                    users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                    user_match = users[(users['Kullanici'] == u_name) & (users['Sifre'] == make_hashes(u_pass))]
                    if not user_match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_type = user_match.iloc[0]['Yetki']
                        st.session_state.username = u_name
                        st.rerun()
                    else: st.error("Giriş bilgileri hatalı!")
        with tab2:
            st.info("Yeni personel hesabı.")
            new_u = st.text_input("Kullanıcı Adı", key="register_user")
            new_p = st.text_input("Şifre", type="password", key="register_pass")
            if st.button("Kayıt Ol", use_container_width=True):
                users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                if new_u and new_p:
                    yeni_user = pd.DataFrame([{"Kullanici": new_u, "Sifre": make_hashes(new_p), "Yetki": "Danışman"}])
                    pd.concat([users, yeni_user]).to_csv(USER_FILE, index=False)
                    st.success("Kayıt başarılı!")

# --- ANA PANEL ---
else:
    df_all = verileri_yukle(DB_FILE, ["ID", "P_No", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
    pay_all = verileri_yukle(SHARED_FILE, ["IlanID", "Paylasan", "Paylasilan"])
    gelen_sayi = len(pay_all[pay_all['Paylasilan'] == st.session_state.username])

    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.write(f"👤 **{st.session_state.username} ({st.session_state.user_type})**")
        st.divider()
        
        search_query = st.text_input("🔍 İlan No Ara", placeholder="Örn: 123456", key="main_search")
        
        st.divider()
        menu_items = {
            "📋 Benim Portföyüm": "portfoy",
            f"🔗 Paylaşılanlar ({gelen_sayi})": "paylasilan",
            "➕ Yeni İlan Ekle": "ekle",
            "📅 Randevularım": "randevu"
        }
        if st.session_state.user_type == "Yönetici": menu_items["⚙️ Yönetici Paneli"] = "admin"
        
        secim_key = st.radio("MENÜ", list(menu_items.keys()))
        secim = menu_items[secim_key]
        st.divider()
        if st.button("🚪 Çıkış Yap"):
            st.session_state.logged_in = False
            st.rerun()

    # --- GÜVENLİ ARAMA ---
    if search_query:
        st.title(f"🔎 Sonuçlar: {search_query}")
        kendi_idleri = df_all[df_all['Sahip'] == st.session_state.username]['ID'].tolist()
        paylasilan_idleri = pay_all[pay_all['Paylasilan'] == st.session_state.username]['IlanID'].astype(str).tolist()
        yetkili_idleri = list(set(kendi_idleri + paylasilan_idleri))

        results = df_all[(df_all['ID'].astype(str).isin(yetkili_idleri)) & (df_all['P_No'].astype(str).str.contains(search_query))]

        if not results.empty:
            for _, r in results.iterrows():
                st.markdown(f'<div class="property-card"><div class="p-no-big">NO: {r["P_No"]}</div><br><b>{r["Baslik"]}</b></div>', unsafe_allow_html=True)
                if st.button(f"Detayları Gör #{r['P_No']}", key=f"src_det_{r['ID']}"):
                    st.info(f"📍 Konum: {r['Konum']}\n\n💰 Fiyat: {r['Fiyat']} TL\n\n📝 Açıklama: {r['Aciklama']}")
        else:
            st.warning("Eşleşen ilan bulunamadı.")
        st.divider()

    # 1. BENİM PORTFÖYÜM
    if secim == "portfoy":
        st.title("📂 Benim Portföyüm")
        kendi_df = df_all[df_all['Sahip'] == st.session_state.username]
        
        if kendi_df.empty:
            st.info("Portföyünüzde henüz aktif ilan yok.")
        else:
            for i, r in kendi_df.iloc[::-1].iterrows():
                with st.container():
                    st.markdown(f"""<div class="property-card">
                        <div class="p-no-big">NO: {r['P_No']}</div><br>
                        <b>{r['Baslik']}</b> | <span style="color:green;">{r['Fiyat']} TL</span>
                    </div>""", unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns([1, 1, 2])
                    if c1.button("🗑️ Sil", key=f"d_{r['ID']}"):
                        df_all[df_all['ID'] != r['ID']].to_csv(DB_FILE, index=False)
                        pay_all[pay_all['IlanID'] != r['ID']].to_csv(SHARED_FILE, index=False)
                        st.rerun()
                    
                    if c2.button("🔍 Detay", key=f"det_{r['ID']}"):
                        st.info(f"📍 Konum: {r['Konum']}\n\n📝 Açıklama: {r['Aciklama']}")

                    with c3:
                        with st.expander("🔗 Paylaş"):
                            u_list = verileri_yukle(USER_FILE, ["Kullanici"])['Kullanici'].tolist()
                            digerleri = [u for u in u_list if u != st.session_state.username]
                            target = st.selectbox("Seç:", digerleri, key=f"s_{r['ID']}")
                            if st.button("Gönder", key=f"p_{r['ID']}"):
                                pd.concat([pay_all, pd.DataFrame([{"IlanID": r['ID'], "Paylasan": st.session_state.username, "Paylasilan": target}])]).to_csv(SHARED_FILE, index=False)
                                st.success("Gönderildi!")

    # 2. PAYLAŞILAN İLANLAR
    elif secim == "paylasilan":
        st.title("🔗 Gelen Paylaşımlar")
        my_shares = pay_all[pay_all['Paylasilan'] == st.session_state.username]
        
        if my_shares.empty:
            st.info("Sizinle henüz ilan paylaşılmadı.")
        else:
            for i, p_row in my_shares.iloc[::-1].iterrows():
                r = df_all[df_all['ID'].astype(str) == str(p_row['IlanID'])]
                if not r.empty:
                    r = r.iloc[0]
                    st.markdown(f"""<div class="share-card">
                        <div class="p-no-big">NO: {r['P_No']}</div><br>
                        <b>{r['Baslik']}</b> | 👤 Gönderen: {p_row['Paylasan']}
                    </div>""", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1, 1])
                    if c1.button("❌ Kaldır", key=f"clr_{p_row['IlanID']}_{i}"):
                        pay_all.drop(i).to_csv(SHARED_FILE, index=False)
                        st.rerun()
                    if c2.button("🔍 Detay", key=f"pdet_{r['ID']}"):
                        st.info(f"💰 Fiyat: {r['Fiyat']} TL\n\n📍 Konum: {r['Konum']}\n\n📝 Açıklama: {r['Aciklama']}")

    # 3. YENİ İLAN EKLE
    elif secim == "ekle":
        st.title("➕ İlan Kaydı")
        with st.form("ekle_f"):
            b = st.text_input("İlan Başlığı"); f = st.text_input("Fiyat"); k = st.text_input("Konum"); a = st.text_area("Açıklama")
            if st.form_submit_button("Sisteme Kaydet"):
                yeni = {"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "P_No": portfoy_no_uret(), "Sahip": st.session_state.username, "Tarih": datetime.now().strftime("%d/%m/%Y"), "Baslik": b, "Fiyat": format_para(f), "Konum": k, "Aciklama": a}
                pd.concat([df_all, pd.DataFrame([yeni])]).to_csv(DB_FILE, index=False)
                st.success(f"İlan {yeni['P_No']} no ile eklendi!")

    # 4. RANDEVULAR (FİLTRE EKLENDİ)
    elif secim == "randevu":
        st.title("📅 Randevu Takvimi")
        r_df = verileri_yukle(RANDEVU_FILE, ["Ekleyen", "Tarih", "Saat", "Musteri", "Ilan_No", "Notlar"])
        
        with st.expander("Yeni Randevu Oluştur"):
            # ÖZELLİK: SADECE KENDİ AKTİF İLANLARI ARASINDAN SEÇİM
            kendi_aktif_ilanlarim = df_all[df_all['Sahip'] == st.session_state.username]
            
            if kendi_aktif_ilanlarim.empty:
                st.warning("Randevu oluşturmak için önce portföyünüze ilan eklemelisiniz.")
            else:
                with st.form("r_f"):
                    d = st.date_input("Gün"); s = st.time_input("Saat"); m = st.text_input("Müşteri")
                    ilan_sec = [f"{row['P_No']} - {row['Baslik']}" for _, row in kendi_aktif_ilanlarim.iterrows()]
                    secilen = st.selectbox("İlgili Portföy (Sadece Senin İlanların)", ilan_sec)
                    n = st.text_area("Randevu Notları")
                    
                    if st.form_submit_button("Randevuyu Kaydet"):
                        y_r = pd.DataFrame([{"Ekleyen": st.session_state.username, "Tarih": str(d), "Saat": str(s), "Musteri": m, "Ilan_No": secilen.split(" - ")[0], "Notlar": n}])
                        pd.concat([r_df, y_r]).to_csv(RANDEVU_FILE, index=False)
                        st.success("Randevu kaydedildi!")
                        st.rerun()
        
        display_r = r_df if st.session_state.user_type == "Yönetici" else r_df[r_df['Ekleyen'] == st.session_state.username]
        st.table(display_r)

    # 5. YÖNETİCİ PANELİ
    elif secim == "admin" and st.session_state.user_type == "Yönetici":
        st.title("⚙️ Yönetim Merkezi")
        st.subheader("Personel Kayıtları")
        st.table(verileri_yukle(USER_FILE, ["Kullanici", "Yetki"]))
