import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd

# --- 1. SAYFA KONFİGÜRASYONU (İLK SATIR OLMALI) ---
st.set_page_config(
    page_title="TradeMaster AI Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ÖZEL CSS TASARIMI (ESTETİK İÇİN) ---
st.markdown("""
<style>
    /* Ana arka planı ve metinleri düzenle */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    /* Metrik kutularını kart gibi yap */
    div[data-testid="stMetric"] {
        background-color: #1e2329;
        border: 1px solid #2b3139;
        padding: 15px 0px 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    /* Butonu özelleştir */
    div.stButton > button {
        width: 100%;
        background-color: #2962ff;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #0039cb;
        border-color: #0039cb;
    }
    /* Başlıkları ortala ve stil ver */
    h1 {
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #007CF0, #00DFD8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
    }
    .report-box {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2962ff;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API VE AYARLAR ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ API Anahtarı Bulunamadı.")
    st.stop()

# --- 4. FONKSİYONLAR ---
@st.cache_data(ttl=300)
def get_market_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="6mo")
        if hist.empty: return None, "Veri Yok"

        # Hesaplamalar
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA200'] = hist['Close'].rolling(window=200).mean()
        
        # Son Veriler
        curr = hist.iloc[-1]
        prev = hist.iloc[-2]
        
        # Değişim Oranı
        change_rate = ((curr['Close'] - prev['Close']) / prev['Close']) * 100
        
        trend = "YÜKSELİŞ" if curr['Close'] > curr['SMA200'] else "DÜŞÜŞ"
        
        return {
            "hist": hist,
            "price": curr['Close'],
            "change": change_rate,
            "rsi": curr['RSI'],
            "sma50": curr['SMA50'],
            "sma200": curr['SMA200'],
            "trend": trend,
            "info": ticker.info
        }, None
    except Exception as e:
        return None, str(e)

def get_ai_insight(data):
    prompt = f"""
    Sen kıdemli bir teknik analistsin. Aşağıdaki anonim varlık verilerini (VARLIK X) analiz et.
    
    VERİLER:
    - Fiyat: {data['price']:.2f}
    - RSI: {data['rsi']:.2f}
    - Trend (200G Ort. göre): {data['trend']}
    - 50 Günlük Ort: {data['sma50']:.2f}
    
    GÖREV:
    Bu tabloyu teknik açıdan yorumla.
    
    ÇIKTI FORMATI:
    SİNYAL: [POZİTİF / NEGATİF / NÖTR]
    GÜVEN: [0-100 arası sadece sayı yaz]
    ANALİZ: [Teknik gerekçeni profesyonel bir dille 2-3 cümlede anlat]
    STRATEJİ: [Destek/Direnç seviyelerine atıfta bulunarak tek cümlelik strateji]
    """
    model = genai.GenerativeModel('gemini-3-flash-preview')
    safe = [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
    try:
        response = model.generate_content(prompt, safety_settings=safe)
        return response.text
    except:
        return "SİNYAL: NÖTR\nGÜVEN: 0\nANALİZ: Bağlantı hatası.\nSTRATEJİ: İşlem yapma."

# --- 5. ARAYÜZ YAPISI ---

# Başlık
st.markdown("<h1>TradeMaster <span style='font-size:0.5em'>AI</span></h1>", unsafe_allow_html=True)

# Sidebar (Sol Panel)
with st.sidebar:
    st.markdown("### ⚙️ Kontrol Paneli")
    symbol_input = st.text_input("Hisse Kodu", value="THYAO.IS", help="BIST için sonuna .IS ekleyin")
    analyze_btn = st.button("ANALİZİ BAŞLAT")
    
    st.markdown("---")
    st.info("💡 **İpucu:** Bu sistem 'Hayalet Mod' kullanır. AI, hisse ismini bilmeden sadece matematiğe odaklanır.")
    st.markdown("---")
    st.caption("⚠️ **Yasal Uyarı:** Burada üretilen içerik yatırım tavsiyesi değildir. Eğitim amaçlı simülasyondur.")

# Ana Ekran Mantığı
if analyze_btn:
    with st.spinner('Piyasa verileri işleniyor...'):
        data, error = get_market_data(symbol_input)
    
    if data:
        # --- A. METRİK KARTLARI ---
        col1, col2, col3, col4 = st.columns(4)
        
        # Renk Belirleme (Yeşil/Kırmızı)
        delta_color = "normal" if data['change'] >= 0 else "inverse"
        
        col1.metric("Son Fiyat", f"{data['price']:.2f} ₺", f"%{data['change']:.2f}", delta_color=delta_color)
        col2.metric("RSI (14)", f"{data['rsi']:.2f}", "30-70 Bölgesi")
        col3.metric("Trend", data['trend'], "200 Günlük Ort.")
        col4.metric("Sektör", data['info'].get('sector', 'Genel'), "BIST")
        
        st.markdown("---")

        # --- B. GRAFİK (PRO GÖRÜNÜM) ---
        fig = go.Figure()
        
        # Mum Grafiği
        fig.add_trace(go.Candlestick(
            x=data['hist'].index,
            open=data['hist']['Open'], high=data['hist']['High'],
            low=data['hist']['Low'], close=data['hist']['Close'],
            name='Fiyat',
            increasing_line_color='#00c853', decreasing_line_color='#ff3d00'
        ))
        
        # Ortalamalar
        fig.add_trace(go.Scatter(x=data['hist'].index, y=data['hist']['SMA50'], line=dict(color='#2962ff', width=1.5), name='SMA 50'))
        fig.add_trace(go.Scatter(x=data['hist'].index, y=data['hist']['SMA200'], line=dict(color='#ff9100', width=1.5), name='SMA 200'))
        
        # Grafik Ayarları (Temiz Görünüm)
        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)', # Şeffaf
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- C. AI ANALİZ RAPORU ---
        with st.spinner('Yapay Zeka Sinyal Üretiyor...'):
            ai_text = get_ai_insight(data)
            
            # AI Çıktısını Parçalama (Parsing)
            lines = ai_text.split('\n')
            signal = "NÖTR"
            confidence = 50
            analysis = ""
            
            for line in lines:
                if "SİNYAL:" in line: signal = line.replace("SİNYAL:", "").strip()
                if "GÜVEN:" in line: 
                    try: confidence = int(line.replace("GÜVEN:", "").strip())
                    except: confidence = 50
                if "ANALİZ:" in line: analysis = line.replace("ANALİZ:", "").strip()
                if "STRATEJİ:" in line: strategy = line.replace("STRATEJİ:", "").strip()

            # Rapor Kutusu Tasarımı
            st.markdown("### 🧠 AI Teknik Raporu")
            
            # Sinyal Rengine Göre Kutu
            box_color = "#2962ff" # Mavi (Nötr)
            if "POZİTİF" in signal: box_color = "#00c853" # Yeşil
            if "NEGATİF" in signal: box_color = "#d50000" # Kırmızı
            
            # HTML ile Özel Rapor Alanı
            st.markdown(f"""
            <div style="background-color: #161b22; border-radius: 10px; padding: 20px; border-left: 10px solid {box_color};">
                <h3 style="margin:0; color:{box_color};">{signal}</h3>
                <p style="color: gray; margin-bottom: 10px;">Algoritmik Güven Skoru: %{confidence}</p>
                <div style="background-color: #30363d; height: 10px; border-radius: 5px; width: 100%;">
                    <div style="background-color: {box_color}; height: 100%; border-radius: 5px; width: {confidence}%;"></div>
                </div>
                <br>
                <p style="font-size: 1.1em;"><strong>Analiz:</strong> {analysis}</p>
                <p style="font-size: 1.1em; color: #aaa;"><strong>Strateji:</strong> {strategy}</p>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.error(f"Hata: {error}")
