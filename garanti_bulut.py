import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib
from fpdf import FPDF

# 1. SAYFA VE LOGO AYARLARI
st.set_page_config(page_title="GARANTİ EMLAK | Yönetim", page_icon="🏢", layout="wide")
LOGO_URL = "https://i.hizliresim.com/iwyt3qr.png"

# Dosya Yolları
DB_FILE = "ilanlar_v3.csv"
USER_FILE = "kullanicilar_v3.csv"
SHARED_FILE = "paylasimlar.csv"
RANDEVU_FILE = "randevular.csv"

# 2. VERİ TABANI FONKSİYONLARI
def verileri_yukle(dosya, sutunlar):
    if os.path.exists(dosya):
        return pd.read_csv(dosya)
    return pd.DataFrame(columns=sutunlar)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# 3. PDF OLUŞTURUCU (Katalog ve Sözleşme için)
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'GARANTI EMLAK KURUMSAL', 0, 1, 'C')
        self.ln(5)

# 4. GİRİŞ KONTROLÜ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.image(LOGO_URL)
        u_name = st.text_input("Kullanıcı Adı")
        u_pass = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if u_name == "admin" and u_pass == "3363Garanti":
                st.session_state.logged_in = True
                st.session_state.user_type = "Yönetici"
                st.session_state.username = "admin"
                st.rerun()
            else:
                users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                hashed = make_hashes(u_pass)
                if not users[(users['Kullanici'] == u_name) & (users['Sifre'] == hashed)].empty:
                    st.session_state.logged_in = True
                    st.session_state.user_type = "Danışman"
                    st.session_state.username = u_name
                    st.rerun()
                else: st.error("Hatalı Giriş!")

# --- ANA PANEL ---
else:
    with st.sidebar:
        st.image(LOGO_URL)
        st.write(f"👤 **{st.session_state.username}**")
        st.divider()
        menu = st.radio("MENÜ", ["📋 Portföy & Paylaşım", "➕ İlan Ekle", "📅 Randevular", "📄 Sözleşme Hazırla", "⚙️ Yönetici", "🚪 Çıkış"])

    # 1. PORTFÖY VE PAYLAŞIM
    if menu == "📋 Portföy & Paylaşım":
        st.title("🏡 Gayrimenkul Portföyü")
        df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
        paylasimlar = verileri_yukle(SHARED_FILE, ["IlanID", "Paylasan", "Paylasilan"])
        
        # Paylaşılanları Filtrele
        paylasilan_idleri = paylasimlar[paylasimlar['Paylasilan'] == st.session_state.username]['IlanID'].tolist()
        display_df = df[(df['Sahip'] == st.session_state.username) | (df['ID'].isin(paylasilan_idleri))]
        
        if not display_df.empty:
            for i, r in display_df.iterrows():
                is_shared = r['ID'] in paylasilan_idleri
                st.info(f"{'🔗 Paylaşılan' if is_shared else '🏠 Kendi İlanım'} - {r['Baslik']}")
                st.write(f"**Fiyat:** {r['Fiyat']} TL | **Konum:** {r['Konum']}")
                
                if not is_shared:
                    users = verileri_yukle(USER_FILE, ["Kullanici"])
                    arkadaslar = users[users['Kullanici'] != st.session_state.username]['Kullanici'].tolist()
                    secilen = st.selectbox("İlanı Paylaş:", arkadaslar, key=f"s_{r['ID']}")
                    if st.button("Yetki Ver", key=f"b_{r['ID']}"):
                        yeni_p = pd.DataFrame([{"IlanID": r['ID'], "Paylasan": st.session_state.username, "Paylasilan": secilen}])
                        pd.concat([paylasimlar, yeni_p]).to_csv(SHARED_FILE, index=False)
                        st.success("Paylaşıldı!")
            
            if st.button("📂 Katalog Oluştur (PDF)"):
                pdf = PDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for _, row in display_df.iterrows():
                    pdf.cell(0, 10, f"{row['Baslik']} - {row['Fiyat']} TL", ln=True)
                st.download_button("📥 İndir", pdf.output(), "katalog.pdf")
        else: st.warning("İlan bulunamadı.")

    # 2. İLAN EKLE
    elif menu == "➕ İlan Ekle":
        st.title("Yeni İlan Girişi")
        with st.form("yeni_ilan"):
            baslik = st.text_input("Başlık")
            fiyat = st.text_input("Fiyat")
            konum = st.text_input("Konum")
            aciklama = st.text_area("Açıklama")
            if st.form_submit_button("Kaydet"):
                df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
                yeni = {"ID": str(datetime.now().timestamp()), "Sahip": st.session_state.username, 
                        "Tarih": datetime.now().strftime("%d/%m/%Y"), "Baslik": baslik, "Fiyat": fiyat, "Konum": konum, "Aciklama": aciklama}
                pd.concat([df, pd.DataFrame([yeni])]).to_csv(DB_FILE, index=False)
                st.success("İlan eklendi!")

    # 3. RANDEVULAR
    elif menu == "📅 Randevular":
        st.title("Randevu ve Yer Gösterme")
        r_df = verileri_yukle(RANDEVU_FILE, ["Tarih", "Saat", "Musteri", "Not"])
        with st.form("randevu"):
            t = st.date_input("Tarih")
            s = st.time_input("Saat")
            m = st.text_input("Müşteri")
            n = st.text_input("Not")
            if st.form_submit_button("Randevu Yaz"):
                yeni_r = {"Tarih": str(t), "Saat": str(s), "Musteri": m, "Not": n}
                pd.concat([r_df, pd.DataFrame([yeni_r])]).to_csv(RANDEVU_FILE, index=False)
                st.rerun()
        st.table(r_df)

    # 4. SÖZLEŞME HAZIRLA
    elif menu == "📄 Sözleşme Hazırla":
        st.title("Matbu Form Hazırlama")
        tip = st.selectbox("Form:", ["Yer Gösterme", "Kira", "Satış"])
        ad = st.text_input("Müşteri Adı")
        if st.button("PDF Taslağı Oluştur"):
            st.success(f"{ad} adına {tip} formu hazırlandı. (Yazıcıya gönderilebilir)")

    # 5. YÖNETİCİ VE ÇIKIŞ
    elif menu == "⚙️ Yönetici" and st.session_state.user_type == "Yönetici":
        st.title("Admin Paneli")
        st.write("Buradan tüm kullanıcıları ve ilanları silebilirsin.")

    elif menu == "🚪 Çıkış":
        st.session_state.logged_in = False
        st.rerun()
