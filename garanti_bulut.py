import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib

# 1. KÜTÜPHANE KONTROLÜ
try:
    from fpdf import FPDF
except ImportError:
    st.error("HATA: 'fpdf2' bulunamadı. Lütfen GitHub'daki dosya adını 'requirements.txt' yapın ve Reboot edin.")

# 2. SAYFA AYARLARI VE DOSYALAR
st.set_page_config(page_title="GARANTİ EMLAK | Yönetim Paneli", page_icon="🏠", layout="wide")
LOGO_URL = "https://i.hizliresim.com/iwyt3qr.png"

DB_FILE = "ilanlar_v3.csv"
USER_FILE = "kullanicilar_v3.csv"
SHARED_FILE = "paylasimlar.csv"
RANDEVU_FILE = "randevular.csv"

# 3. FONKSİYONLAR
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def verileri_yukle(dosya, sutunlar):
    if os.path.exists(dosya):
        return pd.read_csv(dosya)
    return pd.DataFrame(columns=sutunlar)

def format_para(sayi):
    try:
        temiz = ''.join(filter(str.isdigit, str(sayi)))
        return f"{int(temiz):,}".replace(",", ".")
    except: return sayi

# 4. TASARIM
st.markdown("""
    <style>
    .property-card {
        background: white; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px;
        border-left: 5px solid #8CC63F;
    }
    </style>
    """, unsafe_allow_html=True)

# 5. OTURUM YÖNETİMİ
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
            if st.button("Sisteme Giriş", use_container_width=True):
                if u_name == "admin" and u_pass == "3363Garanti":
                    st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Yönetici", "admin"
                    st.rerun()
                else:
                    users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                    if not users[(users['Kullanici'] == u_name) & (users['Sifre'] == make_hashes(u_pass))].empty:
                        st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Danışman", u_name
                        st.rerun()
                    else: st.error("Bilgiler hatalı!")

        with tab2:
            st.info("Yeni personel hesabı buradan oluşturulur.")
            new_u = st.text_input("Yeni Kullanıcı Adı")
            new_p = st.text_input("Yeni Şifre", type="password")
            if st.button("Kayıt Ol"):
                users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                if new_u in users['Kullanici'].values:
                    st.warning("Bu kullanıcı adı alınmış.")
                else:
                    yeni_user = pd.DataFrame([{"Kullanici": new_u, "Sifre": make_hashes(new_p), "Yetki": "Danışman"}])
                    pd.concat([users, yeni_user]).to_csv(USER_FILE, index=False)
                    st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")

# --- ANA PANEL ---
else:
    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.write(f"Hoş geldin, **{st.session_state.username}**")
        st.divider()
        menu = ["📋 Portföy & Paylaşım", "➕ Yeni İlan", "📅 Randevu Takvimi", "📄 Sözleşme Hazırla"]
        if st.session_state.user_type == "Yönetici": menu.append("⚙️ Yönetici Paneli")
        secim = st.radio("MENÜ", menu)
        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    # 1. PORTFÖY VE PAYLAŞIM
    if secim == "📋 Portföy & Paylaşım":
        st.title("🏡 Gayrimenkul Listesi")
        df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
        paylasimlar = verileri_yukle(SHARED_FILE, ["IlanID", "Paylasan", "Paylasilan"])
        
        pay_idleri = paylasimlar[paylasimlar['Paylasilan'] == st.session_state.username]['IlanID'].astype(str).tolist()
        # Kendi ilanları + kendisine paylaşılanlar
        display_df = df[(df['Sahip'] == st.session_state.username) | (df['ID'].astype(str).isin(pay_idleri))]

        for i, r in display_df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f"""<div class="property-card">
                    <b>{r['Baslik']}</b> | <span style="color:green;">{r['Fiyat']} TL</span><br>
                    <small>📍 {r['Konum']} | 👤 Sahibi: {r['Sahip']}</small>
                </div>""", unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 4])
                if c1.button("🗑️ Sil", key=f"d_{r['ID']}"):
                    df = df[df['ID'] != r['ID']]
                    df.to_csv(DB_FILE, index=False)
                    st.rerun()
                
                # Paylaşma Yetkisi (Sadece sahibi paylaşabilir)
                if r['Sahip'] == st.session_state.username:
                    u_list = verileri_yukle(USER_FILE, ["Kullanici"])['Kullanici'].tolist()
                    digerleri = [u for u in u_list if u != st.session_state.username]
                    if digerleri:
                        hedef = c2.selectbox("Personel Seç:", digerleri, key=f"s_{r['ID']}")
                        if c2.button("İlanı Paylaş", key=f"p_{r['ID']}"):
                            yeni_p = pd.DataFrame([{"IlanID": r['ID'], "Paylasan": st.session_state.username, "Paylasilan": hedef}])
                            pd.concat([paylasimlar, yeni_p]).to_csv(SHARED_FILE, index=False)
                            st.success(f"{hedef} ile paylaşıldı!")

        if st.button("📂 Katalog Oluştur (PDF)"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "GARANTI EMLAK PORTFOY", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            for _, row in display_df.iterrows():
                pdf.ln(10)
                pdf.cell(0, 10, f"{row['Baslik']} - {row['Fiyat']} TL", ln=True)
            st.download_button("📥 İndir", pdf.output(dest='S').encode('latin-1', 'ignore'), "katalog.pdf")

    # 2. YENİ İLAN
    elif secim == "➕ Yeni İlan":
        with st.form("ilan_ekle"):
            st.subheader("İlan Detayları")
            b = st.text_input("Başlık")
            f = st.text_input("Fiyat (TL)")
            k = st.text_input("Konum/Adres")
            a = st.text_area("Açıklama")
            if st.form_submit_button("Sisteme Kaydet"):
                df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
                yeni = {"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "Sahip": st.session_state.username, "Tarih": datetime.now().strftime("%d/%m/%Y"), "Baslik": b, "Fiyat": format_para(f), "Konum": k, "Aciklama": a}
                pd.concat([df, pd.DataFrame([yeni])]).to_csv(DB_FILE, index=False)
                st.success("İlan başarıyla eklendi!")

    # 3. RANDEVU TAKVİMİ
    elif secim == "📅 Randevu Takvimi":
        st.title("Müşteri Randevuları")
        r_df = verileri_yukle(RANDEVU_FILE, ["Tarih", "Saat", "Musteri", "Ilan"])
        with st.form("randevu"):
            c1, c2 = st.columns(2)
            d = c1.date_input("Randevu Günü")
            s = c2.time_input("Saat")
            m = st.text_input("Müşteri Ad Soyad")
            i = st.text_input("Hangi İlan İçin?")
            if st.form_submit_button("Randevu Ekle"):
                pd.concat([r_df, pd.DataFrame([{"Tarih": str(d), "Saat": str(s), "Musteri": m, "Ilan": i}])]).to_csv(RANDEVU_FILE, index=False)
                st.rerun()
        st.table(r_df)

    # 4. SÖZLEŞME
    elif secim == "📄 Sözleşme Hazırla":
        st.title("Hızlı Sözleşme Hazırlama")
        tip = st.selectbox("Belge Tipi", ["Yer Gösterme Belgesi", "Kira Kontratı", "Protokol"])
        musteri = st.text_input("Müşteri Bilgisi")
        if st.button("PDF Belgesi Üret"):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"GARANTI EMLAK - {tip}", ln=True, align='C')
            pdf.ln(10); pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, f"Musteri: {musteri}\n\nTarih: {datetime.now().strftime('%d/%m/%Y')}\n\nİşbu belge taraflar arasında emlak hizmeti için düzenlenmiştir.")
            st.download_button("📥 Belgeyi İndir", pdf.output(dest='S').encode('latin-1', 'ignore'), "belge.pdf")

    # 5. YÖNETİCİ
    elif secim == "⚙️ Yönetici Paneli" and st.session_state.user_type == "Yönetici":
        st.title("Sistem Kontrolü")
        u_df = verileri_yukle(USER_FILE, ["Kullanici", "Yetki"])
        st.subheader("Kayıtlı Personeller")
        st.dataframe(u_df)
        if st.button("Veritabanını Temizle (DİKKAT)"):
            st.warning("Bu işlem tüm ilanları siler.")
