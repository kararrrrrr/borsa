import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go
from datetime import datetime

# --- AYARLAR ---
st.set_page_config(page_title="Yapay Zeka Borsa Analisti", layout="wide")
st.title("🤖 AI Destekli Borsa Analiz Asistanı")

# Sidebar (Sol Menü)
st.sidebar.header("Ayarlar")
symbol_input = st.sidebar.text_input("Hisse Kodu Girin (Örn: THYAO.IS, GARAN.IS)", value="THYAO.IS")
analyze_button = st.sidebar.button("Analiz Et")

# API Key Kontrolü
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("Lütfen Streamlit ayarlarından Gemini API Key'inizi ekleyin!")
    st.stop()

def get_analysis(symbol):
    try:
        # Veri Çekme
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")
        
        if hist.empty:
            return None, None, "Veri bulunamadı."

        # Basit Teknik İndikatörler (Manuel Hesaplama)
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        # Hareketli Ortalamalar
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA200'] = hist['Close'].rolling(window=200).mean()
        
        current_price = hist['Close'].iloc[-1]
        current_rsi = hist['RSI'].iloc[-1]
        
        # Haberler
        news_list = ticker.news
        news_text = ""
        if news_list:
            for n in news_list[:3]:
                title = n.get('title', 'Başlık Yok')
                news_text += f"- {title}\n"
        else:
            news_text = "Güncel haber verisi çekilemedi."

        # Temel Bilgiler
        info = ticker.info
        fk = info.get('trailingPE', 'Yok')
        pb = info.get('priceToBook', 'Yok')
        
        # AI Prompt Hazırlama
        prompt = f"""
        Sen uzman bir finansal analistsin. Aşağıdaki {symbol} verilerini yorumla.
        
        VERİLER:
        - Fiyat: {current_price:.2f} TL
        - RSI (14): {current_rsi:.2f} (30 altı ucuz, 70 üstü pahalı kabul edilir)
        - 50 Günlük Ort: {hist['SMA50'].iloc[-1]:.2f}
        - 200 Günlük Ort: {hist['SMA200'].iloc[-1]:.2f}
        - F/K Oranı: {fk}
        - PD/DD Oranı: {pb}
        
        SON HABERLER (İngilizce olabilir, Türkçe yorumla):
        {news_text}
        
        İSTENEN ÇIKTI FORMATI:
        1. **Teknik Görünüm:** (Trend yukarı mı aşağı mı? İndikatörler ne diyor?)
        2. **Temel Durum:** (Fiyat makul mü?)
        3. **Riskler & Fırsatlar:**
        4. **YATIRIMCI ÖZETİ:** (Kısa, Orta ve Uzun vade için net bir cümle)
        """
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        return hist, info, response.text
        
    except Exception as e:
        return None, None, f"Hata oluştu: {str(e)}"

# Ana Ekran
if analyze_button:
    with st.spinner(f'{symbol_input} analiz ediliyor, lütfen bekleyin...'):
        hist, info, ai_response = get_analysis(symbol_input)
        
        if hist is not None:
            # Grafikler
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Fiyat Grafiği")
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=hist.index,
                                open=hist['Open'], high=hist['High'],
                                low=hist['Low'], close=hist['Close'], name='Fiyat'))
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Finansal Özet")
                st.metric("Son Fiyat", f"{hist['Close'].iloc[-1]:.2f} TL")
                st.metric("RSI Değeri", f"{hist['RSI'].iloc[-1]:.2f}")
                st.write(f"**Sektör:** {info.get('sector', '-')}")
            
            st.markdown("---")
            st.subheader("💡 Yapay Zeka Analizi")
            st.markdown(ai_response)
            
        else:
            st.error(ai_response)

else:
    st.info("Analiz için sol menüden hisse kodu girip butona basın.")
