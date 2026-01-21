import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import pandas as pd
import numpy as np
# import optuna (Kaldırıldı - Native Grid Search kullanılacak)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. SAYFA AYARLARI & PROFESYONEL CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="TRENDER PRO",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Profesyonel Koyu Tema CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Ana Tema */
    .stApp {
        background: #0a0a0c;
    }
    
    /* Logo & Başlık */
    .brand-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }
    
    .brand-logo {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 3px;
        margin-bottom: 0.25rem;
    }
    
    .brand-logo span {
        color: #00d4aa;
    }
    
    .brand-tagline {
        color: rgba(255,255,255,0.4);
        font-size: 0.75rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* Karar Paneli - Dopamin Tetikleyici */
    .decision-panel {
        background: linear-gradient(180deg, rgba(20,20,25,1) 0%, rgba(15,15,18,1) 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0 2rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .decision-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--signal-color), transparent);
    }
    
    .signal-label {
        text-align: center;
        font-size: 0.7rem;
        color: rgba(255,255,255,0.35);
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 0.5rem;
    }
    
    .signal-value {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 60px var(--signal-color);
    }
    
    .signal-score {
        text-align: center;
        font-size: 1rem;
        color: rgba(255,255,255,0.5);
        margin-bottom: 1.5rem;
    }
    
    .score-bar-container {
        background: rgba(255,255,255,0.05);
        border-radius: 4px;
        height: 6px;
        overflow: hidden;
        margin: 0 auto;
        max-width: 300px;
    }
    
    .score-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Pulse Animasyonu - Dikkat Çekici */
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px var(--signal-color); }
        50% { box-shadow: 0 0 40px var(--signal-color), 0 0 60px var(--signal-color); }
    }
    
    .pulse-active {
        animation: pulse-glow 2s infinite;
    }
    
    /* Metrik Kartları */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 1rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255,255,255,0.4) !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
    }
    
    [data-testid="stMetricDelta"] svg { display: none; }
    
    /* Input */
    .stTextInput > div > div {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: #00d4aa !important;
        box-shadow: 0 0 0 1px #00d4aa !important;
    }
    
    /* Buton */
    .stButton > button {
        background: #00d4aa !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: #00eebb !important;
        transform: translateY(-1px) !important;
    }
    
    /* Bölüm Başlıkları */
    .section-title {
        color: rgba(255,255,255,0.5);
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Divider */
    hr {
        border-color: rgba(255,255,255,0.04) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Status Widget */
    [data-testid="stStatusWidget"] {
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.04) !important;
        border-radius: 12px !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.2);
        font-size: 0.65rem;
        padding: 3rem 0 1rem 0;
        letter-spacing: 1px;
    }
    
    /* Mobil Responsive */
    @media (max-width: 768px) {
        .brand-logo { font-size: 1.5rem; }
        .signal-value { font-size: 2.5rem; }
        .decision-panel { padding: 1.5rem 1rem; }
        [data-testid="stMetricValue"] { font-size: 1rem !important; }
        
        [data-testid="column"] {
            padding: 0.25rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .signal-value { font-size: 2rem; }
        .brand-logo { font-size: 1.25rem; letter-spacing: 2px; }
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 2. API KONTROL
# ═══════════════════════════════════════════════════════════════════════════════
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ API Anahtarı eksik. Lütfen Streamlit Secrets'a GEMINI_API_KEY ekleyin.")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# 3. GELİŞMİŞ TEKNİK ANALİZ MOTORU
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=120)
def get_advanced_data(symbol):
    """Gelişmiş teknik analiz verileri"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")  # 1 yıllık veri
        
        if hist.empty or len(hist) < 50:
            return None
        
        df = hist.copy()
        
        # ─── RSI (14 Periyot) ───
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # ─── Stokastik RSI ───
        rsi = df['RSI']
        stoch_rsi = (rsi - rsi.rolling(14).min()) / (rsi.rolling(14).max() - rsi.rolling(14).min())
        df['StochRSI'] = stoch_rsi * 100
        
        # ─── Hareketli Ortalamalar ───
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # ─── MACD ───
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # ─── Bollinger Bands ───
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle'] * 100
        
        # ─── ATR (Average True Range) ───
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=14).mean()
        df['ATR_Pct'] = (df['ATR'] / df['Close']) * 100
        
        # ─── ADX (Average Directional Index) ───
        plus_dm = df['High'].diff()
        minus_dm = df['Low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr14 = tr.rolling(window=14).sum()
        plus_di = 100 * (plus_dm.rolling(window=14).sum() / tr14)
        minus_di = 100 * (np.abs(minus_dm).rolling(window=14).sum() / tr14)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df['ADX'] = dx.rolling(window=14).mean()
        
        # ─── Hacim Analizi (OBV) ───
        obv = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        df['OBV'] = obv
        df['OBV_SMA20'] = df['OBV'].rolling(window=20).mean()
        df['Volume_SMA20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA20']
        
        # ─── AKILLI PARA GÖSTERGESİ (Chaikin Money Flow - CMF) ───
        mfv = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        mfv = mfv.fillna(0)
        volume_mfv = mfv * df['Volume']
        df['CMF'] = volume_mfv.rolling(20).sum() / df['Volume'].rolling(20).sum()
        
        # ─── TREND FİLTRESİ (EMA Cloud) ───
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # ─── ICHIMOKU BULUTU (Japon Trend Ustası) ───
        # Conversion Line (Tenkan-sen): 9 periyotluk ortalama
        nine_period_high = df['High'].rolling(window=9).max()
        nine_period_low = df['Low'].rolling(window=9).min()
        df['Tenkan'] = (nine_period_high + nine_period_low) / 2

        # Base Line (Kijun-sen): 26 periyotluk ortalama
        period26_high = df['High'].rolling(window=26).max()
        period26_low = df['Low'].rolling(window=26).min()
        df['Kijun'] = (period26_high + period26_low) / 2

        # Leading Span A (Senkou Span A)
        df['SpanA'] = ((df['Tenkan'] + df['Kijun']) / 2).shift(26)

        # Leading Span B (Senkou Span B)
        period52_high = df['High'].rolling(window=52).max()
        period52_low = df['Low'].rolling(window=52).min()
        df['SpanB'] = ((period52_high + period52_low) / 2).shift(26)
        
        # ─── KELTNER KANALLARI (Volatilite Patlaması İçin) ───
        df['Keltner_Mid'] = df['Close'].ewm(span=20).mean()
        df['Keltner_Upper'] = df['Keltner_Mid'] + (2 * df['ATR'])
        df['Keltner_Lower'] = df['Keltner_Mid'] - (2 * df['ATR'])
        
        # ─── RSI UYUMSUZLUK (Divergence) KONTROLÜ ───
        # Son 20 gündeki RSI ve Fiyat tepelerini karşılaştır
        last_20 = df.tail(20)
        price_max_idx = last_20['Close'].idxmax()
        rsi_max_idx = last_20['RSI'].idxmax()
        
        divergence_signal = "YOK"
        # Eğer Fiyat tepesi RSI tepesinden daha yeniyse (Negatif Uyumsuzluk)
        if df.loc[price_max_idx, 'Close'] > df.loc[rsi_max_idx, 'Close']:
            if df.loc[price_max_idx, 'RSI'] < df.loc[rsi_max_idx, 'RSI']:
                divergence_signal = "NEGATİF"
        
        # Pozitif uyumsuzluk kontrolü (Fiyat düşerken RSI yükseliyorsa)
        price_min_idx = last_20['Close'].idxmin()
        rsi_min_idx = last_20['RSI'].idxmin()
        if df.loc[price_min_idx, 'Close'] < df.loc[rsi_min_idx, 'Close']:
            if df.loc[price_min_idx, 'RSI'] > df.loc[rsi_min_idx, 'RSI']:
                divergence_signal = "POZİTİF"

        # ─── Destek ve Direnç Seviyeleri ───
        recent = df.tail(60)
        support = recent['Low'].min()
        resistance = recent['High'].max()
        
        # Pivot Points
        pivot = (recent['High'].iloc[-1] + recent['Low'].iloc[-1] + recent['Close'].iloc[-1]) / 3
        r1 = 2 * pivot - recent['Low'].iloc[-1]
        s1 = 2 * pivot - recent['High'].iloc[-1]
        
        # ─── Son Veri Noktası ───
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Değişim Hesaplama
        change_val = curr['Close'] - prev['Close']
        change_pct = (change_val / prev['Close']) * 100
        
        # Trend Yönü ve Gücü
        trend_direction = "YUKARI" if curr['Close'] > curr['SMA50'] else "AŞAĞI"
        trend_strength = abs(curr['Close'] - curr['SMA50']) / curr['SMA50'] * 100
        
        # MACD Sinyali
        macd_signal = "AL" if curr['MACD'] > curr['MACD_Signal'] else "SAT"
        
        # BB Pozisyonu
        bb_position = (curr['Close'] - curr['BB_Lower']) / (curr['BB_Upper'] - curr['BB_Lower']) * 100
        
        return {
            "df": df,
            "name": ticker.info.get('shortName', symbol),
            "price": curr['Close'],
            "change_val": change_val,
            "change_pct": change_pct,
            # RSI & Stochastic
            "rsi": curr['RSI'],
            "stoch_rsi": curr['StochRSI'],
            # Ortalamalar
            "sma20": curr['SMA20'],
            "sma50": curr['SMA50'],
            "sma200": curr['SMA200'],
            # EMA
            "ema50": curr['EMA50'],
            "ema200": curr['EMA200'],
            # CMF
            "cmf": curr['CMF'],
            # MACD
            "macd": curr['MACD'],
            "macd_signal": curr['MACD_Signal'],
            "macd_hist": curr['MACD_Hist'],
            "macd_status": macd_signal,
            # Bollinger
            "bb_upper": curr['BB_Upper'],
            "bb_lower": curr['BB_Lower'],
            "bb_width": curr['BB_Width'],
            "bb_position": bb_position,
            # Volatilite
            "atr": curr['ATR'],
            "atr_pct": curr['ATR_Pct'],
            "adx": curr['ADX'],
            # Hacim
            "volume": curr['Volume'],
            "volume_avg": curr['Volume_SMA20'],
            "volume_ratio": curr['Volume_Ratio'],
            "obv_trend": "YUKARI" if curr['OBV'] > curr['OBV_SMA20'] else "AŞAĞI",
            # Destek/Direnç
            "support": support,
            "resistance": resistance,
            "pivot": pivot,
            "r1": r1,
            "s1": s1,
            # Trend
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            # Ichimoku
            "tenkan": curr['Tenkan'],
            "kijun": curr['Kijun'],
            "span_a": curr['SpanA'],
            "span_b": curr['SpanB'],
            # Keltner
            "keltner_upper": curr['Keltner_Upper'],
            "keltner_lower": curr['Keltner_Lower'],
            "keltner_mid": curr['Keltner_Mid'],
            # Divergence
            "divergence": divergence_signal,
        }
    except Exception as e:
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 3.5 HAFTALIK VERİ (Multi-Timeframe)
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def get_weekly_trend(symbol):
    """Haftalık zaman diliminde trend analizi"""
    try:
        ticker = yf.Ticker(symbol)
        weekly = ticker.history(period="2y", interval="1wk")
        
        if weekly.empty or len(weekly) < 20:
            return None
        
        # EMA hesaplamaları
        weekly['EMA20'] = weekly['Close'].ewm(span=20, adjust=False).mean()
        weekly['EMA50'] = weekly['Close'].ewm(span=50, adjust=False).mean()
        
        curr = weekly.iloc[-1]
        prev = weekly.iloc[-2]
        
        # Haftalık trend
        weekly_trend = "YUKARI" if curr['Close'] > curr['EMA20'] else "AŞAĞI"
        weekly_ema_cross = "BOĞA" if curr['EMA20'] > curr['EMA50'] else "AYI"
        
        # Haftalık değişim
        weekly_change = ((curr['Close'] - prev['Close']) / prev['Close']) * 100
        
        # Haftalık destek/direnç
        recent_20 = weekly.tail(20)
        weekly_support = recent_20['Low'].min()
        weekly_resistance = recent_20['High'].max()
        
        return {
            "trend": weekly_trend,
            "ema_cross": weekly_ema_cross,
            "change": weekly_change,
            "support": weekly_support,
            "resistance": weekly_resistance,
            "price": curr['Close'],
            "ema20": curr['EMA20'],
            "ema50": curr['EMA50'],
        }
    except:
        return None
# ═══════════════════════════════════════════════════════════════════════════════
# 3.6 PROFESYONEL BACKTEST (MATRIX ALGORİTMASI v4 - BİREBİR ENTEGRASYON)
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def run_robust_backtest(symbol):
    """
    MATRIX BACKTEST MOTORU v3 (Full Synchronization)
    - Ana analizdeki 'calculate_smart_score' mantığıyla birebir aynı çalışır.
    - CMF, Ichimoku, Ağırlıklı Puanlama ve Dinamik Risk Yönetimi içerir.
    - Haftalık trend teyidini simüle eder.
    """
    try:
        # 1. Veri Hazırlığı
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2y")
        
        # Haftalık Veri (Trend Teyidi İçin)
        weekly = ticker.history(period="2y", interval="1wk")
        
        if df.empty or len(df) < 200: return None
        
        # ─── HAFTALIK VERİYİ GÜNLÜĞE EŞLEME ───
        if not weekly.empty and len(weekly) > 20:
            weekly['W_EMA20'] = weekly['Close'].ewm(span=20, adjust=False).mean()
            weekly['W_EMA50'] = weekly['Close'].ewm(span=50, adjust=False).mean()
            # Haftalık sinyalleri günlüğe yayma (reindex)
            weekly_signals = pd.DataFrame(index=df.index)
            weekly_signals['W_Trend'] = weekly['Close'] > weekly['W_EMA20']
            weekly_signals['W_Cross'] = weekly['W_EMA20'] > weekly['W_EMA50']
            weekly_signals = weekly_signals.fillna(method='ffill').fillna(False) # Eksikleri tamamla
        else:
            weekly_signals = pd.DataFrame(index=df.index)
            weekly_signals['W_Trend'] = False
            weekly_signals['W_Cross'] = False

        # ─── İNDİKATÖR HESAPLAMALARI (Ana Analizle Birebir) ───
        # Ortalamalar
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Width'] = (df['BB_Upper'] - (df['BB_Middle'] - (bb_std * 2))) / df['BB_Middle'] * 100
        
        # ATR (Volatilite)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=14).mean()

        # Ichimoku Bulut
        high9 = df['High'].rolling(9).max()
        low9 = df['Low'].rolling(9).min()
        tenkan = (high9 + low9) / 2
        
        high26 = df['High'].rolling(26).max()
        low26 = df['Low'].rolling(26).min()
        kijun = (high26 + low26) / 2
        
        df['SpanA'] = ((tenkan + kijun) / 2).shift(26)
        
        high52 = df['High'].rolling(52).max()
        low52 = df['Low'].rolling(52).min()
        df['SpanB'] = ((high52 + low52) / 2).shift(26)
        
        # ADX
        plus_dm = df['High'].diff()
        minus_dm = df['Low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        tr14 = tr.rolling(14).sum()
        plus_di = 100 * (plus_dm.rolling(14).sum() / tr14)
        minus_di = 100 * (np.abs(minus_dm).rolling(14).sum() / tr14)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df['ADX'] = dx.rolling(14).mean()

        # CMF (Chaikin Money Flow)
        mfv = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        mfv = mfv.fillna(0)
        volume_mfv = mfv * df['Volume']
        df['CMF'] = volume_mfv.rolling(20).sum() / df['Volume'].rolling(20).sum()
        
        # Hacim Oranı
        df['Volume_SMA20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA20']

        # Temizlik
        df = df.dropna()
        
        # 2. Simülasyon Değişkenleri
        initial_capital = 10000
        cash = initial_capital
        position = 0
        commission = 0.002 # BIST Komisyon
        
        in_position = False
        trades_count = 0
        wins = 0
        
        # Numpy Dizileri (Hız için)
        closes = df['Close'].values
        opens = df['Open'].values
        highs = df['High'].values
        lows = df['Low'].values
        volumes = df['Volume'].values
        
        # İndikatör Dizileri
        ema50 = df['EMA50'].values
        ema200 = df['EMA200'].values
        sma50 = df['SMA50'].values
        rsi = df['RSI'].values
        atr = df['ATR'].values
        span_a = df['SpanA'].values
        span_b = df['SpanB'].values
        adx = df['ADX'].values
        cmf = df['CMF'].values
        bb_upper = df['BB_Upper'].values
        bb_width = df['BB_Width'].values
        vol_ratio = df['Volume_Ratio'].values
        
        # Haftalık Sinyal Dizileri
        w_trend = weekly_signals['W_Trend'].reindex(df.index).fillna(False).values
        w_cross = weekly_signals['W_Cross'].reindex(df.index).fillna(False).values
        
        # İşlem Takip Değişkenleri
        trailing_stop_price = 0
        take_profit_price = 0
        entry_price = 0
        
        # KATSAYILAR (Ana Analizle Aynı)
        W_TREND = 2.0
        W_MOMENTUM = 1.5
        W_VOLUME = 1.2
        W_PATTERN = 1.8
        BASE_SCORE = 50
        
        for i in range(20, len(df) - 1): # İlk 20 gün divergence kontrolü için atla
            current_close = closes[i]
            
            # ─── ÇIKIŞ MANTIĞI ───
            if in_position:
                # 1. Take Profit (Dinamik Hedef)
                if highs[i] >= take_profit_price:
                    exit_price = take_profit_price
                    cash += position * exit_price * (1 - commission)
                    wins += 1
                    position = 0
                    in_position = False
                    continue

                # 2. Stop Loss (Trailing)
                if lows[i] < trailing_stop_price:
                    exit_price = trailing_stop_price
                    if opens[i] < trailing_stop_price: exit_price = opens[i] # Gap durumu
                    
                    cash += position * exit_price * (1 - commission)
                    if exit_price > entry_price: wins += 1
                    position = 0
                    in_position = False
                    continue
                
                # 3. İz Süren Stop Güncelleme
                # Eğer ADX güçlüyse stopu daha agresif takip ettir
                stop_mult = 2.5 if adx[i] > 30 else 3.0
                new_stop = current_close - (stop_mult * atr[i])
                if new_stop > trailing_stop_price:
                    trailing_stop_price = new_stop

            # ─── GİRİŞ MANTIĞI (MATRIX v4 SKORLAMA) ───
            if not in_position:
                # SKORLAMA BAŞLANGIÇ
                trend_score = 0
                mom_score = 0
                vol_score = 0
                pat_score = 0
                
                # 1. TIER: TREND (Ichimoku & EMA)
                cloud_top = max(span_a[i], span_b[i])
                cloud_bottom = min(span_a[i], span_b[i])
                
                if current_close > cloud_top: trend_score += 15
                elif current_close < cloud_bottom: trend_score -= 15
                
                if ema50[i] > ema200[i]:
                    if current_close > ema50[i]: trend_score += 10
                    elif current_close < ema50[i]: trend_score += 5
                else:
                    trend_score -= 10
                    
                # Haftalık Teyit
                if w_cross[i]: trend_score += 10
                else: trend_score -= 10

                # 2. TIER: MOMENTUM
                if rsi[i] > 50 and current_close > cloud_top: mom_score += 5
                elif rsi[i] < 50 and current_close < cloud_bottom: mom_score -= 5
                
                # Pullback Fırsatı (En Değerli Sinyal)
                if current_close > sma50[i] and rsi[i] < 45: mom_score += 25
                
                # Uyumsuzluk Kontrolü (Basitleştirilmiş: Son 20 gündeki fiyat/rsi tepeleri)
                # Döngü içinde her adımda geriye dönük bakmak yavaşlatabilir ama doğruluk için gerekli
                prev_price_max = np.max(closes[i-20:i])
                prev_rsi_max = np.max(rsi[i-20:i])
                if current_close > prev_price_max and rsi[i] < prev_rsi_max: # Negatif Uyumsuzluk
                    mom_score -= 25
                
                # Aşırı Alım Filtresi
                if current_close > bb_upper[i] and rsi[i] > 75: mom_score -= 20

                # 3. TIER: HACİM
                if cmf[i] > 0.10: vol_score += 15
                elif cmf[i] < -0.10: vol_score -= 15
                
                if vol_ratio[i] > 2.0 and (closes[i] > closes[i-1]): vol_score += 10
                
                # 4. TIER: FORMASYON
                if bb_width[i] < 8: pat_score += 5
                if bb_width[i] < 10 and trend_score > 0 and vol_score > 0: pat_score += 20
                
                # FİNAL SKOR HESAPLAMA
                final_raw_score = (trend_score * W_TREND) + \
                                  (mom_score * W_MOMENTUM) + \
                                  (vol_score * W_VOLUME) + \
                                  (pat_score * W_PATTERN)
                
                normalized_score = BASE_SCORE + max(-50, min(50, final_raw_score))
                
                # İŞLEME GİRİŞ KARARI (Eşik: 60)
                if normalized_score >= 60:
                    entry_price = opens[i+1]
                    size = cash / entry_price
                    cost = size * entry_price * (1 + commission)
                    cash -= cost
                    position = size
                    in_position = True
                    trades_count += 1
                    
                    # Risk Yönetimi (Ana analizdeki risk_levels ile uyumlu)
                    # ADX yüksekse volatilite bazlı, düşükse daha geniş stop
                    stop_mult = 2.5 if adx[i] > 30 else 2.0
                    
                    trailing_stop_price = entry_price - (stop_mult * atr[i])
                    take_profit_price = entry_price + (stop_mult * 3.0 * atr[i]) # Hedef 2 seviyesi
                
        final_value = cash + (position * closes[-1] if in_position else 0)
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        win_rate = (wins / trades_count * 100) if trades_count > 0 else 0

        return {
            "total_pnl": total_return,
            "total_trades": trades_count,
            "win_rate": win_rate,
            "final_equity": final_value
        }
    except Exception as e:
        return {"error": str(e)}

def optimize_strategy_robust(symbol):
    """
    GRID SEARCH OPTİMİZASYONU
    Her hisse için en iyi RSI, ATR ve giriş eşiği kombinasyonunu bulur.
    """
    best_result = None
    best_pnl = -999
    
    # Parametre Aralıkları
    rsi_periods = [10, 14, 21]
    atr_mults = [2.5, 3.0, 3.5]
    entry_thresholds = [50, 60, 70]
    
    for rsi_p in rsi_periods:
        for atr_m in atr_mults:
            for entry_t in entry_thresholds:
                result = run_parametric_backtest(
                    symbol, 
                    rsi_period=rsi_p, 
                    atr_mult=atr_m, 
                    entry_threshold=entry_t
                )
                
                if result and "total_pnl" in result:
                    # Risk-adjusted skor
                    adjusted_score = result["total_pnl"] + (result.get("win_rate", 0) * 0.1)
                    
                    if adjusted_score > best_pnl:
                        best_pnl = adjusted_score
                        best_result = {
                            'rsi_period': rsi_p,
                            'atr_mult': atr_m,
                            'entry_threshold': entry_t,
                            'best_pnl': result["total_pnl"],
                            'best_win_rate': result.get("win_rate", 0)
                        }
    
    return best_result if best_result else {'rsi_period': 14, 'atr_mult': 3.0, 'entry_threshold': 60}

def run_parametric_backtest(symbol, rsi_period=14, atr_mult=3.0, entry_threshold=60):
    """
    PARAMETRİK BACKTEST - Grid Search için kullanılır
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2y")
        if df.empty or len(df) < 200: return None
        
        # İndikatörler
        df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        
        # RSI (Parametrik)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # ATR
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=14).mean()
        
        # Ichimoku
        df['Tenkan'] = (df['High'].rolling(9).max() + df['Low'].rolling(9).min()) / 2
        df['Kijun'] = (df['High'].rolling(26).max() + df['Low'].rolling(26).min()) / 2
        df['SpanA'] = ((df['Tenkan'] + df['Kijun']) / 2).shift(26)
        df['SpanB'] = ((df['High'].rolling(52).max() + df['Low'].rolling(52).min()) / 2).shift(26)
        
        # ADX
        plus_dm = df['High'].diff()
        minus_dm = df['Low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        tr14 = tr.rolling(14).sum()
        plus_di = 100 * (plus_dm.rolling(14).sum() / tr14)
        minus_di = 100 * (np.abs(minus_dm).rolling(14).sum() / tr14)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df['ADX'] = dx.rolling(14).mean()
        
        # CMF
        mfv = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        df['CMF'] = (mfv.fillna(0) * df['Volume']).rolling(20).sum() / df['Volume'].rolling(20).sum()
        
        df = df.dropna()
        
        # Simülasyon
        cash = 10000
        position = 0
        commission = 0.001
        in_position = False
        trades = 0
        wins = 0
        entry_price = 0
        trailing_stop = 0
        
        closes = df['Close'].values
        opens = df['Open'].values
        lows = df['Low'].values
        ema200 = df['EMA200'].values
        ema50 = df['EMA50'].values
        sma50 = df['SMA50'].values
        rsi = df['RSI'].values
        atr = df['ATR'].values
        span_a = df['SpanA'].values
        span_b = df['SpanB'].values
        adx = df['ADX'].values
        cmf = df['CMF'].values
        
        for i in range(len(df) - 1):
            c = closes[i]
            
            if in_position:
                if lows[i] < trailing_stop:
                    exit_p = trailing_stop if opens[i] >= trailing_stop else opens[i]
                    cash += position * exit_p * (1 - commission)
                    if exit_p > entry_price: wins += 1
                    position = 0
                    in_position = False
                    continue
                
                new_stop = c - (atr_mult * atr[i])
                if new_stop > trailing_stop: trailing_stop = new_stop
                
                if c < ema200[i] * 0.95:
                    cash += position * c * (1 - commission)
                    if c > entry_price: wins += 1
                    position = 0
                    in_position = False
                    continue
            
            if not in_position:
                score = 0
                cloud_top = max(span_a[i], span_b[i]) if span_a[i] > 0 else 0
                
                # calculate_smart_score ile SENKRON
                if c > cloud_top > 0: score += 15
                if ema50[i] > ema200[i] and c > ema50[i]: score += 10
                elif ema50[i] > ema200[i]: score += 5
                if c > sma50[i] and rsi[i] < 40: score += 25
                if cmf[i] > 0.10: score += 15
                if adx[i] > 25: score += 10
                elif adx[i] > 20: score += 5
                
                if score >= entry_threshold:
                    entry_price = opens[i+1]
                    position = cash / entry_price
                    cash -= position * entry_price * (1 + commission)
                    in_position = True
                    trades += 1
                    trailing_stop = entry_price - (atr_mult * atr[i])
        
        final = cash + (position * closes[-1] if in_position else 0)
        pnl = ((final - 10000) / 10000) * 100
        wr = (wins / trades * 100) if trades > 0 else 0
        
        return {"total_pnl": pnl, "total_trades": trades, "win_rate": wr, "final_equity": final}
    except:
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 4. SİNYAL SKOR HESAPLAMA
# ═══════════════════════════════════════════════════════════════════════════════
def calculate_smart_score(data, weekly_data=None):
    """
    MATRIX ALGORİTMASI v4:
    - Lineer toplama yerine Ağırlıklı Çarpan (Weighted Multiplier) sistemi.
    - Uyumsuzluk (Divergence) taraması.
    - Ichimoku Bulut sistemi entegrasyonu.
    """
    base_score = 50
    score = 0
    reasons = []
    
    # KATSAYILAR (Önem derecesine göre ağırlıklar)
    W_TREND = 2.0      # Trend her şeydir
    W_MOMENTUM = 1.5   # Dönüş sinyalleri
    W_VOLUME = 1.2     # Teyit mekanizması
    W_PATTERN = 1.8    # Ichimoku ve formasyonlar

    # 1. TIER: TREND ANALİZİ (Ichimoku & EMA)
    trend_score = 0
    
    # Fiyat Bulutun Neresinde? (En güçlü trend filtresi)
    span_a = data.get('span_a', 0)
    span_b = data.get('span_b', 0)
    
    # NaN kontrolü yap
    if span_a is None or (isinstance(span_a, float) and np.isnan(span_a)):
        span_a = 0
    if span_b is None or (isinstance(span_b, float) and np.isnan(span_b)):
        span_b = 0
    
    is_above_cloud = data['price'] > max(span_a, span_b) if (span_a > 0 and span_b > 0) else False
    is_below_cloud = data['price'] < min(span_a, span_b) if (span_a > 0 and span_b > 0) else False
    
    if is_above_cloud:
        trend_score += 15
        reasons.append("Fiyat Bulut Üstünde (Güçlü Trend)")
    elif is_below_cloud:
        trend_score -= 15
        reasons.append("Fiyat Bulut Altında (Düşüş Trendi)")
    
    # EMA Sıralaması (Kusursuz Boğa Dizilimi)
    if data['ema50'] > data['ema200']:
        if data['price'] > data['ema50']:
            trend_score += 10
            reasons.append("Golden Cross Bölgesi")
        elif data['price'] < data['ema50']:
             # Trend var ama düzeltme yapıyor
             trend_score += 5 
    else:
        trend_score -= 10

    # Haftalık Teyit
    if weekly_data:
        if weekly_data['ema_cross'] == "BOĞA":
            trend_score += 10
        else:
            trend_score -= 10

    # 2. TIER: MOMENTUM & UYUMSUZLUK (Divergence)
    mom_score = 0
    
    # RSI Trend Uyumu
    if data['rsi'] > 50 and is_above_cloud:
        mom_score += 5
    elif data['rsi'] < 50 and is_below_cloud:
        mom_score -= 5
    
    # Divergence Kontrolü
    divergence = data.get('divergence', 'YOK')
    if divergence == "NEGATİF":
        mom_score -= 25
        reasons.append("Negatif Uyumsuzluk (Dikkat!)")
    elif divergence == "POZİTİF":
        mom_score += 25
        reasons.append("Pozitif Uyumsuzluk (Fırsat!)")
        
    # Trend İçi Pullback (En Değerli Sinyal)
    if data['price'] > data['sma50'] and data['rsi'] < 40:
        mom_score += 25
        reasons.append("Trend İçi Ucuzluk (Pullback Fırsatı)")
    
    if data['price'] > data['bb_upper'] and data['rsi'] > 75:
        mom_score -= 20
        reasons.append("Aşırı Alım + Bollinger Dışı")

    # 3. TIER: HACİM & PARA AKIŞI
    vol_score = 0
    if data['cmf'] > 0.10:
        vol_score += 15
        reasons.append("Balina Girişi (CMF > 0.10)")
    elif data['cmf'] < -0.10:
        vol_score -= 15
        
    if data['volume_ratio'] > 2.0 and data['change_pct'] > 0:
        vol_score += 10
        reasons.append("Hacim Patlaması (x2)")

    # 4. TIER: VOLATİLİTE SIKIŞMASI (Squeeze)
    pat_score = 0
    if data['bb_width'] < 8:
        pat_score += 5
        reasons.append("Sıkışma (Enerji Birikiyor)")
        
        # Sıkışma varken trend ve hacim varsa puanı katla
        if trend_score > 0 and vol_score > 0:
            pat_score += 20
            reasons.append("Sıkışma Yukarı Kırılıyor!")

    # ─── TOPLAM SKOR HESAPLAMA (Ağırlıklı) ───
    final_raw_score = (trend_score * W_TREND) + \
                      (mom_score * W_MOMENTUM) + \
                      (vol_score * W_VOLUME) + \
                      (pat_score * W_PATTERN)
                      
    # Normalizasyon (50 taban puana ekle)
    # Skor çok uçuk çıkabilir, -50 ile +50 arasına sıkıştıracağız
    normalized_score = base_score + max(-50, min(50, final_raw_score))
    
    # ─── FİNAL KARAR & RENK ───
    if normalized_score >= 80:
        signal = "GÜÇLÜ AL"
        color = "#10b981"
    elif normalized_score >= 60:
        signal = "AL"
        color = "#34d399"
    elif normalized_score <= 20:
        signal = "GÜÇLÜ SAT"
        color = "#ef4444"
    elif normalized_score <= 40:
        signal = "SAT"
        color = "#f87171"
    else:
        signal = "BEKLE"
        color = "#fbbf24"

    # Risk Yönetimi (ATR Trailing Stop)
    atr = data['atr']
    price = data['price']
    
    # Volatiliteye göre dinamik çarpan
    stop_mult = 2.5 if data['adx'] > 30 else 2.0
    
    risk_levels = {
        "stop_loss": price - (stop_mult * atr),
        "take_profit_1": price + (stop_mult * 1.5 * atr),
        "take_profit_2": price + (stop_mult * 3.0 * atr),
        "risk_reward": 1.5
    }

    return normalized_score, signal, color, reasons, risk_levels

# ═══════════════════════════════════════════════════════════════════════════════
# 5. YAPAY ZEKA ANALİZ (FİLTRE-DOSTU KISA PROMPT)
# ═══════════════════════════════════════════════════════════════════════════════
def get_ai_analysis(data, score, signal):
    """Finans filtresine takılmayan kısa ve net prompt"""
    
    prompt = f"""
Sen bir veri analisti olarak çalışıyorsun. Aşağıdaki sayısal değerleri kısaca yorumla.

VERİ SETİ:
• Fiyat: {data['price']:.2f} | Değişim: %{data['change_pct']:+.2f}
• RSI: {data['rsi']:.1f} | MACD: {data['macd_status']}
• Bollinger %: {data['bb_position']:.1f} | ADX: {data['adx']:.1f}
• Trend: {data['trend_direction']} | Hacim: {data['volume_ratio']:.2f}x ortalama
• Destek: {data['support']:.2f} | Direnç: {data['resistance']:.2f}
• Hesaplanan Skor: {score}/100 → {signal}

KISA VE NET YANITLA (Maksimum 5 satır):
1. Mevcut teknik durum özeti (1 cümle)
2. En kritik seviye ve neden önemli (1 cümle)
3. Dikkat edilmesi gereken tek şey (1 cümle)
"""
    
    model = genai.GenerativeModel('gemini-2.5-flash-preview')
    
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    try:
        response = model.generate_content(prompt, safety_settings=safety_settings)
        return response.text
    except Exception as e:
        return f"⚠️ Analiz yapılamadı: {str(e)}"

# ═══════════════════════════════════════════════════════════════════════════════
# 5. GELİŞMİŞ GRAFİK MOTORU
# ═══════════════════════════════════════════════════════════════════════════════
def create_analysis_chart(data):
    """Multi-panel gelişmiş analiz grafiği"""
    df = data['df'].tail(120)  # Son 120 gün
    
    # 3 Panelli Grafik
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=('', '', '')
    )
    
    # Panel 1: Fiyat + Bollinger + SMA
    # Mumlar
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Fiyat',
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444'
    ), row=1, col=1)
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_Upper'],
        line=dict(color='rgba(102, 126, 234, 0.3)', width=1),
        name='BB Üst',
        showlegend=False
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_Lower'],
        line=dict(color='rgba(102, 126, 234, 0.3)', width=1),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.05)',
        name='BB Alt',
        showlegend=False
    ), row=1, col=1)
    
    # SMA'lar
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA50'],
        line=dict(color='#fbbf24', width=1.5),
        name='50 Gün'
    ), row=1, col=1)
    
    if 'SMA200' in df.columns and not df['SMA200'].isna().all():
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA200'],
            line=dict(color='#8b5cf6', width=1.5),
            name='200 Gün'
        ), row=1, col=1)
    
    # Panel 2: RSI
    fig.add_trace(go.Scatter(
        x=df.index, y=df['RSI'],
        line=dict(color='#06b6d4', width=1.5),
        name='RSI'
    ), row=2, col=1)
    
    # RSI Seviyeleri
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(239, 68, 68, 0.5)", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(16, 185, 129, 0.5)", row=2, col=1)
    
    # Panel 3: MACD
    colors = ['#10b981' if val >= 0 else '#ef4444' for val in df['MACD_Hist']]
    fig.add_trace(go.Bar(
        x=df.index, y=df['MACD_Hist'],
        marker_color=colors,
        name='MACD Hist'
    ), row=3, col=1)
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['MACD'],
        line=dict(color='#3b82f6', width=1),
        name='MACD'
    ), row=3, col=1)
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['MACD_Signal'],
        line=dict(color='#f97316', width=1),
        name='Sinyal'
    ), row=3, col=1)
    
    # Layout
    fig.update_layout(
        height=600,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        font=dict(color='rgba(255,255,255,0.8)')
    )
    
    # Grid styling
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
# 6. BIST HİSSE LİSTESİ & MARKET SCANNER
# ═══════════════════════════════════════════════════════════════════════════════

# BIST'teki ana hisseler (BIST-30 ve seçili BIST-100 hisseleri)
BIST_STOCKS = [
    # BIST-30
    "AKBNK.IS", "ARCLK.IS", "ASELS.IS", "BIMAS.IS", "EKGYO.IS",
    "EREGL.IS", "FROTO.IS", "GARAN.IS", "GUBRF.IS", "HEKTS.IS",
    "ISCTR.IS", "KCHOL.IS", "KOZAA.IS", "KOZAL.IS", "KRDMD.IS",
    "MGROS.IS", "ODAS.IS", "OYAKC.IS", "PETKM.IS", "PGSUS.IS",
    "SAHOL.IS", "SASA.IS", "SISE.IS", "TAVHL.IS", "TCELL.IS",
    "THYAO.IS", "TKFEN.IS", "TOASO.IS", "TTKOM.IS", "TUPRS.IS",
    "VESTL.IS", "YKBNK.IS",
    # Ek Popüler Hisseler
    "AEFES.IS", "AKSA.IS", "ALARK.IS", "ALFAS.IS", "ANHYT.IS",
    "AYGAZ.IS", "BRISA.IS", "CCOLA.IS", "CEMAS.IS", "DOHOL.IS",
    "EGEEN.IS", "ENKAI.IS", "GESAN.IS", "GOLTS.IS", "ISGYO.IS",
    "ISMEN.IS", "KARTN.IS", "KERVT.IS", "KLRHO.IS", "KONTR.IS",
    "LOGO.IS", "MAVI.IS", "MPARK.IS", "NETAS.IS", "OTKAR.IS",
    "PAPIL.IS", "POLHO.IS", "QUAGR.IS", "SDTTR.IS", "SELEC.IS",
    "SKBNK.IS", "SMRTG.IS", "SOKM.IS", "TATGD.IS", "TMSN.IS",
    "TRGYO.IS", "TSKB.IS", "TTRAK.IS", "TUKAS.IS", "TURSG.IS",
    "ULKER.IS", "VAKBN.IS", "VESBE.IS", "YATAS.IS", "ZOREN.IS"
]

@st.cache_data(ttl=60, show_spinner=False)
def scan_single_stock(symbol):
    """Tek bir hisseyi tarar ve sonucu döndürür"""
    try:
        data = get_advanced_data(symbol)
        if data is None:
            return None
        
        weekly_data = get_weekly_trend(symbol)
        score, signal, color, reasons, risk_levels = calculate_smart_score(data, weekly_data)
        
        return {
            "Sembol": symbol.replace(".IS", ""),
            "Fiyat": data['price'],
            "Değişim %": data['change_pct'],
            "Sinyal": signal,
            "Skor": score,
            "RSI": data['rsi'],
            "ADX": data['adx'],
            "CMF": data['cmf'],
            "Trend": data['trend_direction'],
            "Hacim": data['volume_ratio'],
            "_color": color,
            "_score": score
        }
    except:
        return None

def scan_market(stock_list, progress_callback=None):
    """Tüm hisseleri tarar ve sonuçları skor sırasına göre döndürür"""
    results = []
    total = len(stock_list)
    
    for i, symbol in enumerate(stock_list):
        if progress_callback:
            progress_callback((i + 1) / total, f"Taraniyor: {symbol.replace('.IS', '')} ({i+1}/{total})")
        
        result = scan_single_stock(symbol)
        if result:
            results.append(result)
    
    # Skora göre sırala (yüksekten düşüğe)
    results.sort(key=lambda x: x['_score'], reverse=True)
    
    return results

# ═══════════════════════════════════════════════════════════════════════════════
# 7. ANA ARAYÜZ
# ═══════════════════════════════════════════════════════════════════════════════

# Başlık
st.markdown('''
<div class="brand-header">
    <div class="brand-logo">TRENDER <span>PRO</span></div>
    <div class="brand-tagline">Teknik Analiz Platformu</div>
</div>
''', unsafe_allow_html=True)

# Mod Seçimi (Tabs)
tab_analiz, tab_scanner = st.tabs(["📊 Hisse Analizi", "🔍 Piyasa Tarayıcı"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: TEK HİSSE ANALİZİ
# ═══════════════════════════════════════════════════════════════════════════════
with tab_analiz:
    # Input Alanı
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        input_col, btn_col = st.columns([3, 1])
        with input_col:
            symbol = st.text_input(
                "Hisse Kodu",
                value="THYAO.IS",
                label_visibility="collapsed",
                placeholder="Sembol girin (THYAO.IS, GARAN.IS)"
            )
        with btn_col:
            analyze_click = st.button("ANALIZ", type="primary", use_container_width=True)

    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False

    if analyze_click:
        st.session_state.analyzed = True
        st.session_state.symbol = symbol

    # Analiz Butonu Tıklandığında
    if st.session_state.analyzed:
        target_symbol = st.session_state.symbol
        with st.spinner(""):
            data = get_advanced_data(target_symbol.upper().strip())
            weekly_data = get_weekly_trend(target_symbol.upper().strip())
            # VectorBT ile Profesyonel Backtest
            backtest_results = run_robust_backtest(target_symbol.upper().strip())
        
        if data:
            # ═══ SİNYAL SKORU (SNIPER ALGORİTMASI v3 - Multi-Timeframe) ═══
            score, signal, signal_color, reasons, risk_levels = calculate_smart_score(data, weekly_data)
            
            # Karar Paneli
            pulse_class = "pulse-active" if score >= 75 or score <= 25 else ""
            
            # Reasons HTML (ilk 5 reason)
            reasons_display = reasons[:5] if len(reasons) > 5 else reasons
            reasons_html = " · ".join(reasons_display) if reasons_display else ""
            
            # Risk seviyeleri
            sl = risk_levels['stop_loss']
            tp1 = risk_levels['take_profit_1']
            tp2 = risk_levels['take_profit_2']
            
            # Backtest bilgisi
            bt_html = ""
            if backtest_results and backtest_results.get('total_trades', 0) > 0:
                wr = backtest_results['win_rate']
                total_pnl = backtest_results['total_pnl']
                total_trades = backtest_results['total_trades']
                wr_color = "#10b981" if wr >= 50 else "#ef4444"
                pnl_color = "#10b981" if total_pnl > 0 else "#ef4444"
                bt_html = f'''
<div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.06);">
<div style="font-size: 0.6rem; color: rgba(255,255,255,0.3); text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 0.5rem;">2 Yıllık Backtest</div>
<div style="display: flex; justify-content: center; gap: 1.5rem;">
<div style="text-align: center;">
<div style="font-size: 0.5rem; color: rgba(255,255,255,0.3);">İşlem</div>
<div style="font-size: 0.9rem; color: white;">{total_trades}</div>
</div>
<div style="text-align: center;">
<div style="font-size: 0.5rem; color: rgba(255,255,255,0.3);">Kazanma</div>
<div style="font-size: 0.9rem; color: {wr_color};">%{wr:.0f}</div>
</div>
<div style="text-align: center;">
<div style="font-size: 0.5rem; color: rgba(255,255,255,0.3);">Toplam P/L</div>
<div style="font-size: 0.9rem; color: {pnl_color};">%{total_pnl:.1f}</div>
</div>
</div>
</div>'''
            
            st.markdown(f'''
<div class="decision-panel {pulse_class}" style="--signal-color: {signal_color};">
<div class="signal-label">Sinyal</div>
<div class="signal-value" style="color: {signal_color};">{signal}</div>
<div class="signal-score">Güç: {score}/100</div>
<div class="score-bar-container">
<div class="score-bar-fill" style="width: {score}%; background: {signal_color};"></div>
</div>
<div style="margin-top: 1rem; font-size: 0.7rem; color: rgba(255,255,255,0.4); letter-spacing: 0.5px;">
{reasons_html}
</div>
<div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06);">
<div style="text-align: center;">
<div style="font-size: 0.6rem; color: rgba(255,255,255,0.3); text-transform: uppercase; letter-spacing: 1px;">Stop Loss</div>
<div style="font-size: 1rem; color: #ef4444; font-weight: 600;">{sl:.2f} ₺</div>
</div>
<div style="text-align: center;">
<div style="font-size: 0.6rem; color: rgba(255,255,255,0.3); text-transform: uppercase; letter-spacing: 1px;">Hedef 1</div>
<div style="font-size: 1rem; color: #10b981; font-weight: 600;">{tp1:.2f} ₺</div>
</div>
<div style="text-align: center;">
<div style="font-size: 0.6rem; color: rgba(255,255,255,0.3); text-transform: uppercase; letter-spacing: 1px;">Hedef 2</div>
<div style="font-size: 1rem; color: #10b981; font-weight: 600;">{tp2:.2f} ₺</div>
</div>
</div>
{bt_html}
</div>
''', unsafe_allow_html=True)
            
            # ═══ ANA METRİKLER ═══
            st.markdown('<div class="section-title">Temel Göstergeler</div>', unsafe_allow_html=True)
            
            kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
            
            # Fiyat
            delta_color = "normal" if data['change_pct'] >= 0 else "inverse"
            kpi1.metric(
                "Fiyat",
                f"{data['price']:.2f} ₺",
                f"{data['change_pct']:+.2f}%",
                delta_color=delta_color
            )
            
            # RSI
            if data['rsi'] > 70:
                rsi_label = "RSI · Pahalı"
                rsi_desc = "Satış baskısı olası"
            elif data['rsi'] < 30:
                rsi_label = "RSI · Ucuz"
                rsi_desc = "Alım fırsatı olası"
            else:
                rsi_label = "RSI"
                rsi_desc = "Dengeli"
            kpi2.metric(rsi_label, f"{data['rsi']:.1f}", rsi_desc)
            
            # MACD
            macd_desc = "Yukarı momentum" if data['macd_status'] == "AL" else "Aşağı momentum"
            kpi3.metric("MACD", data['macd_status'], macd_desc)
            
            # ADX
            adx_desc = "Trend güçlü" if data['adx'] > 25 else "Trend zayıf"
            kpi4.metric("Trend Gücü", f"{data['adx']:.1f}", adx_desc)
            
            # Volatilite
            if data['atr_pct'] > 3:
                vol_desc = "Yüksek risk"
            elif data['atr_pct'] > 1.5:
                vol_desc = "Normal"
            else:
                vol_desc = "Düşük risk"
            kpi5.metric("Volatilite", f"%{data['atr_pct']:.2f}", vol_desc)
            
            st.markdown("---")
            
            # ═══ DETAY METRİKLER ═══
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown('<div class="section-title">Momentum & Akıllı Para</div>', unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                
                # CMF (Smart Money)
                if data['cmf'] > 0.05:
                    cmf_desc = "Para Girişi"
                elif data['cmf'] < -0.05:
                    cmf_desc = "Para Çıkışı"
                else:
                    cmf_desc = "Nötr"
                m1.metric("CMF", f"{data['cmf']:.3f}", cmf_desc)
                
                bb_desc = "Üst bant" if data['bb_position'] > 80 else "Alt bant" if data['bb_position'] < 20 else "Orta"
                m2.metric("Bollinger", f"{data['bb_position']:.1f}%", bb_desc)
                
                m3, m4 = st.columns(2)
                m3.metric("EMA 50", f"{data['ema50']:.2f} ₺", "Kısa vade")
                m4.metric("EMA 200", f"{data['ema200']:.2f} ₺" if pd.notna(data['ema200']) else "—", "Uzun vade")
            
            with col_right:
                st.markdown('<div class="section-title">Seviyeler</div>', unsafe_allow_html=True)
                s1, s2 = st.columns(2)
                
                res_dist = ((data['resistance'] - data['price']) / data['price']) * 100
                s1.metric("Direnç", f"{data['resistance']:.2f} ₺", f"{res_dist:+.1f}%")
                
                sup_dist = ((data['support'] - data['price']) / data['price']) * 100
                s2.metric("Destek", f"{data['support']:.2f} ₺", f"{sup_dist:+.1f}%")
                
                s3, s4 = st.columns(2)
                s3.metric("Pivot", f"{data['pivot']:.2f} ₺", "Denge")
                
                vol_status = "Yoğun" if data['volume_ratio'] > 1.5 else "Düşük" if data['volume_ratio'] < 0.5 else "Normal"
                s4.metric("Hacim", f"{data['volume_ratio']:.2f}x", vol_status)
            
            st.markdown("---")
            
            # ═══ GRAFİK ═══
            st.markdown('<div class="section-title">Teknik Grafik</div>', unsafe_allow_html=True)
            chart = create_analysis_chart(data)
            st.plotly_chart(chart, use_container_width=True)
            
            st.markdown("---")
            
            # ═══ AI ANALİZİ ═══
            with st.status("AI Analizi hazırlanıyor...", expanded=True) as status:
                ai_comment = get_ai_analysis(data, score, signal)
                st.markdown(ai_comment)
                status.update(label="Analiz tamamlandı", state="complete", expanded=True)
            
            # ═══ OPTİMİZASYON (YENİ) ═══
            st.markdown("---")
            st.markdown('<div class="section-title">🧬 Strateji Optimizasyonu</div>', unsafe_allow_html=True)
            if st.button("En İyi Parametreleri Bul", type="secondary", use_container_width=True):
                with st.spinner("En uygun parametreler taranıyor..."):
                    best_params = optimize_strategy_robust(target_symbol.upper().strip())
                    st.success("✅ Optimizasyon Tamamlandı! En yüksek getiri sağlayan ayarlar:")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("RSI Periyodu", best_params.get('rsi_period', 14))
                    c2.metric("RSI Eşik", best_params.get('rsi_threshold', 40))
                    c3.metric("EMA Trend", best_params.get('ema_period', 200))
                    st.info(f"💡 {target_symbol} için bu parametreler geçmişte en yüksek kârlılığı sağladı.")
                
        else:
            st.error("Veri bulunamadı. Sembolü kontrol edin.")
            st.info("BIST hisseleri için .IS ekleyin. Örnek: THYAO.IS")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: PİYASA TARAYICI
# ═══════════════════════════════════════════════════════════════════════════════
with tab_scanner:
    st.markdown('''
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 1.2rem; color: white; font-weight: 600; margin-bottom: 0.5rem;">
            🔍 BIST Piyasa Tarayıcı
        </div>
        <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5);">
            Tüm BIST hisselerini tarayın ve en güçlü sinyalleri bulun
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Tarama seçenekleri
    col_opt1, col_opt2, col_opt3 = st.columns([1, 2, 1])
    with col_opt2:
        scan_mode = st.selectbox(
            "Tarama Modu",
            ["BIST-30 + Popüler (77 Hisse)", "Sadece BIST-30 (32 Hisse)"],
            label_visibility="collapsed"
        )
        
        scan_button = st.button("🚀 TARAMAYI BAŞLAT", type="primary", use_container_width=True)
    
    if scan_button:
        # Hisse listesini belirle
        if "BIST-30" in scan_mode and "Popüler" in scan_mode:
            stocks_to_scan = BIST_STOCKS
        else:
            stocks_to_scan = BIST_STOCKS[:32]  # Sadece BIST-30
        
        # Progress bar
        progress_bar = st.progress(0, text="Tarama başlatılıyor...")
        
        def update_progress(progress, text):
            progress_bar.progress(progress, text=text)
        
        # Taramayı çalıştır
        with st.spinner(""):
            results = scan_market(stocks_to_scan, update_progress)
        
        progress_bar.empty()
        
        if results:
            st.success(f"✅ Tarama tamamlandı! {len(results)} hisse analiz edildi.")
            
            # Özet istatistikler
            strong_buy = sum(1 for r in results if r['Sinyal'] == "GÜÇLÜ AL")
            buy = sum(1 for r in results if r['Sinyal'] == "AL")
            wait = sum(1 for r in results if r['Sinyal'] == "BEKLE")
            sell = sum(1 for r in results if r['Sinyal'] == "SAT")
            strong_sell = sum(1 for r in results if r['Sinyal'] == "GÜÇLÜ SAT")
            
            stat1, stat2, stat3, stat4, stat5 = st.columns(5)
            stat1.metric("🟢 Güçlü Al", strong_buy)
            stat2.metric("🟩 Al", buy)
            stat3.metric("🟡 Bekle", wait)
            stat4.metric("🟧 Sat", sell)
            stat5.metric("🔴 Güçlü Sat", strong_sell)
            
            st.markdown("---")
            
            # Sonuç tablosu
            st.markdown('<div class="section-title">Sinyal Sıralaması (Güçlüden Zayıfa)</div>', unsafe_allow_html=True)
            
            # DataFrame oluştur
            df_results = pd.DataFrame(results)
            
            # Görüntüleme için sütunları seç ve formatla
            display_df = df_results[["Sembol", "Fiyat", "Değişim %", "Sinyal", "Skor", "RSI", "ADX", "Trend", "Hacim"]].copy()
            display_df["Fiyat"] = display_df["Fiyat"].apply(lambda x: f"{x:.2f} ₺")
            display_df["Değişim %"] = display_df["Değişim %"].apply(lambda x: f"{x:+.2f}%")
            display_df["RSI"] = display_df["RSI"].apply(lambda x: f"{x:.1f}")
            display_df["ADX"] = display_df["ADX"].apply(lambda x: f"{x:.1f}")
            display_df["Hacim"] = display_df["Hacim"].apply(lambda x: f"{x:.2f}x")
            
            # Sinyal renklerini belirle
            def style_signal(val):
                color_map = {
                    "GÜÇLÜ AL": "background-color: #10b981; color: white; font-weight: bold;",
                    "AL": "background-color: #34d399; color: white;",
                    "BEKLE": "background-color: #fbbf24; color: black;",
                    "SAT": "background-color: #f87171; color: white;",
                    "GÜÇLÜ SAT": "background-color: #ef4444; color: white; font-weight: bold;"
                }
                return color_map.get(val, "")
            
            def style_skor(val):
                if val >= 75:
                    return "background-color: rgba(16, 185, 129, 0.3); color: #10b981; font-weight: bold;"
                elif val >= 60:
                    return "background-color: rgba(52, 211, 153, 0.2); color: #34d399;"
                elif val <= 25:
                    return "background-color: rgba(239, 68, 68, 0.3); color: #ef4444; font-weight: bold;"
                elif val <= 40:
                    return "background-color: rgba(248, 113, 113, 0.2); color: #f87171;"
                else:
                    return "background-color: rgba(251, 191, 36, 0.2); color: #fbbf24;"
            
            # Styled DataFrame
            styled_df = display_df.style.applymap(
                style_signal, subset=["Sinyal"]
            ).applymap(
                style_skor, subset=["Skor"]
            ).set_properties(**{
                'text-align': 'center',
                'font-size': '0.85rem'
            }).set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'center'), ('font-size', '0.75rem'), ('color', 'rgba(255,255,255,0.6)'), ('text-transform', 'uppercase'), ('letter-spacing', '1px')]},
                {'selector': 'td', 'props': [('padding', '0.5rem')]},
            ])
            
            st.dataframe(styled_df, use_container_width=True, height=500)
            
            # En iyi 5 hisse
            if len(results) >= 5:
                st.markdown("---")
                st.markdown('<div class="section-title">🏆 En Güçlü 5 Sinyal</div>', unsafe_allow_html=True)
                
                top5 = results[:5]
                cols = st.columns(5)
                for i, stock in enumerate(top5):
                    with cols[i]:
                        signal_color = stock['_color']
                        st.markdown(f'''
                        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1rem; text-align: center;">
                            <div style="font-size: 1.2rem; font-weight: 700; color: white;">{stock['Sembol']}</div>
                            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5); margin: 0.25rem 0;">{stock['Fiyat']:.2f} ₺</div>
                            <div style="font-size: 1.5rem; font-weight: 800; color: {signal_color}; margin: 0.5rem 0;">{stock['Skor']}</div>
                            <div style="font-size: 0.7rem; color: {signal_color}; font-weight: 600;">{stock['Sinyal']}</div>
                        </div>
                        ''', unsafe_allow_html=True)
        else:
            st.warning("Tarama sonucu bulunamadı. Lütfen tekrar deneyin.")

# Footer
st.markdown('''
<div class="footer">
    TRENDER PRO · Teknik Analiz Platformu
</div>
''', unsafe_allow_html=True)