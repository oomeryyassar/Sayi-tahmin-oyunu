
import streamlit as st
import random
import time
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="Sayı Tahmin Oyunu 🎮", page_icon="🎯", layout="centered")

# CSS ile Özel Arka Plan ve Renklendirme
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    h1 {
        color: #ff4b4b;
        text-align: center;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 8px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎮 Sayı Tahmin Dünyası 🎯")
st.write("Bilgisayarın veya arkadaşının tuttuğu sayıyı tahmin edebilecek misin?")

# Oyun Durumunu (Session State) Hazırlama
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.puan = 100
    st.session_state.deneme_sayisi = 0
    st.session_state.skorlar = []

def asal_mi(sayi):
    if sayi < 2: return False
    for i in range(2, int(sayi ** 0.5) + 1):
        if sayi % i == 0: return False
    return True

# Sol Panel: Ayarlar
with st.sidebar:
    st.header("⚙️ Oyun Ayarları")
    zorluk = st.selectbox("Zorluk Seviyesi", ["1: Kolay (1-50)", "2: Orta (1-100)", "3: Zor (1-200)"])
    mod = st.radio("Oyun Modu", ["🖥️ PC'ye Karşı", "👥 Arkadaşına Karşı"])

    if zorluk.startswith("1"):
        hak_limiti, max_sayi, ceza = 10, 50, 5
    elif zorluk.startswith("2"):
        hak_limiti, max_sayi, ceza = 7, 100, 15
    else:
        hak_limiti, max_sayi, ceza = 5, 200, 30

    if st.button("🔄 Oyunu/Sayıyı Yeniden Başlat"):
        st.session_state.game_started = False

# Oyunu Başlat
if not st.session_state.game_started:
    st.session_state.hak = hak_limiti
    st.session_state.puan = 150 if zorluk.startswith("3") else 100 if zorluk.startswith("2") else 50
    st.session_state.deneme_sayisi = 0
    st.session_state.max_sayi = max_sayi
    st.session_state.ceza = ceza
    st.session_state.baslangic_zamani = time.time()

    if mod == "🖥️ PC'ye Karşı":
        st.session_state.gizli_sayi = random.randint(1, max_sayi)
        st.session_state.game_started = True
        st.rerun()

if not st.session_state.game_started and mod == "👥 Arkadaşına Karşı":
    arkadas_sayisi = st.number_input(f"Arkadaşının bulması için bir sayı gizle (1-{max_sayi}):", min_value=1, max_value=max_sayi, step=1, type="password")
    if st.button("Gizli Sayıyı Onayla ve Başlat"):
        st.session_state.gizli_sayi = arkadas_sayisi
        st.session_state.game_started = True
        st.rerun()

# Aktif Oyun Alanı
if st.session_state.game_started:
    st.subheader(f"🎯 1 ile {st.session_state.max_sayi} Arasında Bir Sayı Tutuldu!")

    # İpuçları Alanı
    st.info(f"❤️ Kalan Hak: {st.session_state.hak}  |  🏆 Güncel Puan: {st.session_state.puan}")

    tahmin = st.number_input("Tahmininizi giriniz:", min_value=1, max_value=st.session_state.max_sayi, step=1, key="tahmin_input")

    if st.button("Tahmin Et"):
        gecen_sure = int(time.time() - st.session_state.baslangic_zamani)
        if gecen_sure > 10:
            st.session_state.puan = max(0, st.session_state.puan - 10)
            st.warning(f"⏱️ Biraz yavaş kaldın ({gecen_sure} saniye)! 10 puan ceza uygulandı.")

        st.session_state.hak -= 1
        st.session_state.deneme_sayisi += 1
        st.session_state.baslangic_zamani = time.time()

        mesafe = abs(st.session_state.gizli_sayi - tahmin)

        if tahmin == st.session_state.gizli_sayi:
            st.balloons()
            st.success(f"🎉 Tebrikler! {st.session_state.deneme_sayisi}. denemede doğru bildiniz! Skorunuz: {st.session_state.puan}")

            # Skoru dosyaya yazdır
            tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
            with open("skorlar.txt", "a", encoding="utf-8") as dosya:
                dosya.write(f"[{tarih}] Skor: {st.session_state.puan} (Arayüz Versiyonu)\n")

            st.session_state.game_started = False
        else:
            if mesafe <= 5:
                st.error("🔥 Alev Alev: Gizli sayıya çok yaklaştın!")
            elif mesafe <= 15:
                st.warning("🌤️ Ilık: Yakınlardasın.")
            else:
                st.info("❄️ Buz Gibi: Çok uzaktasın.")

            if tahmin > st.session_state.gizli_sayi:
                st.session_state.puan = max(0, st.session_state.puan - st.session_state.ceza)
                st.write("⬇️ Daha KÜÇÜK bir sayı girmelisin.")
            else:
                st.session_state.puan = max(0, st.session_state.puan - st.session_state.ceza)
                st.write("⬆️ Daha BÜYÜK bir sayı girmelisin.")

            if st.session_state.hak == 0:
                st.error(f"😔 Maalesef hakların bitti! Doğru sayı: {st.session_state.gizli_sayi} idi.")
                st.session_state.game_started = False

# Geçmiş Skorlar Tablosu
st.markdown("--- ")
st.subheader("🏆 Liderlik Tablosu (Skorlar)")
try:
    with open("skorlar.txt", "r", encoding="utf-8") as dosya:
        skorlar_icerik = dosya.read()
        if skorlar_icerik.strip():
            st.text(skorlar_icerik)
        else:
            st.write("Henüz skor kaydı yok.")
except FileNotFoundError:
    st.write("Henüz skor kaydı yok.")
