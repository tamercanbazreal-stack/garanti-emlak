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
CONFIG_FILE = "config.csv"

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
                    df[col] = [portfoy_no_uret() if col == "P_No" else "" for _ in range(len(df))]
            return df
        except:
            return pd.DataFrame(columns=sutunlar)
    return pd.DataFrame(columns=sutunlar)

def format_para(sayi):
    try:
        temiz = ''.join(filter(str.isdigit, str(sayi)))
        return f"{int(temiz):,}".replace(",", ".")
    except: return sayi

# Ayarları yükle (İlan ekleme kısıtlaması için)
def ayar_getir():
    if os.path.exists(CONFIG_FILE):
        return pd.read_csv(CONFIG_FILE).iloc[0]['ilan_ekleme'] == "True"
    return True

# 3. TASARIM
st.markdown("""
    <style>
    .property-card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; border-left: 5px solid #8CC63F; }
    .share-card { background: #f0f7ff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; border-left: 5px solid #007bff; }
    .p-no-big { background: #333; color: white; padding: 5px 12px; border-radius: 6px; font-size: 20px; font-weight: bold; display: inline-block; margin-bottom: 5px; }
    .loc-text { color: #666; font-size: 14px; margin-bottom: 5px; }
    .detail-box { background: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px dashed #8CC63F; margin-top: 10px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 4. OTURUM YÖNETİMİ
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'show_detail' not in st.session_state: st.session_state.show_detail = {}

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.image(LOGO_URL, use_container_width=True)
        u_name = st.text_input("Kullanıcı Adı")
        u_pass = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş", use_container_width=True):
            if u_name == "admin" and u_pass == "3363Garanti":
                st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Yönetici", "admin"
                st.rerun()
            else:
                users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                user_match = users[(users['Kullanici'] == u_name) & (users['Sifre'] == make_hashes(u_pass))]
                if not user_match.empty:
                    st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, user_match.iloc[0]['Yetki'], u_name
                    st.rerun()
                else: st.error("Hatalı Giriş!")

# --- ANA PANEL ---
else:
    df_all = verileri_yukle(DB_FILE, ["ID", "P_No", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
    pay_all = verileri_yukle(SHARED_FILE, ["IlanID", "Paylasan", "Paylasilan"])
    ilan_ekleme_izni = ayar_getir()

    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.write(f"👤 **{st.session_state.username} ({st.session_state.user_type})**")
        search_query = st.text_input("🔍 Portföy No Ara")
        st.divider()
        
        menu_items = {"📋 Portföyüm": "portfoy", f"🔗 Gelenler": "paylasilan"}
        if st.session_state.user_type == "Yönetici" or ilan_ekleme_izni:
            menu_items["➕ İlan Ekle"] = "ekle"
        menu_items["📅 Randevular"] = "randevu"
        if st.session_state.user_type == "Yönetici":
            menu_items["🌐 Tüm Portföy"] = "all_port"
            menu_items["⚙️ Admin Panel"] = "admin"
            
        secim = menu_items[st.radio("MENÜ", list(menu_items.keys()))]
        if st.button("🚪 Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    # PORTFÖY GÖRÜNTÜLEME FONKSİYONU (Ortak kullanım için)
    def ilan_listele(dataframe, admin_modu=False):
        for i, r in dataframe.iloc[::-1].iterrows():
            st.markdown(f"""<div class="property-card">
                <div class="p-no-big">NO: {r['P_No']}</div><br>
                <b>{r['Baslik']}</b> | <span style="color:green; font-weight:bold;">{r['Fiyat']} TL</span><br>
                <div class="loc-text">📍 {r['Konum']} {f' | 👤 Sahibi: {r["Sahip"]}' if admin_modu else ''}</div>
            </div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 1, 2])
            detay_key = f"det_{r['ID']}"
            if c1.button("Kapat" if st.session_state.show_detail.get(detay_key) else "🔍 Detay", key=detay_key):
                st.session_state.show_detail[detay_key] = not st.session_state.show_detail.get(detay_key)
                st.rerun()
            
            if c2.button("🗑️ Sil", key=f"del_{r['ID']}"):
                df_all[df_all['ID'].astype(str) != str(r['ID'])].to_csv(DB_FILE, index=False)
                st.success("İlan Silindi!")
                st.rerun()
            
            if not admin_modu:
                with c3:
                    with st.expander("🔗 Paylaş"):
                        target = st.selectbox("Personel:", [u for u in verileri_yukle(USER_FILE, ["Kullanici"])['Kullanici'] if u != st.session_state.username], key=f"sel_{r['ID']}")
                        if st.button("Gönder", key=f"snd_{r['ID']}"):
                            pd.concat([pay_all, pd.DataFrame([{"IlanID": r['ID'], "Paylasan": st.session_state.username, "Paylasilan": target}])]).to_csv(SHARED_FILE, index=False)
                            st.success("Gönderildi!")

            if st.session_state.show_detail.get(detay_key):
                st.markdown(f'<div class="detail-box"><b>📝 İLAN NOTLARI:</b><br>{r["Aciklama"]}</div>', unsafe_allow_html=True)

    # SEARCH / ARAMA
    if search_query:
        st.title("🔎 Arama Sonuçları")
        res = df_all[df_all['P_No'].astype(str).str.contains(search_query)]
        ilan_listele(res, admin_modu=(st.session_state.user_type == "Yönetici"))

    # MENÜ SEÇİMLERİ
    elif secim == "portfoy":
        st.title("📂 Benim Portföyüm")
        ilan_listele(df_all[df_all['Sahip'] == st.session_state.username])

    elif secim == "all_port":
        st.title("🌐 Tüm Şirket Portföyü")
        ilan_listele(df_all, admin_modu=True)

    elif secim == "paylasilan":
        st.title("🔗 Gelen Paylaşımlar")
        shares = pay_all[pay_all['Paylasilan'] == st.session_state.username]
        for i, p in shares.iterrows():
            r = df_all[df_all['ID'].astype(str) == str(p['IlanID'])]
            if not r.empty:
                r = r.iloc[0]
                st.markdown(f'<div class="share-card"><div class="p-no-big">NO: {r["P_No"]}</div><br><b>{r["Baslik"]}</b> | 👤 Gönderen: {p["Paylasan"]}</div>', unsafe_allow_html=True)
                if st.button("🔍 Detayları Gör", key=f"sh_d_{i}"):
                    st.info(f"Notlar: {r['Aciklama']}")
                if st.button("❌ Listeden Kaldır", key=f"sh_rm_{i}"):
                    pay_all.drop(i).to_csv(SHARED_FILE, index=False)
                    st.rerun()

    elif secim == "ekle":
        st.title("➕ Yeni İlan")
        with st.form("add"):
            b = st.text_input("Başlık"); f = st.text_input("Fiyat"); k = st.text_input("Konum"); a = st.text_area("Notlar")
            if st.form_submit_button("Kaydet"):
                yeni = {"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "P_No": portfoy_no_uret(), "Sahip": st.session_state.username, "Tarih": datetime.now().strftime("%d/%m/%Y"), "Baslik": b, "Fiyat": format_para(f), "Konum": k, "Aciklama": a}
                pd.concat([df_all, pd.DataFrame([yeni])]).to_csv(DB_FILE, index=False)
                st.success("İlan Kaydedildi!")

    elif secim == "randevu":
        st.title("📅 Randevular")
        r_df = verileri_yukle(RANDEVU_FILE, ["Ekleyen", "Tarih", "Saat", "Musteri", "Ilan_No", "Notlar"])
        st.table(r_df[r_df['Ekleyen'] == st.session_state.username] if st.session_state.user_type != "Yönetici" else r_df)

    elif secim == "admin":
        st.title("⚙️ Yönetici Kontrol Paneli")
        
        # 1. İlan Ekleme Kısıtlaması
        st.subheader("🛠️ Sistem Ayarları")
        yeni_izin = st.toggle("Danışmanlar İlan Ekleyebilsin", value=ilan_ekleme_izni)
        if st.button("Ayarları Kaydet"):
            pd.DataFrame([{"ilan_ekleme": str(yeni_izin)}]).to_csv(CONFIG_FILE, index=False)
            st.success("Sistem güncellendi!")
        
        # 2. Personel Yönetimi
        st.subheader("👥 Personel Listesi ve Yönetimi")
        u_df = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
        for idx, row in u_df.iterrows():
            if row['Kullanici'] != "admin":
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 **{row['Kullanici']}** - {row['Yetki']}")
                if col2.button("Üyeyi Sil", key=f"user_del_{idx}"):
                    u_df.drop(idx).to_csv(USER_FILE, index=False)
                    st.rerun()
