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
                    df[col] = True if col == "CanAdd" else ""
            return df
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
    .property-card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; border-left: 5px solid #8CC63F; }
    .p-no-big { background: #333; color: white; padding: 5px 12px; border-radius: 6px; font-size: 20px; font-weight: bold; display: inline-block; margin-bottom: 5px; }
    .loc-text { color: #666; font-size: 14px; margin-bottom: 5px; }
    .detail-box { background: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px dashed #8CC63F; margin-top: 10px; margin-bottom: 15px; }
    .appointment-card { background: #fffcf0; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 4. OTURUM YÖNETİMİ
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'show_detail' not in st.session_state: st.session_state.show_detail = {}

# --- GİRİŞ / KAYIT EKRANI ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.image(LOGO_URL, use_container_width=True)
        tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Üye Ol"])
        
        with tab1:
            u_name = st.text_input("Kullanıcı Adı", key="login_user")
            u_pass = st.text_input("Şifre", type="password", key="login_pass")
            if st.button("Sisteme Giriş", use_container_width=True):
                if u_name == "admin" and u_pass == "3363Garanti":
                    st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, "Yönetici", "admin"
                    st.rerun()
                else:
                    users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki", "CanAdd"])
                    user_match = users[(users['Kullanici'] == u_name) & (users['Sifre'] == make_hashes(u_pass))]
                    if not user_match.empty:
                        st.session_state.logged_in, st.session_state.user_type, st.session_state.username = True, user_match.iloc[0]['Yetki'], u_name
                        st.rerun()
                    else: st.error("Hatalı Giriş Bilgileri!")
        
        with tab2:
            new_user = st.text_input("Yeni Kullanıcı Adı", key="reg_user")
            new_pass = st.text_input("Yeni Şifre", type="password", key="reg_pass")
            confirm_pass = st.text_input("Şifre Tekrar", type="password", key="reg_pass_conf")
            
            if st.button("Kayıt Ol", use_container_width=True):
                users = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki", "CanAdd"])
                if not new_user or not new_pass:
                    st.warning("Lütfen tüm alanları doldurun.")
                elif new_pass != confirm_pass:
                    st.error("Şifreler uyuşmuyor!")
                elif new_user in users['Kullanici'].values or new_user == "admin":
                    st.error("Bu kullanıcı adı zaten alınmış.")
                else:
                    # Yeni üyeler artık varsayılan olarak İlan Ekleme yetkisi AÇIK (True) gelir.
                    new_data = {"Kullanici": new_user, "Sifre": make_hashes(new_pass), "Yetki": "Danışman", "CanAdd": True}
                    pd.concat([users, pd.DataFrame([new_data])]).to_csv(USER_FILE, index=False)
                    st.success("Kayıt Başarılı! Giriş yapabilirsiniz.")

# --- ANA PANEL ---
else:
    df_all = verileri_yukle(DB_FILE, ["ID", "P_No", "Sahip", "Tarih", "Baslik", "Fiyat", "Konum", "Aciklama"])
    pay_all = verileri_yukle(SHARED_FILE, ["IlanID", "Paylasan", "Paylasilan"])
    users_df = verileri_yukle(USER_FILE, ["Kullanici", "Sifre", "Yetki", "CanAdd"])

    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.write(f"👤 **{st.session_state.username} ({st.session_state.user_type})**")
        search_query = st.text_input("🔍 İlan No Ara")
        st.divider()
        
        menu_items = {"📋 Portföyüm": "portfoy", "🔗 Gelenler": "paylasilan"}
        
        # Yetki Kontrolü
        can_user_add = False
        if st.session_state.user_type == "Yönetici":
            can_user_add = True
        else:
            current_user_row = users_df[users_df['Kullanici'] == st.session_state.username]
            if not current_user_row.empty:
                can_user_add = str(current_user_row.iloc[0]['CanAdd']) == "True"

        if can_user_add:
            menu_items["➕ İlan Ekle"] = "ekle"
            
        menu_items["📅 Randevular"] = "randevu"
        if st.session_state.user_type == "Yönetici":
            menu_items["🌐 Şirket Portföyü"] = "all_port"
            menu_items["⚙️ Admin Panel"] = "admin"
            
        secim = menu_items[st.radio("MENÜ", list(menu_items.keys()))]
        if st.button("🚪 Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    # --- İLAN LİSTELEME ---
    def ilan_listele(dataframe, admin_modu=False):
        for i, r in dataframe.iloc[::-1].iterrows():
            st.markdown(f"""<div class="property-card">
                <div class="p-no-big">NO: {r['P_No']}</div><br>
                <b>{r['Baslik']}</b> | <span style="color:green; font-weight:bold;">{r['Fiyat']} TL</span><br>
                <div class="loc-text">📍 {r['Konum']} {f' | 👤 Personel: {r["Sahip"]}' if admin_modu else ''}</div>
            </div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 1, 2])
            detay_key = f"det_{r['ID']}"
            if c1.button("Kapat" if st.session_state.show_detail.get(detay_key) else "🔍 Detay", key=detay_key):
                st.session_state.show_detail[detay_key] = not st.session_state.show_detail.get(detay_key)
                st.rerun()
            if c2.button("🗑️ İlanı Sil", key=f"del_{r['ID']}"):
                df_all[df_all['ID'].astype(str) != str(r['ID'])].to_csv(DB_FILE, index=False)
                st.rerun()
            if not admin_modu:
                with c3:
                    with st.expander("🔗 Paylaş"):
                        target = st.selectbox("Personel:", [u for u in users_df['Kullanici'] if u != st.session_state.username], key=f"sel_{r['ID']}")
                        if st.button("Gönder", key=f"snd_{r['ID']}"):
                            pd.concat([pay_all, pd.DataFrame([{"IlanID": r['ID'], "Paylasan": st.session_state.username, "Paylasilan": target}])]).to_csv(SHARED_FILE, index=False)
                            st.success("Gönderildi!")
            if st.session_state.show_detail.get(detay_key):
                st.markdown(f'<div class="detail-box"><b>📝 NOTLAR:</b><br>{r["Aciklama"]}</div>', unsafe_allow_html=True)

    # --- MENÜ MANTIKLARI ---
    if search_query:
        st.title("🔎 Arama Sonuçları")
        res = df_all[df_all['P_No'].astype(str).str.contains(search_query)]
        ilan_listele(res, admin_modu=(st.session_state.user_type == "Yönetici"))

    elif secim == "portfoy":
        st.title("📂 Benim Portföyüm")
        ilan_listele(df_all[df_all['Sahip'] == st.session_state.username])

    elif secim == "all_port":
        st.title("🌐 Şirket Portföyü")
        ilan_listele(df_all, admin_modu=True)

    elif secim == "ekle":
        st.title("➕ Yeni İlan")
        with st.form("add_form"):
            b = st.text_input("İlan Başlığı *")
            f = st.text_input("Fiyat *")
            k = st.text_input("Konum *")
            a = st.text_area("Notlar *")
            if st.form_submit_button("Portföye Ekle"):
                if not b or not f or not k or not a:
                    st.error("⚠️ Lütfen tüm alanları doldurun.")
                else:
                    yeni = {"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "P_No": portfoy_no_uret(), "Sahip": st.session_state.username, "Tarih": datetime.now().strftime("%d/%m/%Y"), "Baslik": b, "Fiyat": format_para(f), "Konum": k, "Aciklama": a}
                    pd.concat([df_all, pd.DataFrame([yeni])]).to_csv(DB_FILE, index=False)
                    st.success(f"✅ İlan Eklendi! NO: {yeni['P_No']}")

    elif secim == "randevu":
        st.title("📅 Randevu Yönetimi")
        r_df = verileri_yukle(RANDEVU_FILE, ["ID", "Ekleyen", "Tarih", "Saat", "Musteri", "Ilan_No", "Notlar"])
        with st.expander("➕ Yeni Randevu Kaydı"):
            with st.form("r_form", clear_on_submit=True):
                d = st.date_input("Randevu Günü")
                s = st.time_input("Saat")
                m = st.text_input("Müşteri Adı")
                p_secim = st.selectbox("İlgili İlan", [f"{row['P_No']} - {row['Baslik']}" for _, row in df_all.iterrows()])
                n = st.text_area("Randevu Notları")
                if st.form_submit_button("Randevuyu Kaydet"):
                    r_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
                    yeni_r = {"ID": r_id, "Ekleyen": st.session_state.username, "Tarih": str(d), "Saat": str(s), "Musteri": m, "Ilan_No": p_secim.split(" - ")[0], "Notlar": n}
                    pd.concat([r_df, pd.DataFrame([yeni_r])]).to_csv(RANDEVU_FILE, index=False)
                    st.success("Randevu eklendi!")
                    st.rerun()
        st.divider()
        gosterilecek_r = r_df if st.session_state.user_type == "Yönetici" else r_df[r_df['Ekleyen'] == st.session_state.username]
        if gosterilecek_r.empty:
            st.info("Kayıtlı randevu bulunamadı.")
        else:
            for idx, row in gosterilecek_r.iloc[::-1].iterrows():
                st.markdown(f"""<div class="appointment-card"><b>📅 {row['Tarih']} | ⏰ {row['Saat']}</b><br>👤 Müşteri: {row['Musteri']} <br>🏠 İlan No: {row['Ilan_No']} <br>📝 Notlar: {row['Notlar']} <br>{f'✍️ Ekleyen: {row["Ekleyen"]}' if st.session_state.user_type == "Yönetici" else ''}</div>""", unsafe_allow_html=True)
                if st.button("🗑️ Bu Randevuyu Sil", key=f"r_del_{row['ID']}_{idx}"):
                    yeni_r_df = r_df[r_df['ID'].astype(str) != str(row['ID'])]
                    yeni_r_df.to_csv(RANDEVU_FILE, index=False)
                    st.success("Silindi.")
                    st.rerun()

    elif secim == "admin":
        st.title("⚙️ Yönetici Paneli")
        st.subheader("👥 Personel Yönetimi")
        for idx, row in users_df.iterrows():
            if row['Kullanici'] != "admin":
                c1, c2, c3 = st.columns([2, 2, 1])
                c1.write(f"👤 **{row['Kullanici']}**")
                cur_val = str(row['CanAdd']) == "True"
                toggle = c2.toggle("İlan Ekleme Yetkisi", value=cur_val, key=f"tog_{idx}")
                if toggle != cur_val:
                    users_df.at[idx, 'CanAdd'] = toggle
                    users_df.to_csv(USER_FILE, index=False)
                    st.rerun()
                if c3.button("Personeli Sil", key=f"udel_{idx}"):
                    users_df.drop(idx).to_csv(USER_FILE, index=False)
                    st.rerun()

    elif secim == "paylasilan":
        st.title("🔗 Gelen Paylaşımlar")
        shares = pay_all[pay_all['Paylasilan'] == st.session_state.username]
        for i, p in shares.iterrows():
            r = df_all[df_all['ID'].astype(str) == str(p['IlanID'])]
            if not r.empty:
                r = r.iloc[0]
                st.markdown(f'<div class="share-card"><div class="p-no-big">NO: {r["P_No"]}</div><br><b>{r["Baslik"]}</b> | 👤 Gönderen: {p["Paylasan"]}</div>', unsafe_allow_html=True)
                if st.button("❌ Kaldır", key=f"sh_rm_{i}"):
                    pay_all.drop(i).to_csv(SHARED_FILE, index=False)
                    st.rerun()
