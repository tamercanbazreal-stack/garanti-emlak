import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib

# 1. SAYFA AYARLARI VE DOSYALAR
st.set_page_config(page_title="GARANTİ EMLAK | Yönetim Paneli", page_icon="🏠", layout="wide")
LOGO_URL = "https://i.hizliresim.com/iwyt3qr.png"

DB_FILE = "ilanlar_v3.csv"
USER_FILE = "kullanicilar_v3.csv"
SHARED_FILE = "paylasimlar.csv"
RANDEVU_FILE = "randevular.csv"

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
    .share-box {
        background: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px dashed #ccc;
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
            new_u = st.text_input("Yeni Kullanıcı Adı", key="new_user")
            new_p = st.text_input("Yeni Şifre", type="password", key="new_pass")
            if st.button("Kayıt Ol", use_container_width=True):
                users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                if new_u in users['Kullanici'].values:
                    st.warning("Bu kullanıcı adı sistemde zaten var.")
                elif new_u and new_p:
                    yeni_user = pd.DataFrame([{"Kullanici": new_u, "Sifre": make_hashes(new_p), "Yetki": "Danışman"}])
                    pd.concat([users, yeni_user]).to_csv(USER_FILE, index=False)
                    st.success("Kayıt başarılı! Giriş sekmesine dönebilirsiniz.")

# --- ANA PANEL ---
else:
    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.write(f"Hoş geldin, **{st.session_state.username}**")
        st.write(f"Yetki: {st.session_state.user_type}")
        st.divider()
        menu = ["📋 Portföyüm & Paylaşılanlar", "➕ İlan Ekle", "📅 Randevular"]
        if st.session_state.user_type == "Yönetici": menu.append("⚙️ Yönetici")
        secim = st.radio("MENÜ", menu)
        st.divider()
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # 1. PORTFÖY VE ÖZEL PAYLAŞIM
    if secim == "📋 Portföyüm & Paylaşılanlar":
        st.title("🏡 Gayrimenkul Portföyü")
        
        df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
        paylasimlar = verileri_yukle(SHARED_FILE, ["IlanID", "Paylasan", "Paylasilan"])
        
        # Filtreleme: Kendi ilanları + Başkasının onunla paylaştığı ilanlar
        pay_idleri = paylasimlar[paylasimlar['Paylasilan'] == st.session_state.username]['IlanID'].astype(str).tolist()
        display_df = df[(df['Sahip'] == st.session_state.username) | (df['ID'].astype(str).isin(pay_idleri))]

        if display_df.empty:
            st.info("Henüz görüntülenecek bir ilan yok.")
        else:
            for i, r in display_df.iloc[::-1].iterrows():
                with st.container():
                    # İlan Kartı Tasarımı
                    is_shared = " (Sizinle Paylaşıldı)" if r['Sahip'] != st.session_state.username else ""
                    st.markdown(f"""<div class="property-card">
                        <div style="display:flex; justify-content:space-between;">
                            <b>{r['Baslik']}{is_shared}</b>
                            <b style="color:#8CC63F;">{r['Fiyat']} TL</b>
                        </div>
                        <small>📍 {r['Konum']} | 🗓 {r['Tarih']} | 👤 Sorumlu: {r['Sahip']}</small><br>
                        <p style="margin-top:5px; font-size:14px;">{r['Aciklama']}</p>
                    </div>""", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1, 3])
                    
                    # Sadece ilanın sahibi silebilir
                    if r['Sahip'] == st.session_state.username:
                        if c1.button("🗑️ İlanı Kaldır", key=f"del_{r['ID']}", use_container_width=True):
                            df = df[df['ID'] != r['ID']]
                            df.to_csv(DB_FILE, index=False)
                            # Paylaşımlardan da sil
                            paylasimlar = paylasimlar[paylasimlar['IlanID'].astype(str) != str(r['ID'])]
                            paylasimlar.to_csv(SHARED_FILE, index=False)
                            st.rerun()
                        
                        # PAYLAŞMA ALANI
                        with c2:
                            with st.expander("🔗 Bu İlanı Başka Danışmanla Paylaş"):
                                u_list = verileri_yukle(USER_FILE, ["Kullanici"])['Kullanici'].tolist()
                                if "admin" not in u_list: u_list.append("admin")
                                digerleri = [u for u in u_list if u != st.session_state.username]
                                
                                if digerleri:
                                    hedef_user = st.selectbox("Danışman Seç:", digerleri, key=f"sel_{r['ID']}")
                                    if st.button("Erişim İzni Ver", key=f"btn_{r['ID']}"):
                                        # Zaten paylaşılmış mı kontrol et
                                        var_mi = paylasimlar[(paylasimlar['IlanID'].astype(str) == str(r['ID'])) & (paylasimlar['Paylasilan'] == hedef_user)]
                                        if var_mi.empty:
                                            yeni_p = pd.DataFrame([{"IlanID": r['ID'], "Paylasan": st.session_state.username, "Paylasilan": hedef_user}])
                                            pd.concat([paylasimlar, yeni_p]).to_csv(SHARED_FILE, index=False)
                                            st.success(f"İlan {hedef_user} personeline açıldı!")
                                        else:
                                            st.warning("Bu ilan zaten bu kişiyle paylaşılmış.")
                                else:
                                    st.write("Paylaşılacak başka personel yok.")

    # 2. İLAN EKLE
    elif secim == "➕ İlan Ekle":
        st.title("Yeni Portföy Kaydı")
        with st.form("yeni_ilan_form"):
            b = st.text_input("İlan Başlığı (Örn: Tarsus Satılık 3+1)")
            f = st.text_input("Fiyat")
            k = st.text_input("Konum / Mahalle")
            a = st.text_area("İlan Detayları ve Notlar")
            
            if st.form_submit_button("İlanı Yayınla"):
                if b and f:
                    df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
                    yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
                    yeni_data = {
                        "ID": yeni_id, 
                        "Sahip": st.session_state.username, 
                        "Tarih": datetime.now().strftime("%d/%m/%Y"), 
                        "Baslik": b, 
                        "Fiyat": format_para(f), 
                        "Konum": k, 
                        "Aciklama": a
                    }
                    pd.concat([df, pd.DataFrame([yeni_data])]).to_csv(DB_FILE, index=False)
                    st.success("İlan portföyünüze eklendi!")
                else:
                    st.error("Başlık ve Fiyat alanları boş bırakılamaz.")

    # 3. RANDEVULAR
    elif secim == "📅 Randevular":
        st.title("Randevu ve Görüşme Takvimi")
        r_df = verileri_yukle(RANDEVU_FILE, ["Tarih", "Saat", "Musteri", "Ilan"])
        
        with st.expander("➕ Yeni Randevu Oluştur"):
            with st.form("r_form"):
                c1, c2 = st.columns(2)
                d = c1.date_input("Gün")
                s = c2.time_input("Saat")
                m = st.text_input("Müşteri Adı")
                i = st.text_input("İlgilenilen İlan")
                if st.form_submit_button("Randevuyu Kaydet"):
                    yeni_r = pd.DataFrame([{"Tarih": str(d), "Saat": str(s), "Musteri": m, "Ilan": i}])
                    pd.concat([r_df, yeni_r]).to_csv(RANDEVU_FILE, index=False)
                    st.rerun()
        
        st.subheader("Planlanmış Randevular")
        st.dataframe(r_df, use_container_width=True)

    # 4. YÖNETİCİ PANELİ
    elif secim == "⚙️ Yönetici" and st.session_state.user_type == "Yönetici":
        st.title("Sistem Yönetimi")
        u_df = verileri_yukle(USER_FILE, ["Kullanici", "Yetki"])
        st.subheader("Kayıtlı Tüm Personeller")
        st.table(u_df)
        
        if st.button("⚠️ Tüm İlan Verilerini Sıfırla"):
            pd.DataFrame(columns=["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"]).to_csv(DB_FILE, index=False)
            pd.DataFrame(columns=["IlanID", "Paylasan", "Paylasilan"]).to_csv(SHARED_FILE, index=False)
            st.success("Tüm veritabanı temizlendi.")
