import streamlit as st
import yfinance as yf
import google.generativeai as genai
import plotly.graph_objects as go

# --- AYARLAR ---
st.set_page_config(page_title="AI Sinyal v3.0", layout="wide")
st.title("🤖 AI Teknik Analiz Sinyal Üretici (Phantom Mod)")

# --- SIDEBAR ---
st.sidebar.header("Ayarlar")
symbol_input = st.sidebar.text_input("Hisse Kodu (Örn: THYAO.IS)", value="THYAO.IS")
analyze_button = st.sidebar.button("Sinyal Üret")

# API KEY
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key Eksik! Streamlit Secrets ayarlarını kontrol et.")
    st.stop()

# --- VERİ ÇEKME VE İŞLEME ---
@st.cache_data(ttl=300)
def get_technical_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Veriyi çek
        hist = ticker.history(period="6mo")
        if hist.empty: return None, "Veri Yok"

        # --- PYTHON İLE HESAPLAMALAR (AI'a bırakmıyoruz) ---
        # 1. RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        # 2. Hareketli Ortalamalar
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA200'] = hist['Close'].rolling(window=200).mean()
        
        # Son Veriler
        current_price = hist['Close'].iloc[-1]
        current_rsi = hist['RSI'].iloc[-1]
        sma50 = hist['SMA50'].iloc[-1]
        sma200 = hist['SMA200'].iloc[-1]
        
        # Trend Tespiti
        trend_durumu = "YÜKSELİŞ" if current_price > sma200 else "DÜŞÜŞ"
        rsi_durumu = "AŞIRI SATIM (UCUZ)" if current_rsi < 30 else ("AŞIRI ALIM (PAHALI)" if current_rsi > 70 else "NÖTR")
        
        return {
            "hist": hist,
            "price": current_price,
            "rsi": current_rsi,
            "sma50": sma50,
            "sma200": sma200,
            "trend": trend_durumu,
            "rsi_status": rsi_durumu
        }, None
        
    except Exception as e:
        return None, str(e)

# --- AI ANALİZ (ANONİM VARLIK YÖNTEMİ) ---
def get_ai_signal(data):
    # BURASI ÇOK ÖNEMLİ: Hisse adını göndermiyoruz. "Varlık X" diyoruz.
    prompt = f"""
    Sen bir matematik ve istatistik uzmanısın.
    Aşağıda ismini gizlediğimiz bir finansal varlığın (VARLIK X) teknik verileri var.
    
    VERİ SETİ:
    - Güncel Fiyat: {data['price']:.2f}
    - RSI (Güç Endeksi): {data['rsi']:.2f}
    - RSI Durumu: {data['rsi_status']}
    - 50 Günlük Ortalama: {data['sma50']:.2f} (Fiyat bunun {'üstünde' if data['price'] > data['sma50'] else 'altında'})
    - 200 Günlük Ortalama: {data['sma200']:.2f} (Fiyat bunun {'üstünde' if data['price'] > data['sma200'] else 'altında'})
    
    GÖREVİN:
    Bu matematiksel tabloyu teknik analiz literatürüne göre yorumla.
    Duygulardan arınmış, tamamen teknik bir çıkarım yap.
    
    ÇIKTI FORMATI (Aynen bu formatı kullan):
    KARAR: [POZİTİF / NEGATİF / NÖTR]
    GÜVEN SKORU: [10 üzerinden bir puan ver]
    NEDEN: [Teknik gerekçeni 2 cümlede açıkla]
    STRATEJİ: [Destek/Direnç mantığına göre kısa bir cümle]
    """
    
    model = genai.GenerativeModel('gemini-3-pro-preview')
    
    # Filtreleri Kapat
    safe = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    try:
        response = model.generate_content(prompt, safety_settings=safe)
        return response.text
    except Exception as e:
        return "AI Bağlantı Hatası."

# --- ARAYÜZ ---
if analyze_button:
    with st.spinner('Piyasa verileri taranıyor...'):
        data, error = get_technical_data(symbol_input)
        
    if data:
        # 1. Grafik Alanı
        st.subheader(f"{symbol_input} Teknik Görünüm")
        
        # Grafik Çizimi
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data['hist'].index,
                        open=data['hist']['Open'], high=data['hist']['High'],
                        low=data['hist']['Low'], close=data['hist']['Close'], name='Fiyat'))
        # Ortalamaları da çizelim ki görsel olsun
        fig.add_trace(go.Scatter(x=data['hist'].index, y=data['hist']['SMA50'], line=dict(color='orange', width=1), name='50 Günlük'))
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # 2. Göstergeler
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fiyat", f"{data['price']:.2f}")
        c2.metric("RSI", f"{data['rsi']:.2f}")
        c3.metric("Trend", data['trend'])
        
        # Renge göre RSI durumu
        rsi_color = "red" if data['rsi'] > 70 else ("green" if data['rsi'] < 30 else "gray")
        c4.markdown(f"**RSI Durumu:** :{rsi_color}[{data['rsi_status']}]")
        
        # 3. AI SİNYAL KUTUSU
        st.markdown("---")
        st.subheader("⚡ AI Sinyal Raporu")
        
        with st.spinner('Algoritma hesaplıyor...'):
            ai_result = get_ai_signal(data)
            
            # Sonucu güzel bir kutu içinde gösterelim
            if "POZİTİF" in ai_result:
                st.success(ai_result)
            elif "NEGATİF" in ai_result:
                st.error(ai_result)
            else:
                st.warning(ai_result)
                
    else:
        st.error(f"Hata: {error}")
