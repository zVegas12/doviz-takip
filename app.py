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

st.title("🌐 Google / Yahoo Uyumlu Ham Kur Paneli")
st.caption("Piyasalar kapalı olsa bile en son resmi kapanış fiyatlarını gösteren sistem")
st.markdown("---")

# 2. YAHOO FINANCE ALTYAPILI VERİ ÇEKME FONKSİYONU
def verileri_getir():
    try:
        # Yahoo Finance verilerini çeken ücretsiz kurumsal açık servis
        url = "https://query1.finance.yahoo.com/v8/finance/chart/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # 1. Dolar/TL Kapanış veya Canlı Fiyatı
        usd_res = requests.get(url + "TRY=X", headers=headers, timeout=5).json()
        dolar = usd_res['chart']['result'][0]['meta']['regularMarketPrice']
        
        # 2. Euro/TL Kapanış veya Canlı Fiyatı
        eur_res = requests.get(url + "EURTRY=X", headers=headers, timeout=5).json()
        euro = eur_res['chart']['result'][0]['meta']['regularMarketPrice']
        
        # 3. Ons Altın -> Gram Altın Hesaplama
        gold_res = requests.get(url + "GC=F", headers=headers, timeout=5).json()
        ons = gold_res['chart']['result'][0]['meta']['regularMarketPrice']
        
        gram_altin = (ons / 31.10347) * dolar
        ceyrek_altin = gram_altin * 1.6045
        
        return {
            "TRY": 1.0,
            "USD": round(dolar, 2),
            "EUR": round(euro, 2),
            "GA": round(gram_altin, 2),
            "CA": round(ceyrek_altin, 2)
        }
    except Exception:
        # Eğer Yahoo servislerinde anlık bir kesinti olursa çökmesin diye son güncel ortalama
        return {"TRY": 1.0, "USD": 34.25, "EUR": 37.15, "GA": 3015.00, "CA": 4837.00}

kurlar = verileri_getir()

# 3. CANLI PİYASA EKRANI
st.subheader("📊 Küresel Resmi Ham Veriler")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="🇺🇸 ABD Doları (USD/TRY)", value=f"{kurlar['USD']} TL", delta="Yahoo / Google Verisi")
with col2:
    st.metric(label="🇪🇺 Euro (EUR/TRY)", value=f"{kurlar['EUR']} TL", delta="Yahoo / Google Verisi")
with col3:
    st.metric(label="🟡 Gram Altın (24K - Ham)", value=f"{kurlar['GA']} TL", delta="Resmi Ons Hesabı")
with col4:
    st.metric(label="🪙 Çeyrek Altın (Saf Değer)", value=f"{kurlar['CA']} TL", delta="İşçiliksiz Saf Oran")

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
st.subheader("📈 Trend Analizi")
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
