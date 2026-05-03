import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Sayfa Ayarları (Mobil Uyumlu)
st.set_page_config(page_title="GARANTİ EMLAK | Mobil Panel", layout="centered")

# Veritabanı Bağlantısı
def init_db():
    conn = sqlite3.connect("garanti_bulut.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS portfoy 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, baslik TEXT, tip TEXT, fiyat TEXT, tarih TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- ARAYÜZ ---
st.title("🏠 GARANTİ EMLAK")
st.subheader("Kurumsal Portföy Yönetimi")

menu = ["Portföy Listesi", "Yeni İlan Ekle", "Web Parsel Sorgu"]
choice = st.sidebar.selectbox("Menü", menu)

if choice == "Yeni İlan Ekle":
    st.info("Telefondan ilan bilgilerini girip 'Kaydet'e basman yeterli.")
    with st.form("ilan_form"):
        baslik = st.text_input("İlan Başlığı")
        tip = st.selectbox("Emlak Tipi", ["Daire", "Arsa", "Dükkan", "Villa"])
        fiyat = st.text_input("Fiyat (TL)")
        submit = st.form_submit_button("Sisteme Kaydet")
        
        if submit:
            if baslik and fiyat:
                tarih = datetime.now().strftime("%d-%m-%Y %H:%M")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO portfoy (baslik, tip, fiyat, tarih) VALUES (?,?,?,?)", (baslik, tip, fiyat, tarih))
                conn.commit()
                st.success(f"{baslik} başarıyla eklendi!")
            else:
                st.error("Lütfen başlık ve fiyat gir kanka!")

elif choice == "Portföy Listesi":
    st.write("### Güncel İlanlar")
    df = pd.read_sql_query("SELECT * FROM portfoy ORDER BY id DESC", conn)
    
    if not df.empty:
        # Mobilde şık dursun diye tablo yerine kart şeklinde gösterelim
        for index, row in df.iterrows():
            with st.expander(f"{row['baslik']} - {row['fiyat']} TL"):
                st.write(f"**Tip:** {row['tip']}")
                st.write(f"**Tarih:** {row['tarih']}")
                if st.button(f"Sil (ID: {row['id']})", key=row['id']):
                    cursor = conn.cursor()
                    cursor.execute(f"DELETE FROM portfoy WHERE id={row['id']}")
                    conn.commit()
                    st.rerun()
    else:
        st.warning("Henüz portföyde ilan yok.")

elif choice == "Web Parsel Sorgu":
    st.link_button("TKGM Parsel Sorgu'ya Git", "https://parselsorgu.tkgm.gov.tr/")