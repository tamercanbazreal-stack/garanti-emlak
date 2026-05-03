import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib

# Kütüphane yükleme hatasını önlemek için güvenli import
try:
    from fpdf import FPDF
except ImportError:
    st.error("HATA: 'fpdf2' kütüphanesi bulunamadı. Lütfen requirements.txt dosyasına 'fpdf2' eklediğinizden emin olun.")

# 1. SAYFA AYARLARI
st.set_page_config(page_title="GARANTİ EMLAK | Yönetim Paneli", page_icon="🏠", layout="wide")
LOGO_URL = "https://i.hizliresim.com/iwyt3qr.png"

# Dosya Yolları
DB_FILE = "ilanlar_v3.csv"
USER_FILE = "kullanicilar_v3.csv"
SHARED_FILE = "paylasimlar.csv"
RANDEVU_FILE = "randevular.csv"

# 2. VERİ FONKSİYONLARI
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def verileri_yukle(dosya, sutunlar):
    if os.path.exists(dosya):
        return pd.read_csv(dosya)
    return pd.DataFrame(columns=sutunlar)

def format_para(sayi):
    try:
        temiz_sayi = int(''.join(filter(str.isdigit, str(sayi))))
        return f"{temiz_sayi:,}".replace(",", ".")
    except: return sayi

# 3. TASARIM (CSS)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f1f3f5 !important; }
    .property-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 15px;
        border-left: 5px solid #8CC63F; transition: 0.3s;
    }
    .property-card:hover { transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 4. OTURUM KONTROLÜ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.image(LOGO_URL, use_container_width=True)
        tab1, tab2 = st.tabs(["🔐 Giriş Yap", "📝 Personel Kaydı"])
        with tab1:
            u_name = st.text_input("Kullanıcı Adı")
            u_pass = st.text_input("Şifre", type="password")
            if st.button("Sisteme Giriş", use_container_width=True):
                # Admin Girişi
                if u_name == "admin" and u_pass == "3363Garanti":
                    st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Yönetici", "admin"
                    st.rerun()
                else:
                    users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                    if not users[(users['Kullanici'] == u_name) & (users['Sifre'] == make_hashes(u_pass))].empty:
                        st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Danışman", u_name
                        st.rerun()
                    else: st.error("Hatalı Giriş Bilgileri!")
        with tab2:
            n_user = st.text_input("Yeni Personel Adı")
            n_pass = st.text_input("Şifre Belirle", type="password")
            if st.button("Kaydı Tamamla"):
                users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                if n_user in users['Kullanici'].values: st.warning("Bu isimde bir kayıt zaten mevcut.")
                else:
                    pd.concat([users, pd.DataFrame([{"Kullanici": n_user, "Sifre": make_hashes(n_pass), "Yetki": "Danışman"}])]).to_csv(USER_FILE, index=False)
                    st.success("Kayıt Başarılı! Giriş yapabilirsiniz.")

# --- ANA PANEL ---
else:
    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.write(f"👤 **{st.session_state.username}** ({st.session_state.user_type})")
        st.divider()
        menu_items = ["📋 İlan Portföyü", "➕ Yeni İlan Ekle", "📅 Randevu Takvimi", "📄 Sözleşme Hazırla"]
        if st.session_state.user_type == "Yönetici": menu_items.append("⚙️ Yönetici Paneli")
        secim = st.radio("MENÜ", menu_items)
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # 1. PORTFÖY VE PAYLAŞIM SİSTEMİ
    if secim == "📋 İlan Portföyü":
        st.title("🏡 Gayrimenkul Listesi")
        df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
        paylasimlar = verileri_yukle(SHARED_FILE, ["IlanID", "Paylasan", "Paylasilan"])
        
        # Paylaşılan ilanları kontrol et
        paylasilan_idleri = paylasimlar[paylasimlar['Paylasilan'] == st.session_state.username]['IlanID'].astype(str).tolist()
        display_df = df[(df['Sahip'] == st.session_state.username) | (df['ID'].astype(str).isin(paylasilan_idleri))]
        
        if not display_df.empty:
            for i, r in display_df.iloc[::-1].iterrows():
                is_shared = str(r['ID']) in paylasilan_idleri
                with st.container():
                    st.markdown(f"""<div class="property-card">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-size:12px; color:gray;">{'🔗 Paylaşılan' if is_shared else '🏠 Kendi İlanım'} | {r['Sahip']}</span>
                            <span style="color:#4b8a00; font-weight:bold;">{r['Fiyat']} TL</span>
                        </div>
                        <h4>{r['Baslik']}</h4><p>📍 {r['Konum']}</p><p style="font-size:14px;">{r['Aciklama']}</p>
                    </div>""", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1, 4])
                    if c1.button("🗑️ Sil", key=f"del_{r['ID']}"):
                        df = df[df['ID'] != r['ID']]
                        df.to_csv(DB_FILE, index=False)
                        st.rerun()
                    
                    if not is_shared:
                        u_list = verileri_yukle(USER_FILE, ["Kullanici"])['Kullanici'].tolist()
                        arkadas = c2.selectbox("Bu ilanı şu danışmanla paylaş:", [u for u in u_list if u != st.session_state.username], key=f"sel_{r['ID']}")
                        if c2.button("Yetki Ver", key=f"shr_{r['ID']}"):
                            pd.concat([paylasimlar, pd.DataFrame([{"IlanID": r['ID'], "Paylasan": st.session_state.username, "Paylasilan": arkadas}])]).to_csv(SHARED_FILE, index=False)
                            st.success("İş ortağınızla paylaşıldı!")
            
            # PDF KATALOG OLUŞTURMA
            if st.button("📂 Katalog Oluştur (PDF)"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "GARANTI EMLAK PORTFOY KATALOGU", ln=True, align='C')
                pdf.set_font("Arial", size=11)
                for _, row in display_df.iterrows():
                    pdf.ln(10)
                    pdf.cell(0, 10, f"{row['Baslik']} - {row['Fiyat']} TL", ln=True)
                    pdf.multi_cell(0, 5, f"Konum: {row['Konum']}\nAciklama: {row['Aciklama']}")
                st.download_button("📥 PDF İndir", pdf.output(dest='S').encode('latin-1', 'ignore'), "emlak_katalog.pdf", "application/pdf")
        else: st.info("Henüz portföyünüzde ilan bulunmamaktadır.")

    # 2. YENİ İLAN EKLEME
    elif secim == "➕ Yeni İlan Ekle":
        st.title("Yeni İlan Kaydı")
        with st.form("ilan_form"):
            b, f = st.columns(2); baslik, fiyat = b.text_input("İlan Başlığı"), f.text_input("Fiyat (TL)")
            k, t = st.columns(2); konum, tarih = k.text_input("Mahalle/Konum"), t.date_input("Kayıt Tarihi")
            detay = st.text_area("İlan Detaylı Açıklaması")
            if st.form_submit_button("Sisteme Kaydet"):
                df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
                yeni_id = datetime.now().strftime("%Y%m%d%H%M%S")
                yeni = {"ID": yeni_id, "Sahip": st.session_state.username, "Tarih": tarih.strftime("%d/%m/%Y"), "Baslik": baslik, "Fiyat": format_para(fiyat), "Konum": konum, "Aciklama": detay}
                pd.concat([df, pd.DataFrame([yeni])]).to_csv(DB_FILE, index=False)
                st.success("İlan başarıyla portföye eklendi!"); st.rerun()

    # 3. RANDEVU TAKVİMİ
    elif secim == "📅 Randevu Takvimi":
        st.title("Müşteri Randevu ve Yer Gösterme Takibi")
        r_df = verileri_yukle(RANDEVU_FILE, ["Tarih", "Saat", "Musteri", "Ilan"])
        with st.form("randevu_form"):
            c1, c2 = st.columns(2); d, s = c1.date_input("Randevu Günü"), c2.time_input("Randevu Saati")
            m, i = st.columns(2); mus, ila = m.text_input("Müşteri Ad Soyad"), i.text_input("Gidilecek İlan/Adres")
            if st.form_submit_button("Randevuyu Kaydet"):
                pd.concat([r_df, pd.DataFrame([{"Tarih": str(d), "Saat": str(s), "Musteri": mus, "Ilan": ila}])]).to_csv(RANDEVU_FILE, index=False)
                st.success("Randevu oluşturuldu."); st.rerun()
        st.table(r_df)

    # 4. SÖZLEŞME HAZIRLAYICI (PDF)
    elif secim == "📄 Sözleşme Hazırla":
        st.title("Kurumsal Sözleşme Hazırlama")
        tip = st.selectbox("Form Tipi", ["Yer Gösterme Belgesi", "Kira Kontratı", "Satış Protokolü"])
        isim = st.text_input("Müşteri Ad Soyad")
        if st.button("📄 Sözleşme PDF Hazırla"):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 15)
            pdf.cell(0, 10, f"GARANTI EMLAK - {tip.upper()}", ln=True, align='C')
            pdf.ln(10); pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 10, f"Sayin {isim},\n\nIsbu belge {datetime.now().strftime('%d/%m/%Y')} tarihinde Tarsus subemizde tanzim edilmistir.\n\nIlgili emlak islemi kapsaminda sunulan hizmetlerin detaylari ve taraflarin sorumluluklari asagidaki gibidir...")
            st.download_button("📥 Sözleşmeyi İndir", pdf.output(dest='S').encode('latin-1', 'ignore'), "garanti_sozlesme.pdf")

    # 5. YÖNETİCİ PANELİ (SADECE ADMİN)
    elif secim == "⚙️ Yönetici Paneli" and st.session_state.user_type == "Yönetici":
        st.title("⚙️ Kurumsal Yönetim")
        t1, t2 = st.tabs(["👥 Personel Listesi", "🗑️ Tüm Portföy Yönetimi"])
        with t1:
            u = verileri_yukle(USER_FILE, ["Kullanici", "Yetki"])
            for i, row in u.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"👤 {row['Kullanici']}")
                if c2.button("SİL", key=f"u_{row['Kullanici']}"):
                    u.drop(i).to_csv(USER_FILE, index=False); st.rerun()
        with t2:
            all_i = verileri_yukle(DB_FILE, ["ID", "Baslik", "Sahip"])
            for i, row in all_i.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"🏠 {row['Baslik']} (Sorumlu: {row['Sahip']})")
                if c2.button("İLANLI KALDIR", key=f"i_{row['ID']}"):
                    all_i.drop(i).to_csv(DB_FILE, index=False); st.rerun()
