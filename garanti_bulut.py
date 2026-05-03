import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib
from fpdf import FPDF

# 1. SAYFA KONFİGÜRASYONU VE LOGO
st.set_page_config(page_title="GARANTİ EMLAK | Tarsus", page_icon="🏠", layout="wide")
LOGO_URL = "https://i.hizliresim.com/iwyt3qr.png"

# Dosya Yolları
DB_FILE = "ilanlar_v3.csv"
USER_FILE = "kullanicilar_v3.csv"
SHARED_FILE = "paylasimlar.csv"
RANDEVU_FILE = "randevular.csv"

# 2. YARDIMCI FONKSİYONLAR
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

# 3. TASARIM (CSS) - ESKİ MENÜ RENGİ VE ANİMASYONLAR
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

# 4. OTURUM YÖNETİMİ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

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
                    st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Yönetici", "admin"
                    st.rerun()
                else:
                    users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                    if not users[(users['Kullanici'] == u_name) & (users['Sifre'] == make_hashes(u_pass))].empty:
                        st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Danışman", u_name
                        st.rerun()
                    else: st.error("Hatalı Giriş!")
        with tab2:
            n_user = st.text_input("Personel Adı")
            n_pass = st.text_input("Şifre", type="password")
            if st.button("Kaydı Tamamla"):
                users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki"])
                if n_user in users['Kullanici'].values: st.warning("Bu kullanıcı zaten var.")
                else:
                    pd.concat([users, pd.DataFrame([{"Kullanici": n_user, "Sifre": make_hashes(n_pass), "Yetki": "Danışman"}])]).to_csv(USER_FILE, index=False)
                    st.success("Kayıt başarılı!")

# --- ANA PANEL ---
else:
    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.write(f"👤 **{st.session_state.username}** ({st.session_state.user_type})")
        st.divider()
        menu_items = ["📋 Portföy & Paylaşım", "➕ Yeni İlan Ekle", "📅 Randevu Takvimi", "📄 Sözleşme Hazırla"]
        if st.session_state.user_type == "Yönetici": menu_items.append("⚙️ Yönetici Paneli")
        secim = st.radio("MENÜ", menu_items)
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # 1. PORTFÖY VE ÖZEL PAYLAŞIM
    if secim == "📋 Portföy & Paylaşım":
        st.title("🏡 Gayrimenkul Portföyü")
        df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
        paylasimlar = verileri_yukle(SHARED_FILE, ["IlanID", "Paylasan", "Paylasilan"])
        
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
                        arkadas = c2.selectbox("Paylaş:", [u for u in u_list if u != st.session_state.username], key=f"sel_{r['ID']}")
                        if c2.button("Yetki Ver", key=f"shr_{r['ID']}"):
                            pd.concat([paylasimlar, pd.DataFrame([{"IlanID": r['ID'], "Paylasan": st.session_state.username, "Paylasilan": arkadas}])]).to_csv(SHARED_FILE, index=False)
                            st.success(f"{arkadas} ile paylaşıldı!")
            
            if st.button("📂 Katalog Oluştur (PDF)"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "GARANTI EMLAK KATALOG", ln=True, align='C')
                pdf.set_font("Arial", size=12)
                for _, row in display_df.iterrows():
                    pdf.ln(10)
                    pdf.cell(0, 10, f"{row['Baslik']} - {row['Fiyat']} TL", ln=True)
                    pdf.multi_cell(0, 5, f"Konum: {row['Konum']}\nAciklama: {row['Aciklama']}")
                st.download_button("📥 İndir", pdf.output(dest='S').encode('latin-1', 'ignore'), "katalog.pdf", "application/pdf")
        else: st.info("Henüz ilan yok.")

    # 2. YENİ İLAN EKLE
    elif secim == "➕ Yeni İlan Ekle":
        st.title("İlan Girişi")
        with st.form("ilan_form"):
            b, f = st.columns(2); baslik, fiyat = b.text_input("Başlık"), f.text_input("Fiyat")
            k, t = st.columns(2); konum, tarih = k.text_input("Konum"), t.date_input("Tarih")
            detay = st.text_area("Detaylı Açıklama")
            if st.form_submit_button("Kaydet"):
                df = verileri_yukle(DB_FILE, ["ID", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
                yeni = {"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "Sahip": st.session_state.username, "Tarih": tarih.strftime("%d/%m/%Y"), "Baslik": baslik, "Fiyat": format_para(fiyat), "Konum": konum, "Aciklama": detay}
                pd.concat([df, pd.DataFrame([yeni])]).to_csv(DB_FILE, index=False)
                st.success("Eklendi!"); st.rerun()

    # 3. RANDEVU TAKVİMİ
    elif secim == "📅 Randevu Takvimi":
        st.title("Yer Gösterme Ajandası")
        r_df = verileri_yukle(RANDEVU_FILE, ["Tarih", "Saat", "Musteri", "Ilan"])
        with st.form("r_form"):
            c1, c2 = st.columns(2); d, s = c1.date_input("Gün"), c2.time_input("Saat")
            m, i = st.columns(2); mus, ila = m.text_input("Müşteri"), i.text_input("İlan/Yer")
            if st.form_submit_button("Randevu Kaydet"):
                pd.concat([r_df, pd.DataFrame([{"Tarih": str(d), "Saat": str(s), "Musteri": mus, "Ilan": ila}])]).to_csv(RANDEVU_FILE, index=False)
                st.rerun()
        st.dataframe(r_df, use_container_width=True)

    # 4. SÖZLEŞME HAZIRLA
    elif secim == "📄 Sözleşme Hazırla":
        st.title("Matbu Form Hazırlama")
        tip = st.selectbox("Form Tipi", ["Yer Gösterme Belgesi", "Kira Kontratı", "Satış Protokolü"])
        isim = st.text_input("Müşteri Ad Soyad")
        if st.button("Taslak PDF Oluştur"):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"GARANTI EMLAK - {tip.upper()}", ln=True, align='C')
            pdf.ln(10); pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, f"Sayin {isim},\n\nBu belge {datetime.now().strftime('%d/%m/%Y')} tarihinde duzenlenmistir.\n\nIlgili gayrimenkul islemi icin tarafimizca sunulan hizmetin detaylari asagidadir...")
            st.download_button("📥 Formu İndir", pdf.output(dest='S').encode('latin-1', 'ignore'), "sozlesme.pdf")

    # 5. YÖNETİCİ PANELİ
    elif secim == "⚙️ Yönetici Paneli" and st.session_state.user_type == "Yönetici":
        st.title("Sistem Yönetimi")
        t1, t2 = st.tabs(["👥 Üyeler", "🗑️ Tüm İlanlar"])
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
                c1.write(f"🏠 {row['Baslik']} ({row['Sahip']})")
                if c2.button("KALDIR", key=f"i_{row['ID']}"):
                    all_i.drop(i).to_csv(DB_FILE, index=False); st.rerun()
