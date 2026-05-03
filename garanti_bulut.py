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

# 3. TASARIM (CSS)
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
        display: inline-block; margin-bottom: 5px;
    }
    .loc-text { color: #666; font-size: 14px; margin-bottom: 5px; }
    .detail-box {
        background: #f9f9f9; padding: 15px; border-radius: 8px;
        border: 1px dashed #8CC63F; margin-top: 10px; margin-bottom: 15px;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. OTURUM YÖNETİMİ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'show_detail' not in st.session_state:
    st.session_state.show_detail = {}

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
                    else: st.error("Hatalı Giriş!")
        with tab2:
            new_u = st.text_input("Kullanıcı Adı", key="reg_u")
            new_p = st.text_input("Şifre", type="password", key="reg_p")
            if st.button("Kayıt Ol"):
                users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                pd.concat([users, pd.DataFrame([{"Kullanici": new_u, "Sifre": make_hashes(new_p), "Yetki": "Danışman"}])]).to_csv(USER_FILE, index=False)
                st.success("Kayıt Başarılı!")

# --- ANA PANEL ---
else:
    df_all = verileri_yukle(DB_FILE, ["ID", "P_No", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
    pay_all = verileri_yukle(SHARED_FILE, ["IlanID", "Paylasan", "Paylasilan"])
    gelen_sayi = len(pay_all[pay_all['Paylasilan'] == st.session_state.username])

    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        # Personel adının yanında yetkisi yazıyor
        st.write(f"👤 **{st.session_state.username} ({st.session_state.user_type})**")
        search_query = st.text_input("🔍 İlan No Ara", key="side_search")
        st.divider()
        menu = {"📋 Portföy": "portfoy", f"🔗 Gelenler ({gelen_sayi})": "paylasilan", "➕ Ekle": "ekle", "📅 Randevu": "randevu"}
        if st.session_state.user_type == "Yönetici": menu["⚙️ Admin"] = "admin"
        secim = menu[st.radio("MENÜ", list(menu.keys()))]
        if st.button("🚪 Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    # ARAMA SONUÇLARI
    if search_query:
        st.title("🔎 Arama Sonuçları")
        kendi_idleri = df_all[df_all['Sahip'] == st.session_state.username]['ID'].tolist()
        paylasilan_idleri = pay_all[pay_all['Paylasilan'] == st.session_state.username]['IlanID'].astype(str).tolist()
        results = df_all[(df_all['ID'].astype(str).isin(list(set(kendi_idleri + paylasilan_idleri)))) & (df_all['P_No'].astype(str).str.contains(search_query))]
        
        for _, r in results.iterrows():
            st.markdown(f'<div class="property-card"><div class="p-no-big">NO: {r["P_No"]}</div><br><b>{r["Baslik"]}</b><br><div class="loc-text">📍 {r["Konum"]}</div></div>', unsafe_allow_html=True)
            detay_key = f"src_det_{r['ID']}"
            if st.button("Kapat" if st.session_state.show_detail.get(detay_key) else "🔍 Detay", key=detay_key):
                st.session_state.show_detail[detay_key] = not st.session_state.show_detail.get(detay_key)
                st.rerun()
            if st.session_state.show_detail.get(detay_key):
                st.markdown(f'<div class="detail-box"><b>📝 İLAN NOTLARI:</b><br>{r["Aciklama"]}</div>', unsafe_allow_html=True)

    # 1. BENİM PORTFÖYÜM
    if secim == "portfoy":
        st.title("📂 Benim Portföyüm")
        kendi_df = df_all[df_all['Sahip'] == st.session_state.username]
        for i, r in kendi_df.iloc[::-1].iterrows():
            st.markdown(f"""<div class="property-card">
                <div class="p-no-big">NO: {r['P_No']}</div><br>
                <b>{r['Baslik']}</b> | <span style="color:green; font-weight:bold;">{r['Fiyat']} TL</span><br>
                <div class="loc-text">📍 {r['Konum']}</div>
            </div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 1, 2])
            detay_key = f"my_det_{r['ID']}"
            if c1.button("Kapat" if st.session_state.show_detail.get(detay_key) else "🔍 Detay", key=detay_key):
                st.session_state.show_detail[detay_key] = not st.session_state.show_detail.get(detay_key)
                st.rerun()
            
            if c2.button("🗑️ Sil", key=f"del_{r['ID']}"):
                df_all[df_all['ID'] != r['ID']].to_csv(DB_FILE, index=False)
                st.rerun()
            
            with c3:
                with st.expander("🔗 Paylaş"):
                    target = st.selectbox("Personel Seç:", [u for u in verileri_yukle(USER_FILE, ["Kullanici"])['Kullanici'] if u != st.session_state.username], key=f"sel_{r['ID']}")
                    if st.button("Gönder", key=f"snd_{r['ID']}"):
                        pd.concat([pay_all, pd.DataFrame([{"IlanID": r['ID'], "Paylasan": st.session_state.username, "Paylasilan": target}])]).to_csv(SHARED_FILE, index=False)
                        st.success("Gönderildi!")

            if st.session_state.show_detail.get(detay_key):
                st.markdown(f'<div class="detail-box"><b>📝 İLAN NOTLARI:</b><br>{r["Aciklama"]}</div>', unsafe_allow_html=True)

    # 2. PAYLAŞILANLAR
    elif secim == "paylasilan":
        st.title("🔗 Gelen Paylaşımlar")
        my_shares = pay_all[pay_all['Paylasilan'] == st.session_state.username]
        for i, p_row in my_shares.iloc[::-1].iterrows():
            r = df_all[df_all['ID'].astype(str) == str(p_row['IlanID'])]
            if not r.empty:
                r = r.iloc[0]
                st.markdown(f"""<div class="share-card">
                    <div class="p-no-big">NO: {r['P_No']}</div><br>
                    <b>{r['Baslik']}</b> | <span style="color:green; font-weight:bold;">{r['Fiyat']} TL</span><br>
                    <div class="loc-text">📍 {r['Konum']} | 👤 Gönderen: {p_row['Paylasan']}</div>
                </div>""", unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 1])
                detay_key = f"sh_det_{r['ID']}"
                if c1.button("Kapat" if st.session_state.show_detail.get(detay_key) else "🔍 Detay", key=detay_key):
                    st.session_state.show_detail[detay_key] = not st.session_state.show_detail.get(detay_key)
                    st.rerun()
                
                if c2.button("❌ Kaldır", key=f"rm_{i}"):
                    pay_all.drop(i).to_csv(SHARED_FILE, index=False)
                    st.rerun()
                
                if st.session_state.show_detail.get(detay_key):
                    st.markdown(f'<div class="detail-box"><b>📝 İLAN NOTLARI:</b><br>{r["Aciklama"]}</div>', unsafe_allow_html=True)

    # 3. YENİ İLAN EKLE
    elif secim == "ekle":
        st.title("➕ Yeni İlan Kaydı")
        with st.form("add"):
            b = st.text_input("İlan Başlığı")
            f = st.text_input("Fiyat")
            k = st.text_input("Konum")
            a = st.text_area("İlan Notu / Açıklama")
            if st.form_submit_button("Sisteme Kaydet"):
                yeni = {"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "P_No": portfoy_no_uret(), "Sahip": st.session_state.username, "Tarih": datetime.now().strftime("%d/%m/%Y"), "Baslik": b, "Fiyat": format_para(f), "Konum": k, "Aciklama": a}
                pd.concat([df_all, pd.DataFrame([yeni])]).to_csv(DB_FILE, index=False)
                st.success(f"İlan {yeni['P_No']} numarasıyla kaydedildi!")

    # 4. RANDEVULAR (Sadece Kendi Aktif İlanları)
    elif secim == "randevu":
        st.title("📅 Randevu Takvimi")
        r_df = verileri_yukle(RANDEVU_FILE, ["Ekleyen", "Tarih", "Saat", "Musteri", "Ilan_No", "Notlar"])
        kendi_ilanlarim = df_all[df_all['Sahip'] == st.session_state.username]
        
        with st.expander("➕ Yeni Randevu"):
            if kendi_ilanlarim.empty: st.warning("İlanınız bulunmadığı için randevu alamazsınız.")
            else:
                with st.form("r"):
                    d = st.date_input("Randevu Günü")
                    s = st.time_input("Saat")
                    m = st.text_input("Müşteri Adı")
                    p = st.selectbox("İlgili İlan", [f"{row['P_No']} - {row['Baslik']}" for _, row in kendi_ilanlarim.iterrows()])
                    n = st.text_area("Notlar")
                    if st.form_submit_button("Randevuyu Kaydet"):
                        pd.concat([r_df, pd.DataFrame([{"Ekleyen": st.session_state.username, "Tarih": str(d), "Saat": str(s), "Musteri": m, "Ilan_No": p.split(" - ")[0], "Notlar": n}])]).to_csv(RANDEVU_FILE, index=False)
                        st.success("Randevu başarıyla eklendi!")
                        st.rerun()
        st.table(r_df[r_df['Ekleyen'] == st.session_state.username])

    # 5. ADMIN PANELİ
    elif secim == "admin" and st.session_state.user_type == "Yönetici":
        st.title("⚙️ Admin - Personel Yönetimi")
        st.table(verileri_yukle(USER_FILE, ["Kullanici", "Yetki"]))
