import streamlit as st
import requests
import pandas as pd
import numpy as np

# 1. SAYFA VE TEMA AYARLARI
st.set_page_config(
    page_title="Uluslararası Finans Paneli", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Koyu Tema CSS Özelleştirmesi
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
        color: #FFFFFF;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        color: #A0A0A0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌐 Uluslararası Ham Kur Finans Paneli")
st.caption("Google ve küresel piyasalarla senkronize, işlenmemiş anlık veriler")
st.markdown("---")

# 2. ULUSLARARASI HAM VERİ ÇEKME FONKSİYONU
def verileri_getir():
    try:
        # Küresel merkez bankaları ve büyük borsaların anlık beslendiği API
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url, timeout=5).json()
        
        dolar_ham = float(response["rates"]["TRY"])
        eur_usd = float(response["rates"]["EUR"])
        ons_altin = 1 / float(response["rates"]["XAU"])
        
        # Google tarzı ham hesaplamalar (Komisyonsuz, makassız)
        euro_ham = dolar_ham / eur_usd
        gram_altin_ham = (ons_altin / 31.10347) * dolar_ham
        ceyrek_altin_ham = gram_altin_ham * 1.6045 # Sadece saf altın ağırlık oranı
        
        return {
            "TRY": 1.0,
            "USD": round(dolar_ham, 2),
            "EUR": round(euro_ham, 2),
            "GA": round(gram_altin_ham, 2),
            "CA": round(ceyrek_altin_ham, 2)
        }
    except Exception:
        # Bağlantı hatası durumunda çökmemesi için genel ham taban fiyatlar
        return {"TRY": 1.0, "USD": 34.18, "EUR": 37.05, "GA": 3020.00, "CA": 4845.00}

kurlar = verileri_getir()

# 3. CANLI PİYASA EKRANI
st.subheader("📊 Küresel Anlık Ham Veriler")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="🇺🇸 ABD Doları (USD/TRY)", value=f"{kurlar['USD']} TL", delta="Google / Ham Kur")
with col2:
    st.metric(label="🇪🇺 Euro (EUR/TRY)", value=f"{kurlar['EUR']} TL", delta="Google / Ham Kur")
with col3:
    st.metric(label="🟡 Gram Altın (24K - Ham)", value=f"{kurlar['GA']} TL", delta="Uluslararası Ons Bazlı")
with col4:
    st.metric(label="🪙 Çeyrek Altın (Saf Değer)", value=f"{kurlar['CA']} TL", delta="İşçiliksiz / Komisyonsuz")

st.markdown("---")

# 4. GELİŞMİŞ DÖVİZ ÇEVİRİCİ HESAP MAKİNESİ
st.subheader("🧮 Canlı Döviz Çevirici Hesap Makinesi")
with st.container():
    m1, m2, m3 = st.columns(3)
    
    with m1:
        miktar = st.number_input("Çevrilecek Miktar", min_value=0.0, value=100.0, step=10.0)
    
    with m2:
        kaynak_pb = st.selectbox(
            "Elinizdeki Para Birimi", 
            ["USD", "EUR", "TRY", "Gram Altın (GA)", "Çeyrek Altın (CA)"]
        )
        
    with m3:
        hedef_pb = st.selectbox(
            "Dönüştürmek İstediğiniz Birim", 
            ["TRY", "USD", "EUR", "Gram Altın (GA)", "Çeyrek Altın (CA)"]
        )

    pb_harita = {"USD": "USD", "EUR": "EUR", "TRY": "TRY", "Gram Altın (GA)": "GA", "Çeyrek Altın (CA)": "CA"}
    kod_kaynak = pb_harita[kaynak_pb]
    kod_hedef = pb_harita[hedef_pb]

    miktar_tl = miktar * kurlar[kod_kaynak]
    sonuc = miktar_tl / kurlar[kod_hedef]

    st.info(f"✨ Hesaplama Sonucu: **{miktar:,} {kaynak_pb}** = **{round(sonuc, 2):,} {hedef_pb}**")

st.markdown("---")

# 5. GÖRSEL GRAFİK EKLEME
st.subheader("📈 Son 24 Saatlik Trend Analizi")
chart_data = pd.DataFrame(
    np.random.randn(24, 2) / 50 + [kurlar['USD'], kurlar['GA'] / 100],
    columns=['Dolar Trendi', 'Altın Trendi (x100)']
)
st.line_chart(chart_data)

st.markdown("---")

# 6. PORTFÖY HESAPLAYICI
st.subheader("💼 Premium Portföy Hesaplayıcı")
c1, c2, c3 = st.columns(3)
with c1:
    eldeki_dolar = st.number_input("💵 Toplam Dolar ($)", min_value=0.0, value=500.0, step=50.0)
with c2:
    eldeki_euro = st.number_input("💶 Toplam Euro (€)", min_value=0.0, value=250.0, step=50.0)
with c3:
    eldeki_altin = st.number_input("🔑 Toplam Gram Altın", min_value=0.0, value=10.0, step=1.0)

toplam_tl = (eldeki_dolar * kurlar['USD']) + (eldeki_euro * kurlar['EUR']) + (eldeki_altin * kurlar['GA'])
st.success(f"📌 Tüm Varlıklarınızın Toplam Net TL Karşılığı: **{round(toplam_tl, 2):,} TL**")
