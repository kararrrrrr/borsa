import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go

# --- AYARLAR ---
st.set_page_config(page_title="Yapay Zeka Borsa Analisti", layout="wide")
st.title("🤖 AI Destekli Borsa Analiz Asistanı")

# Sidebar
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
            return None, None, "Veri bulunamadı. Hisse kodunun sonuna .IS eklediğinizden emin olun (Örn: ASELS.IS)"

        # İndikatör Hesaplamaları
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        # Hareketli Ortalamalar
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA200'] = hist['Close'].rolling(window=200).mean()
        
        # Son veriler
        current_price = hist['Close'].iloc[-1]
        current_rsi = hist['RSI'].iloc[-1]
        sma50 = hist['SMA50'].iloc[-1]
        sma200 = hist['SMA200'].iloc[-1]
        
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
        fk = info.get('trailingPE', 'Veri Yok')
        pb = info.get('priceToBook', 'Veri Yok')
        sector = info.get('sector', 'Belirtilmemiş')
        
        # AI Prompt
        prompt = f"""
        Sen profesyonel bir borsa analistisin. Aşağıdaki verileri analiz et ve yorumla.
        
        HİSSE: {symbol}
        SEKTÖR: {sector}
        FİYAT: {current_price:.2f} TL
        
        TEKNİK GÖSTERGELER:
        - RSI (14): {current_rsi:.2f}
        - 50 Günlük Ortalama: {sma50:.2f}
        - 200 Günlük Ortalama: {sma200:.2f}
        
        TEMEL ORANLAR:
        - F/K: {fk}
        - PD/DD: {pb}
        
        HABER BAŞLIKLARI:
        {news_text}
        
        Lütfen şunları yap:
        1. Teknik analizi yorumla (Alım/Satım bölgesinde mi?).
        2. Temel verileri ve haberleri değerlendir.
        3. Yatırımcı için Kısa ve Orta vadeli net bir özet geç.
        """
        
        # MODEL VE GÜVENLİK AYARLARI (Sorunu çözen kısım burası)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        safe = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        response = model.generate_content(prompt, safety_settings=safe)
        
        # Cevap kontrolü
        if response.text:
            return hist, info, response.text
        else:
            return hist, info, "Yapay zeka boş bir cevap döndürdü."
            
    except Exception as e:
        return None, None, f"Hata detayı: {str(e)}"

# Arayüz
if analyze_button:
    with st.spinner(f'{symbol_input} analiz ediliyor...'):
        hist, info, ai_response = get_analysis(symbol_input)
        
        if hist is not None:
            # Üst Bilgi Kartları
            col1, col2, col3 = st.columns(3)
            col1.metric("Fiyat", f"{hist['Close'].iloc[-1]:.2f} TL")
            col2.metric("RSI", f"{hist['RSI'].iloc[-1]:.2f}")
            col3.metric("Değişim", f"%{((hist['Close'].iloc[-1] - hist['Open'].iloc[-1])/hist['Open'].iloc[-1]*100):.2f}")
            
            # Grafik
            st.subheader("Fiyat Grafiği")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=hist.index,
                            open=hist['Open'], high=hist['High'],
                            low=hist['Low'], close=hist['Close'], name='Fiyat'))
            fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
            
            # AI Yorumu
            st.markdown("### 🧠 Yapay Zeka Yorumu")
            st.info(ai_response)
            
        else:
            st.error(ai_response)
else:
    st.info("Analiz etmek istediğiniz hisse kodunu yanda girip butona basın.")
