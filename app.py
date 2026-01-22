import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import pandas as pd
import numpy as np
import time
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
        
        # ═══════════════════════════════════════════════════════════════════
        # ADAPTIVE STRATEGY GENERATOR - YENİ İNDİKATÖRLER (20+ Sinyal Havuzu)
        # ═══════════════════════════════════════════════════════════════════
        
        # ─── CCI (Commodity Channel Index - 20 Periyot) ───
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        sma_tp = typical_price.rolling(window=20).mean()
        mean_deviation = typical_price.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
        df['CCI'] = (typical_price - sma_tp) / (0.015 * mean_deviation)
        
        # ─── Williams %R (14 Periyot) ───
        highest_high = df['High'].rolling(window=14).max()
        lowest_low = df['Low'].rolling(window=14).min()
        df['Williams_R'] = -100 * (highest_high - df['Close']) / (highest_high - lowest_low)
        
        # ─── MFI (Money Flow Index - 14 Periyot) ───
        typical_price_mfi = (df['High'] + df['Low'] + df['Close']) / 3
        raw_money_flow = typical_price_mfi * df['Volume']
        money_flow_positive = raw_money_flow.where(typical_price_mfi > typical_price_mfi.shift(1), 0)
        money_flow_negative = raw_money_flow.where(typical_price_mfi < typical_price_mfi.shift(1), 0)
        positive_flow_sum = money_flow_positive.rolling(window=14).sum()
        negative_flow_sum = money_flow_negative.rolling(window=14).sum()
        money_flow_ratio = positive_flow_sum / negative_flow_sum.replace(0, 0.001)
        df['MFI'] = 100 - (100 / (1 + money_flow_ratio))
        
        # ─── ROC (Rate of Change - 12 Periyot) ───
        df['ROC'] = ((df['Close'] - df['Close'].shift(12)) / df['Close'].shift(12)) * 100
        
        # ─── Ultimate Oscillator ───
        bp = df['Close'] - pd.concat([df['Low'], df['Close'].shift(1)], axis=1).min(axis=1)
        tr_uo = pd.concat([df['High'], df['Close'].shift(1)], axis=1).max(axis=1) - pd.concat([df['Low'], df['Close'].shift(1)], axis=1).min(axis=1)
        avg7 = bp.rolling(7).sum() / tr_uo.rolling(7).sum()
        avg14 = bp.rolling(14).sum() / tr_uo.rolling(14).sum()
        avg28 = bp.rolling(28).sum() / tr_uo.rolling(28).sum()
        df['Ultimate_Osc'] = 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7
        
        # ─── Aroon Indicator (25 Periyot) ───
        aroon_period = 25
        df['Aroon_Up'] = 100 * df['High'].rolling(aroon_period + 1).apply(lambda x: x.argmax()) / aroon_period
        df['Aroon_Down'] = 100 * df['Low'].rolling(aroon_period + 1).apply(lambda x: x.argmin()) / aroon_period
        
        # ─── Elder Ray (Bull/Bear Power) ───
        ema13 = df['Close'].ewm(span=13, adjust=False).mean()
        df['Bull_Power'] = df['High'] - ema13
        df['Bear_Power'] = df['Low'] - ema13
        
        # ─── TRIX (15 Periyot) ───
        ema1 = df['Close'].ewm(span=15, adjust=False).mean()
        ema2 = ema1.ewm(span=15, adjust=False).mean()
        ema3 = ema2.ewm(span=15, adjust=False).mean()
        df['TRIX'] = (ema3 - ema3.shift(1)) / ema3.shift(1) * 10000
        df['TRIX_Signal'] = df['TRIX'].ewm(span=9, adjust=False).mean()
        
        # ─── PPO (Percentage Price Oscillator) ───
        ema12_ppo = df['Close'].ewm(span=12, adjust=False).mean()
        ema26_ppo = df['Close'].ewm(span=26, adjust=False).mean()
        df['PPO'] = ((ema12_ppo - ema26_ppo) / ema26_ppo) * 100
        df['PPO_Signal'] = df['PPO'].ewm(span=9, adjust=False).mean()
        
        # ─── Parabolic SAR (Basitleştirilmiş) ───
        # İlk değerler için trend yönünü belirle
        af_start = 0.02
        af_max = 0.2
        df['PSAR'] = np.nan
        
        # Basit SAR hesaplaması (trend takibi için)
        psar = df['Low'].iloc[0]
        ep = df['High'].iloc[0]
        af = af_start
        trend = 1  # 1: Yukarı, -1: Aşağı
        
        psar_values = [psar]
        for i in range(1, len(df)):
            if trend == 1:
                psar = psar + af * (ep - psar)
                psar = min(psar, df['Low'].iloc[i-1], df['Low'].iloc[max(0, i-2)])
                if df['Low'].iloc[i] < psar:
                    trend = -1
                    psar = ep
                    ep = df['Low'].iloc[i]
                    af = af_start
                else:
                    if df['High'].iloc[i] > ep:
                        ep = df['High'].iloc[i]
                        af = min(af + af_start, af_max)
            else:
                psar = psar + af * (ep - psar)
                psar = max(psar, df['High'].iloc[i-1], df['High'].iloc[max(0, i-2)])
                if df['High'].iloc[i] > psar:
                    trend = 1
                    psar = ep
                    ep = df['High'].iloc[i]
                    af = af_start
                else:
                    if df['Low'].iloc[i] < ep:
                        ep = df['Low'].iloc[i]
                        af = min(af + af_start, af_max)
            psar_values.append(psar)
        
        df['PSAR'] = psar_values
        
        # ─── Donchian Channels (20 Periyot) ───
        df['Donchian_High'] = df['High'].rolling(window=20).max()
        df['Donchian_Low'] = df['Low'].rolling(window=20).min()
        df['Donchian_Mid'] = (df['Donchian_High'] + df['Donchian_Low']) / 2
        
        # ─── SuperTrend (ATR Multiplier: 3) ───
        supertrend_mult = 3
        hl2 = (df['High'] + df['Low']) / 2
        upperband = hl2 + (supertrend_mult * df['ATR'])
        lowerband = hl2 - (supertrend_mult * df['ATR'])
        
        supertrend = [True] * len(df)  # True = Uptrend
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > upperband.iloc[i-1]:
                supertrend[i] = True
            elif df['Close'].iloc[i] < lowerband.iloc[i-1]:
                supertrend[i] = False
            else:
                supertrend[i] = supertrend[i-1]
        
        df['SuperTrend'] = [lowerband.iloc[i] if supertrend[i] else upperband.iloc[i] for i in range(len(df))]
        df['SuperTrend_Direction'] = supertrend  # True = Bullish
        
        # ─── VWAP (Volume Weighted Average Price - Günlük Reset Yok, Kümülatif) ───
        df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
        
        # ─── Bollinger %B ───
        df['BB_PercentB'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
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
            # ═══ ADAPTİF SİSTEM YENİ İNDİKATÖRLER ═══
            "cci": curr['CCI'],
            "williams_r": curr['Williams_R'],
            "mfi": curr['MFI'],
            "roc": curr['ROC'],
            "ultimate_osc": curr['Ultimate_Osc'],
            "aroon_up": curr['Aroon_Up'],
            "aroon_down": curr['Aroon_Down'],
            "bull_power": curr['Bull_Power'],
            "bear_power": curr['Bear_Power'],
            "trix": curr['TRIX'],
            "trix_signal": curr['TRIX_Signal'],
            "ppo": curr['PPO'],
            "ppo_signal": curr['PPO_Signal'],
            "psar": curr['PSAR'],
            "donchian_high": curr['Donchian_High'],
            "donchian_low": curr['Donchian_Low'],
            "supertrend": curr['SuperTrend'],
            "supertrend_dir": curr['SuperTrend_Direction'],
            "vwap": curr['VWAP'],
            "bb_percentb": curr['BB_PercentB'],
            # Divergence
            "divergence": divergence_signal,
        }
    except Exception as e:
        st.error(f"Veri Hatası ({symbol}): {str(e)}")
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
    except Exception as e:
        st.error(f"Haftalık Veri Hatası ({symbol}): {str(e)}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 3.5.1 PİYASA REJİMİ TESPİTİ (Regime Switching)
# ═══════════════════════════════════════════════════════════════════════════════
def detect_market_regime(adx_value):
    """
    ADX değerine göre piyasa rejimini belirler.
    
    Returns:
        tuple: (regime_name, oscillator_weight_mult, trend_weight_mult)
        - "RANGE": ADX < 20 → Salınım moduna geç (RSI, Stokastik ağırlığı artar)
        - "TRANSITION": 20 <= ADX < 25 → Geçiş bölgesi
        - "TREND": ADX >= 25 → Trend moduna geç (MACD, EMA ağırlığı artar)
    """
    if pd.isna(adx_value) or adx_value is None:
        return ("TRANSITION", 1.0, 1.0)  # Varsayılan nötr
    
    if adx_value < 20:
        # YATAY PİYASA: Osilatörler daha iyi çalışır
        return ("RANGE", 2.5, 0.5)
    elif adx_value < 25:
        # GEÇİŞ BÖLGESİ: Dengeli yaklaşım
        return ("TRANSITION", 1.5, 1.0)
    else:
        # GÜÇLÜ TREND: Trend indikatörleri daha iyi çalışır
        return ("TREND", 0.5, 2.0)

# ═══════════════════════════════════════════════════════════════════════════════
# 3.5.2 ENDEKS VERİSİ (BIST XU100 Korelasyonu)
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def get_index_data():
    """
    BIST 100 (XU100.IS) endeks verisini çeker.
    Çıkış stratejisinde endeks korelasyonu için kullanılır.
    
    Returns:
        dict: Endeks fiyatı, EMA20, ve güç durumu
    """
    try:
        ticker = yf.Ticker("XU100.IS")
        hist = ticker.history(period="6mo")
        
        if hist.empty or len(hist) < 20:
            return None
        
        hist['EMA20'] = hist['Close'].ewm(span=20, adjust=False).mean()
        curr = hist.iloc[-1]
        
        return {
            "price": curr['Close'],
            "ema20": curr['EMA20'],
            "is_strong": curr['Close'] > curr['EMA20']  # Endeks güçlü mü?
        }
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 3.5.3 ADAPTİF STRATEJİ JENERATÖRÜ - KENDİ KENDİNE ÖĞRENEN SİSTEM
# ═══════════════════════════════════════════════════════════════════════════════

# 22 İndikatör için AL koşulları tanımları
INDICATOR_BUY_CONDITIONS = {
    # MOMENTUM İNDİKATÖRLERİ
    'RSI': lambda df: (df['RSI'] < 30),
    'StochRSI': lambda df: (df['StochRSI'] < 20),
    'CCI': lambda df: (df['CCI'] < -100),
    'Williams_R': lambda df: (df['Williams_R'] < -80),
    'MFI': lambda df: (df['MFI'] < 20),
    'ROC': lambda df: (df['ROC'] > 0) & (df['ROC'].diff() > 0),
    'Ultimate_Osc': lambda df: (df['Ultimate_Osc'] < 30),
    
    # TREND İNDİKATÖRLERİ
    'MACD_Cross': lambda df: (df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)),
    'EMA_Golden': lambda df: (df['Close'] > df['EMA50']) & (df['EMA50'] > df['EMA200']),
    'Aroon_Bullish': lambda df: (df['Aroon_Up'] > 70) & (df['Aroon_Down'] < 30),
    'TRIX_Cross': lambda df: (df['TRIX'] > df['TRIX_Signal']) & (df['TRIX'].shift(1) <= df['TRIX_Signal'].shift(1)),
    'PPO_Cross': lambda df: (df['PPO'] > df['PPO_Signal']) & (df['PPO'].shift(1) <= df['PPO_Signal'].shift(1)),
    'PSAR_Bullish': lambda df: (df['Close'] > df['PSAR']),
    'SuperTrend_Bull': lambda df: df['SuperTrend_Direction'] == True,
    'Ichimoku_TK': lambda df: (df['Tenkan'] > df['Kijun']) & (df['Tenkan'].shift(1) <= df['Kijun'].shift(1)),
    
    # HACİM İNDİKATÖRLERİ
    'CMF_Positive': lambda df: (df['CMF'] > 0.10),
    'OBV_Rising': lambda df: (df['OBV'] > df['OBV_SMA20']),
    'VWAP_Above': lambda df: (df['Close'] > df['VWAP']),
    
    # VOLATİLİTE / BREAKOUT İNDİKATÖRLERİ
    'BB_Oversold': lambda df: (df['BB_PercentB'] < 0),
    'Donchian_Break': lambda df: (df['High'] >= df['Donchian_High'].shift(1)),
    'Keltner_Squeeze': lambda df: (df['BB_Upper'] < df['Keltner_Upper']) & (df['BB_Lower'] > df['Keltner_Lower']),
    
    # ELDER RAY
    'Elder_Bullish': lambda df: (df['Bull_Power'] > 0) & (df['Bull_Power'].diff() > 0),
}

def backtest_single_indicator(df, indicator_name, buy_condition_func, hold_days=5, min_return=0.02):
    """
    TEK BİR İNDİKATÖRÜN TARİHSEL BAŞARISINI ÖLÇER.
    
    Mantık:
    1. 1 yıllık veriyi tara
    2. Her AL sinyalinde hold_days gün sonraki getiriyi hesapla
    3. Pozitif getiri (> min_return) = Başarılı sinyal
    
    Args:
        df: DataFrame (tüm indikatörler hesaplanmış)
        indicator_name: İndikatör adı
        buy_condition_func: AL koşulu fonksiyonu
        hold_days: Pozisyon tutma süresi (gün)
        min_return: Başarı eşiği (varsayılan %2)
        
    Returns:
        dict: {
            'win_rate': float,  # Başarı oranı (%)
            'total_signals': int,  # Toplam sinyal sayısı
            'avg_return': float,  # Ortalama getiri (%)
            'confidence': float  # 0-100 arası güven skoru
        }
    """
    try:
        # Forward return hesapla
        df = df.copy()
        df['Forward_Return'] = df['Close'].shift(-hold_days) / df['Close'] - 1
        
        # AL sinyallerini bul
        try:
            buy_signals = buy_condition_func(df)
        except Exception:
            return {'win_rate': 0, 'total_signals': 0, 'avg_return': 0, 'confidence': 0}
        
        # Sinyal olan günleri filtrele
        signal_df = df[buy_signals].dropna(subset=['Forward_Return'])
        
        if len(signal_df) < 3:  # Minimum 3 sinyal gerekli
            return {'win_rate': 0, 'total_signals': len(signal_df), 'avg_return': 0, 'confidence': 0}
        
        # Başarı oranı hesapla
        wins = (signal_df['Forward_Return'] > min_return).sum()
        total = len(signal_df)
        win_rate = (wins / total) * 100
        avg_return = signal_df['Forward_Return'].mean() * 100
        
        # Güven skoru (win_rate + sinyal sayısı bonusu)
        signal_bonus = min(10, total / 2)  # Her 2 sinyal için +1, max 10
        confidence = win_rate + signal_bonus
        
        return {
            'win_rate': round(win_rate, 1),
            'total_signals': total,
            'avg_return': round(avg_return, 2),
            'confidence': round(min(100, confidence), 1)
        }
    except Exception:
        return {'win_rate': 0, 'total_signals': 0, 'avg_return': 0, 'confidence': 0}


@st.cache_data(ttl=600)
def calculate_indicator_confidence_scores(symbol):
    """
    HER İNDİKATÖR İÇİN O HİSSEYE ÖZEL GÜVEN SKORU HESAPLAR.
    
    Bu fonksiyon Adaptive Strategy Generator'ın kalbidir:
    - 22 indikatörü ayrı ayrı backtest eder
    - Her birinin tarihsel başarısını ölçer
    - Sadece %50+ başarılı olanları aktif işaretler
    
    Args:
        symbol: Hisse sembolü (örn: "THYAO.IS")
        
    Returns:
        dict: Her indikatör için {
            'confidence': float (0-100),
            'active': bool,
            'signals': int,
            'win_rate': float,
            'avg_return': float,
            'current_signal': 'AL' | 'SAT' | 'BEKLE'
        }
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")
        
        if df.empty or len(df) < 100:
            return None
        
        closes = df['Close']
        highs = df['High']
        lows = df['Low']
        volumes = df['Volume']
        
        # ═══════════════════════════════════════════════════════════════════
        # TÜM İNDİKATÖRLERİ HESAPLA
        # ═══════════════════════════════════════════════════════════════════
        
        # RSI
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Stochastic RSI
        rsi = df['RSI']
        df['StochRSI'] = (rsi - rsi.rolling(14).min()) / (rsi.rolling(14).max() - rsi.rolling(14).min()) * 100
        
        # EMA'lar
        df['EMA50'] = closes.ewm(span=50, adjust=False).mean()
        df['EMA200'] = closes.ewm(span=200, adjust=False).mean()
        
        # MACD
        ema12 = closes.ewm(span=12, adjust=False).mean()
        ema26 = closes.ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # ATR
        high_low = highs - lows
        high_close = np.abs(highs - closes.shift())
        low_close = np.abs(lows - closes.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=14).mean()
        
        # Bollinger Bands
        bb_mid = closes.rolling(window=20).mean()
        bb_std = closes.rolling(window=20).std()
        df['BB_Upper'] = bb_mid + (bb_std * 2)
        df['BB_Lower'] = bb_mid - (bb_std * 2)
        df['BB_PercentB'] = (closes - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # CMF
        mfv = ((closes - lows) - (highs - closes)) / (highs - lows)
        mfv = mfv.fillna(0)
        volume_mfv = mfv * volumes
        df['CMF'] = volume_mfv.rolling(20).sum() / volumes.rolling(20).sum()
        
        # OBV
        obv = (np.sign(closes.diff()) * volumes).fillna(0).cumsum()
        df['OBV'] = obv
        df['OBV_SMA20'] = df['OBV'].rolling(window=20).mean()
        
        # CCI
        typical_price = (highs + lows + closes) / 3
        sma_tp = typical_price.rolling(window=20).mean()
        mean_dev = typical_price.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
        df['CCI'] = (typical_price - sma_tp) / (0.015 * mean_dev)
        
        # Williams %R
        highest_high = highs.rolling(window=14).max()
        lowest_low = lows.rolling(window=14).min()
        df['Williams_R'] = -100 * (highest_high - closes) / (highest_high - lowest_low)
        
        # MFI
        typical_price_mfi = (highs + lows + closes) / 3
        raw_money_flow = typical_price_mfi * volumes
        mf_pos = raw_money_flow.where(typical_price_mfi > typical_price_mfi.shift(1), 0)
        mf_neg = raw_money_flow.where(typical_price_mfi < typical_price_mfi.shift(1), 0)
        mf_ratio = mf_pos.rolling(14).sum() / mf_neg.rolling(14).sum().replace(0, 0.001)
        df['MFI'] = 100 - (100 / (1 + mf_ratio))
        
        # ROC
        df['ROC'] = ((closes - closes.shift(12)) / closes.shift(12)) * 100
        
        # Ultimate Oscillator
        bp = closes - pd.concat([lows, closes.shift(1)], axis=1).min(axis=1)
        tr_uo = pd.concat([highs, closes.shift(1)], axis=1).max(axis=1) - pd.concat([lows, closes.shift(1)], axis=1).min(axis=1)
        avg7 = bp.rolling(7).sum() / tr_uo.rolling(7).sum()
        avg14 = bp.rolling(14).sum() / tr_uo.rolling(14).sum()
        avg28 = bp.rolling(28).sum() / tr_uo.rolling(28).sum()
        df['Ultimate_Osc'] = 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7
        
        # Aroon
        aroon_period = 25
        df['Aroon_Up'] = 100 * highs.rolling(aroon_period + 1).apply(lambda x: x.argmax()) / aroon_period
        df['Aroon_Down'] = 100 * lows.rolling(aroon_period + 1).apply(lambda x: x.argmin()) / aroon_period
        
        # TRIX
        ema1 = closes.ewm(span=15, adjust=False).mean()
        ema2 = ema1.ewm(span=15, adjust=False).mean()
        ema3 = ema2.ewm(span=15, adjust=False).mean()
        df['TRIX'] = (ema3 - ema3.shift(1)) / ema3.shift(1) * 10000
        df['TRIX_Signal'] = df['TRIX'].ewm(span=9, adjust=False).mean()
        
        # PPO
        ema12_ppo = closes.ewm(span=12, adjust=False).mean()
        ema26_ppo = closes.ewm(span=26, adjust=False).mean()
        df['PPO'] = ((ema12_ppo - ema26_ppo) / ema26_ppo) * 100
        df['PPO_Signal'] = df['PPO'].ewm(span=9, adjust=False).mean()
        
        # Parabolic SAR (Basitleştirilmiş)
        af_start, af_max = 0.02, 0.2
        psar = lows.iloc[0]
        ep = highs.iloc[0]
        af = af_start
        trend = 1
        psar_values = [psar]
        for i in range(1, len(df)):
            if trend == 1:
                psar = psar + af * (ep - psar)
                psar = min(psar, lows.iloc[i-1], lows.iloc[max(0, i-2)])
                if lows.iloc[i] < psar:
                    trend, psar, ep, af = -1, ep, lows.iloc[i], af_start
                elif highs.iloc[i] > ep:
                    ep, af = highs.iloc[i], min(af + af_start, af_max)
            else:
                psar = psar + af * (ep - psar)
                psar = max(psar, highs.iloc[i-1], highs.iloc[max(0, i-2)])
                if highs.iloc[i] > psar:
                    trend, psar, ep, af = 1, ep, highs.iloc[i], af_start
                elif lows.iloc[i] < ep:
                    ep, af = lows.iloc[i], min(af + af_start, af_max)
            psar_values.append(psar)
        df['PSAR'] = psar_values
        
        # SuperTrend
        supertrend_mult = 3
        hl2 = (highs + lows) / 2
        upperband = hl2 + (supertrend_mult * df['ATR'])
        lowerband = hl2 - (supertrend_mult * df['ATR'])
        supertrend = [True] * len(df)
        for i in range(1, len(df)):
            if closes.iloc[i] > upperband.iloc[i-1]:
                supertrend[i] = True
            elif closes.iloc[i] < lowerband.iloc[i-1]:
                supertrend[i] = False
            else:
                supertrend[i] = supertrend[i-1]
        df['SuperTrend_Direction'] = supertrend
        
        # Donchian Channels
        df['Donchian_High'] = highs.rolling(window=20).max()
        df['Donchian_Low'] = lows.rolling(window=20).min()
        
        # VWAP
        df['VWAP'] = (volumes * (highs + lows + closes) / 3).cumsum() / volumes.cumsum()
        
        # Ichimoku
        nine_h = highs.rolling(window=9).max()
        nine_l = lows.rolling(window=9).min()
        df['Tenkan'] = (nine_h + nine_l) / 2
        p26_h = highs.rolling(window=26).max()
        p26_l = lows.rolling(window=26).min()
        df['Kijun'] = (p26_h + p26_l) / 2
        
        # Keltner Channels
        df['Keltner_Mid'] = closes.ewm(span=20).mean()
        df['Keltner_Upper'] = df['Keltner_Mid'] + (2 * df['ATR'])
        df['Keltner_Lower'] = df['Keltner_Mid'] - (2 * df['ATR'])
        
        # Elder Ray
        ema13 = closes.ewm(span=13, adjust=False).mean()
        df['Bull_Power'] = highs - ema13
        df['Bear_Power'] = lows - ema13
        
        df = df.dropna()
        
        # ═══════════════════════════════════════════════════════════════════
        # HER İNDİKATÖRÜ BACKTEST ET
        # ═══════════════════════════════════════════════════════════════════
        
        results = {}
        current_row = df.iloc[-1]
        
        for indicator_name, condition_func in INDICATOR_BUY_CONDITIONS.items():
            # Backtest yap
            backtest_result = backtest_single_indicator(df, indicator_name, condition_func)
            
            # Mevcut sinyal durumunu kontrol et
            try:
                current_signal_mask = condition_func(df.tail(1))
                is_buy_now = current_signal_mask.iloc[0] if len(current_signal_mask) > 0 else False
            except Exception:
                is_buy_now = False
            
            # Aktiflik kontrolü (confidence >= 50 VE en az 3 sinyal)
            is_active = backtest_result['confidence'] >= 50 and backtest_result['total_signals'] >= 3
            
            results[indicator_name] = {
                'confidence': backtest_result['confidence'],
                'active': is_active,
                'signals': backtest_result['total_signals'],
                'win_rate': backtest_result['win_rate'],
                'avg_return': backtest_result['avg_return'],
                'current_signal': 'AL' if is_buy_now else 'BEKLE'
            }
        
        return results
        
    except Exception as e:
        return None


def generate_adaptive_signal(data, indicator_scores):
    """
    SADECE AKTİF İNDİKATÖRLERİN OY BİRLİĞİ İLE KARAR VERİR.
    
    Mantık:
    1. Aktif indikatörleri filtrele (confidence >= 50)
    2. Her aktif indikatörün mevcut sinyalini oku
    3. Ağırlıklı oylama yap (confidence = oy ağırlığı)
    4. Sonuç hesapla
    
    Karar Kuralları:
    - %60+ AL oyu → GÜÇLÜ AL (skor 80+)
    - %50-60 AL oyu → AL (skor 60+)
    - %40-50 AL oyu → BEKLE (skor 50)
    - %40'ın altı → SAT sinyali
    
    Args:
        data: Hisse teknik verileri
        indicator_scores: calculate_indicator_confidence_scores çıktısı
        
    Returns:
        tuple: (score, reasons, active_indicators)
    """
    if not indicator_scores:
        return 50, ["DNA verisi yok"], []
    
    # Aktif indikatörleri filtrele
    active_indicators = {
        name: info for name, info in indicator_scores.items() 
        if info['active']
    }
    
    if len(active_indicators) < 3:
        return 50, ["Yetersiz aktif indikatör"], list(active_indicators.keys())
    
    # Ağırlıklı oylama
    total_weight = 0
    buy_weight = 0
    buy_reasons = []
    
    for name, info in active_indicators.items():
        weight = info['confidence']
        total_weight += weight
        
        if info['current_signal'] == 'AL':
            buy_weight += weight
            buy_reasons.append(f"{name} (+{info['win_rate']:.0f}%)")
    
    # Oy oranı hesapla
    if total_weight > 0:
        buy_ratio = buy_weight / total_weight
    else:
        buy_ratio = 0
    
    # Skoru hesapla
    if buy_ratio >= 0.60:
        score = 80 + int((buy_ratio - 0.60) * 50)  # 80-100 arası
        reasons = [f"🎯 Güçlü Konsensüs (%{buy_ratio*100:.0f})"] + buy_reasons[:3]
    elif buy_ratio >= 0.50:
        score = 60 + int((buy_ratio - 0.50) * 200)  # 60-80 arası
        reasons = [f"✅ Çoğunluk AL (%{buy_ratio*100:.0f})"] + buy_reasons[:3]
    elif buy_ratio >= 0.40:
        score = 50
        reasons = [f"⏸️ Kararsız (%{buy_ratio*100:.0f})"]
    else:
        score = 30 + int(buy_ratio * 50)  # 30-50 arası
        reasons = [f"⚠️ Çoğunluk SAT (%{(1-buy_ratio)*100:.0f})"]
    
    # Aktif indikatör sayısı bonusu
    if len(active_indicators) >= 10:
        score = min(100, score + 5)
        reasons.append(f"📊 {len(active_indicators)} aktif indikatör")
    
    return min(100, max(0, score)), reasons, list(active_indicators.keys())


# Eski fonksiyonu koruyoruz (geriye uyumluluk için sarmalayıcı)
@st.cache_data(ttl=600)
def analyze_indicator_dna(symbol, lookback_days=60):
    """
    Geriye uyumluluk için eski API.
    Yeni sistem calculate_indicator_confidence_scores kullanır.
    """
    scores = calculate_indicator_confidence_scores(symbol)
    
    if not scores:
        return {"trend_weight": 1.0, "momentum_weight": 1.0, "volume_weight": 1.0}
    
    # Kategorilere göre ortalama başarı oranı hesapla
    momentum_indicators = ['RSI', 'StochRSI', 'CCI', 'Williams_R', 'MFI', 'ROC', 'Ultimate_Osc']
    trend_indicators = ['MACD_Cross', 'EMA_Golden', 'Aroon_Bullish', 'TRIX_Cross', 'PPO_Cross', 'PSAR_Bullish', 'SuperTrend_Bull', 'Ichimoku_TK']
    volume_indicators = ['CMF_Positive', 'OBV_Rising', 'VWAP_Above']
    
    def calc_category_weight(indicators):
        active = [scores[i]['win_rate'] for i in indicators if i in scores and scores[i]['active']]
        if not active:
            return 1.0
        avg_win = sum(active) / len(active)
        return 0.5 + (avg_win / 100)  # 0.5x - 1.5x arası
    
    return {
        "trend_weight": round(calc_category_weight(trend_indicators), 2),
        "momentum_weight": round(calc_category_weight(momentum_indicators), 2),
        "volume_weight": round(calc_category_weight(volume_indicators), 2),
        "indicator_scores": scores  # Yeni: Detaylı skorlar
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3.6 WYCKOFF & PRICE ACTION ANALİZ MOTORU
# ═══════════════════════════════════════════════════════════════════════════════

def detect_swing_points(df, lookback=5):
    """
    Swing High/Low (Tepe/Dip) noktalarını tespit eder.
    HH (Higher High), HL (Higher Low), LH (Lower High), LL (Lower Low)
    
    Args:
        df: OHLCV DataFrame
        lookback: Kaç mum geriye bakılacağı
        
    Returns:
        dict: swing_highs, swing_lows, current_structure
    """
    highs = df['High'].values
    lows = df['Low'].values
    closes = df['Close'].values
    
    swing_highs = []
    swing_lows = []
    
    for i in range(lookback, len(df) - lookback):
        # Swing High: Ortadaki mum, sağ ve soldaki N mumdan yüksek
        is_swing_high = all(highs[i] >= highs[i-j] for j in range(1, lookback+1)) and \
                        all(highs[i] >= highs[i+j] for j in range(1, lookback+1))
        
        # Swing Low: Ortadaki mum, sağ ve soldaki N mumdan düşük
        is_swing_low = all(lows[i] <= lows[i-j] for j in range(1, lookback+1)) and \
                       all(lows[i] <= lows[i+j] for j in range(1, lookback+1))
        
        if is_swing_high:
            swing_highs.append({'index': i, 'price': highs[i], 'date': df.index[i]})
        if is_swing_low:
            swing_lows.append({'index': i, 'price': lows[i], 'date': df.index[i]})
    
    # Son 2 swing point'i karşılaştırarak yapıyı belirle
    structure = "UNDEFINED"
    
    if len(swing_highs) >= 2 and len(swing_lows) >= 2:
        last_high = swing_highs[-1]['price']
        prev_high = swing_highs[-2]['price']
        last_low = swing_lows[-1]['price']
        prev_low = swing_lows[-2]['price']
        
        if last_high > prev_high and last_low > prev_low:
            structure = "UPTREND"  # HH + HL
        elif last_high < prev_high and last_low < prev_low:
            structure = "DOWNTREND"  # LH + LL
        else:
            structure = "CONSOLIDATION"  # Karışık
    
    return {
        'swing_highs': swing_highs,
        'swing_lows': swing_lows,
        'structure': structure,
        'last_hl': swing_lows[-1]['price'] if swing_lows else None,
        'last_lh': swing_highs[-1]['price'] if swing_highs else None
    }


def detect_choch(df, swing_data):
    """
    Change of Character (Karakter Değişimi) tespit eder.
    
    Yükseliş trendinde: Fiyat son HL'nin altına inerse → BEARISH CHoCH
    Düşüş trendinde: Fiyat son LH'nin üstüne çıkarsa → BULLISH CHoCH
    
    Returns:
        dict: choch_type, is_choch, message
    """
    if not swing_data or not swing_data['swing_lows'] or not swing_data['swing_highs']:
        return {'is_choch': False, 'choch_type': None, 'message': 'Yetersiz veri'}
    
    current_price = df['Close'].iloc[-1]
    structure = swing_data['structure']
    last_hl = swing_data['last_hl']
    last_lh = swing_data['last_lh']
    
    # Yükseliş trendinde düşüş CHoCH
    if structure == "UPTREND" and last_hl:
        if current_price < last_hl:
            return {
                'is_choch': True,
                'choch_type': 'BEARISH',
                'message': f'⚠️ CHoCH: Fiyat son HL ({last_hl:.2f}) altına indi. TREND BİTTİ!',
                'level': last_hl
            }
    
    # Düşüş trendinde yükseliş CHoCH
    if structure == "DOWNTREND" and last_lh:
        if current_price > last_lh:
            return {
                'is_choch': True,
                'choch_type': 'BULLISH',
                'message': f'✅ CHoCH: Fiyat son LH ({last_lh:.2f}) üstüne çıktı. TREND DÖNDÜ!',
                'level': last_lh
            }
    
    return {'is_choch': False, 'choch_type': None, 'message': 'CHoCH yok'}


def analyze_candle_wick(row):
    """
    Mum iğne analizi - Rejection sinyalleri için.
    
    - Üst iğne > 2x gövde → Satıcı reddi (BEARISH)
    - Alt iğne > 2x gövde → Alıcı reddi (BULLISH)
    
    Returns:
        dict: body, upper_wick, lower_wick, rejection_up, rejection_down, wick_ratio
    """
    open_price = row['Open']
    close_price = row['Close']
    high_price = row['High']
    low_price = row['Low']
    
    body = abs(close_price - open_price)
    upper_wick = high_price - max(open_price, close_price)
    lower_wick = min(open_price, close_price) - low_price
    
    # Minimum gövde eşiği (çok küçük gövdelerde oran yanıltıcı olabilir)
    min_body = body if body > 0.001 else 0.001
    
    return {
        'body': body,
        'upper_wick': upper_wick,
        'lower_wick': lower_wick,
        'upper_wick_ratio': upper_wick / min_body,
        'lower_wick_ratio': lower_wick / min_body,
        'rejection_up': lower_wick > (2 * body),  # Yukarı rejection (BULLISH)
        'rejection_down': upper_wick > (2 * body),  # Aşağı rejection (BEARISH)
        'is_doji': body < (high_price - low_price) * 0.1  # Gövde < %10 range = Doji
    }


def detect_buying_climax(row, vol_ratio, price_change_pct):
    """
    Buying Climax (Alım Çılgınlığı) tespit eder.
    Dağıtım işareti = ÇIKIŞ SİNYALİ
    
    Koşullar:
    - Hacim normalin 1.5x+ üstünde
    - Fiyat yükseliyor (pozitif değişim)
    - Uzun üst iğne (satıcı reddi)
    
    Bu, akıllı paranın elindeki malı küçük yatırımcıya devrettiği noktadır.
    """
    wick_data = analyze_candle_wick(row)
    
    is_climax = (
        vol_ratio > 1.5 and
        price_change_pct > 0 and
        wick_data['rejection_down']  # Üstten red = satıcılar bastırdı
    )
    
    strength = 0
    if is_climax:
        # Hacim ne kadar yüksekse sinyal o kadar güçlü
        strength = min(100, int(vol_ratio * 30 + wick_data['upper_wick_ratio'] * 10))
    
    return {
        'is_climax': is_climax,
        'strength': strength,
        'vol_ratio': vol_ratio,
        'wick_ratio': wick_data['upper_wick_ratio'],
        'message': '🔴 BUYING CLIMAX: Akıllı para dağıtıyor!' if is_climax else None
    }


def detect_stopping_volume(row, vol_ratio, price_change_pct, prev_closes):
    """
    Stopping Volume (Durduran Hacim) tespit eder.
    Birikim işareti = GİRİŞ SİNYALİ
    
    Koşullar:
    - Devasa hacim (2x+ ortalama)
    - Fiyat düşüşten sonra artık düşmüyor
    - Uzun alt iğne veya Doji (alıcı iradesi)
    
    Bu, büyük oyuncuların sessizce mal topladığı noktadır.
    """
    wick_data = analyze_candle_wick(row)
    
    # Son 5 günde düşüş var mı?
    was_falling = False
    if len(prev_closes) >= 5:
        was_falling = prev_closes[-1] < prev_closes[-5]  # 5 gün önceye göre düşmüş
    
    is_stopping = (
        vol_ratio > 2.0 and
        was_falling and
        (wick_data['rejection_up'] or wick_data['is_doji']) and
        abs(price_change_pct) < 1.0  # Fiyat fazla değişmedi (emilim)
    )
    
    strength = 0
    if is_stopping:
        strength = min(100, int(vol_ratio * 25 + wick_data['lower_wick_ratio'] * 15))
    
    return {
        'is_stopping': is_stopping,
        'strength': strength,
        'vol_ratio': vol_ratio,
        'wick_ratio': wick_data['lower_wick_ratio'],
        'message': '🟢 STOPPING VOLUME: Büyük oyuncular topluyor!' if is_stopping else None
    }


def analyze_effort_vs_result(vol_ratio, price_change_pct):
    """
    Çaba vs. Sonuç Analizi (Effort vs Result)
    
    Hacim yükseldi ama fiyat değişmedi = BİRİLERİ SESSIZCE POZİSYON DEĞİŞTİRİYOR
    
    - Hacim %50+ arttı (vol_ratio > 1.5)
    - Fiyat sadece %0.5'ten az değişti
    
    Bu uyumsuzluk, yaklaşan büyük bir hareketin habercisidir.
    """
    is_divergence = vol_ratio > 1.5 and abs(price_change_pct) < 0.5
    
    direction = None
    if is_divergence:
        # Yön tahmini: Fiyat yükseliyorsa dağıtım, düşüyorsa birikim olabilir
        if price_change_pct > 0:
            direction = "DISTRIBUTION"  # Yukarı gidiyor ama hacim emiliyor = Dağıtım
        else:
            direction = "ACCUMULATION"  # Aşağı gidiyor ama hacim emiliyor = Birikim
    
    return {
        'is_divergence': is_divergence,
        'direction': direction,
        'vol_ratio': vol_ratio,
        'price_change': price_change_pct,
        'message': f'⚡ ÇABA/SONUÇ: Hacim {vol_ratio:.1f}x ama fiyat sadece %{price_change_pct:.2f}' if is_divergence else None
    }


def detect_liquidity_sweep(df, lookback=3):
    """
    Liquidity Sweep (Likidite Avı) / Spring tespit eder.
    
    Spring (BULLISH):
    - Fiyat son N günün en düşüğünün altına sarkıp hemen geri döndü
    - Stop-loss avı yapılmış, yakıt toplandı
    - ÇOK GÜÇLÜ ALIŞ SİNYALİ
    
    Upthrust (BEARISH):
    - Fiyat son N günün en yükseğinin üstüne çıkıp geri döndü
    - Stop-loss avı yapılmış
    - SATIŞ SİNYALİ
    """
    if len(df) < lookback + 2:
        return {'is_sweep': False, 'sweep_type': None}
    
    current = df.iloc[-1]
    current_close = current['Close']
    current_low = current['Low']
    current_high = current['High']
    
    # Son N günün aralığı (bugün hariç)
    recent = df.iloc[-(lookback+1):-1]
    recent_low = recent['Low'].min()
    recent_high = recent['High'].max()
    
    # SPRING: Düşük kırıldı ama kapanış içeride
    is_spring = current_low < recent_low and current_close > recent_low
    
    # UPTHRUST: Yüksek kırıldı ama kapanış içeride
    is_upthrust = current_high > recent_high and current_close < recent_high
    
    if is_spring:
        sweep_depth = ((recent_low - current_low) / recent_low) * 100
        return {
            'is_sweep': True,
            'sweep_type': 'SPRING',
            'level': recent_low,
            'depth': sweep_depth,
            'message': f'🎯 SPRING: Likidite avı! Fiyat {recent_low:.2f} altına sarkıp döndü. GÜÇLÜ ALIŞ!'
        }
    
    if is_upthrust:
        sweep_depth = ((current_high - recent_high) / recent_high) * 100
        return {
            'is_sweep': True,
            'sweep_type': 'UPTHRUST',
            'level': recent_high,
            'depth': sweep_depth,
            'message': f'🎯 UPTHRUST: Likidite avı! Fiyat {recent_high:.2f} üstüne çıkıp döndü. SATIŞ!'
        }
    
    return {'is_sweep': False, 'sweep_type': None, 'message': None}


def check_structure_break(df, lookback=5):
    """
    Yapı Kontrolü - "Son N günün en düşüğünün altına sarktık mı?"
    
    Bu basit ama etkili filtre, trend kırılımlarını erken tespit eder.
    """
    if len(df) < lookback + 1:
        return {'is_broken': False, 'level': None}
    
    current_low = df['Low'].iloc[-1]
    recent_lows = df['Low'].iloc[-(lookback+1):-1]
    structure_level = recent_lows.min()
    
    is_broken = current_low < structure_level
    
    return {
        'is_broken': is_broken,
        'level': structure_level,
        'current_low': current_low,
        'message': f'⚠️ YAPI KIRILDI: Fiyat {structure_level:.2f} desteğinin altına indi!' if is_broken else None
    }


def calculate_wyckoff_score(data, df):
    """
    WYCKOFF & PRICE ACTION SKORLAMA SİSTEMİ
    
    Geleneksel indikatörler yerine 3 temel mantık kapısına dayanır:
    
    1. YAPI KONTROLÜ (Structure Check)
    2. ÇABA vs. SONUÇ (Effort vs Result) + VSA
    3. İĞNE ANALİZİ (Wick Analysis)
    
    BONUS: Spring, CHoCH, Buying Climax, Stopping Volume
    """
    base_score = 50
    score = 0
    reasons = []
    
    # Gerekli verileri al
    current_row = df.iloc[-1]
    vol_ratio = data.get('volume_ratio', 1.0)
    price_change = data.get('change_pct', 0)
    prev_closes = df['Close'].values[-10:] if len(df) >= 10 else df['Close'].values
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. MANTIК KAPISI: YAPI KONTROLÜ
    # ═══════════════════════════════════════════════════════════════════
    structure_check = check_structure_break(df, lookback=3)
    if structure_check['is_broken']:
        score -= 30
        reasons.append("⚠️ Yapı Kırıldı (Risk)")
    
    # ═══════════════════════════════════════════════════════════════════
    # 2. MANTIК KAPISI: ÇABA vs. SONUÇ
    # ═══════════════════════════════════════════════════════════════════
    effort_result = analyze_effort_vs_result(vol_ratio, price_change)
    if effort_result['is_divergence']:
        if effort_result['direction'] == "ACCUMULATION":
            score += 15
            reasons.append("⚡ Gizli Birikim")
        elif effort_result['direction'] == "DISTRIBUTION":
            score -= 20
            reasons.append("⚡ Gizli Dağıtım")
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. MANTIК KAPISI: İĞNE ANALİZİ
    # ═══════════════════════════════════════════════════════════════════
    wick_data = analyze_candle_wick(current_row)
    
    if wick_data['rejection_up']:  # Alt iğne = Alıcı tepkisi
        score += 25
        reasons.append("📍 Güçlü Alt İğne (Alıcı Reddi)")
    
    if wick_data['rejection_down']:  # Üst iğne = Satıcı tepkisi
        score -= 25
        reasons.append("📍 Güçlü Üst İğne (Satıcı Reddi)")
    
    # ═══════════════════════════════════════════════════════════════════
    # BONUS SİNYALLER
    # ═══════════════════════════════════════════════════════════════════
    
    # Spring (Likidite Avı - GÜÇLÜ AL)
    liquidity_sweep = detect_liquidity_sweep(df, lookback=3)
    if liquidity_sweep['is_sweep']:
        if liquidity_sweep['sweep_type'] == 'SPRING':
            score += 40
            reasons.append("🎯 Spring: Likidite Avı Tamamlandı!")
        elif liquidity_sweep['sweep_type'] == 'UPTHRUST':
            score -= 40
            reasons.append("🎯 Upthrust: Satış Baskısı!")
    
    # Buying Climax (ÇIKIŞ SİNYALİ)
    buying_climax = detect_buying_climax(current_row, vol_ratio, price_change)
    if buying_climax['is_climax']:
        score -= 40
        reasons.append("🔴 Alım Çılgınlığı (Dağıtım)")
    
    # Stopping Volume (GİRİŞ SİNYALİ)
    stopping_vol = detect_stopping_volume(current_row, vol_ratio, price_change, prev_closes)
    if stopping_vol['is_stopping']:
        score += 35
        reasons.append("🟢 Durduran Hacim (Birikim)")
    
    # CHoCH (Change of Character)
    swing_data = detect_swing_points(df, lookback=5)
    choch = detect_choch(df, swing_data)
    
    if choch['is_choch']:
        if choch['choch_type'] == 'BEARISH':
            score -= 50
            reasons.append("❌ CHoCH: Trend Sona Erdi!")
        elif choch['choch_type'] == 'BULLISH':
            score += 35
            reasons.append("✅ CHoCH: Trend Dönüşü!")
    
    # Market Structure Bonus
    if swing_data['structure'] == 'UPTREND':
        score += 10
        reasons.append("📈 Yapı: Yükseliş Trendi")
    elif swing_data['structure'] == 'DOWNTREND':
        score -= 15
        reasons.append("📉 Yapı: Düşüş Trendi")
    
    # ═══════════════════════════════════════════════════════════════════
    # TEMEL TREND FİLTRELERİ (Güvenlik Ağı)
    # ═══════════════════════════════════════════════════════════════════
    ema50 = data.get('ema50', 0)
    ema200 = data.get('ema200', 0)
    price = data.get('price', 0)
    
    # Altın Çapraz kontrolü
    if ema50 > 0 and ema200 > 0:
        if ema50 > ema200 and price > ema50:
            score += 10
        elif ema50 < ema200 and price < ema50:
            score -= 10
    
    # RSI Aşırı Alım Cezası
    rsi = data.get('rsi', 50)
    if rsi > 75:
        score -= 20
        reasons.append("⚠️ RSI Aşırı Alım (>75)")
    elif rsi > 70:
        score -= 10
        reasons.append("⚠️ RSI Dikkat (>70)")
    
    # Final skor hesaplama
    final_score = base_score + max(-50, min(50, score))
    
    return int(final_score), reasons, {
        'structure': swing_data['structure'],
        'choch': choch,
        'liquidity_sweep': liquidity_sweep,
        'wick_analysis': wick_data
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3.7 BACKTEST MOTORU
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def run_robust_backtest(df, atr_mult=3.0, tp_ratio=0, rsi_limit=75):
    """
    rsi_limit parametresi eklendi.
    Artık sembol yerine DataFrame (df) alıyor.
    """
    try:
        # 1. Veri Kontrolü
        if df is None or df.empty or len(df) < 200: return None
        
        # DataFrame'i kopyala (orijinali bozmamak için)
        df = df.copy()
        
        # ─── İndikatör Hesaplamaları ───
        closes = df['Close']
        highs = df['High']
        lows = df['Low']
        volumes = df['Volume']

        # EMA & Trend
        df['EMA200'] = closes.ewm(span=200, adjust=False).mean()
        df['EMA50'] = closes.ewm(span=50, adjust=False).mean()
        df['SMA50'] = closes.rolling(window=50).mean() # YENİ
        
        # Değişim
        df['Change_Pct'] = closes.pct_change() * 100 # YENİ

        # RSI
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # ATR (Volatilite ve Stop için)
        high_low = highs - lows
        high_close = np.abs(highs - closes.shift())
        low_close = np.abs(lows - closes.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=14).mean()

        # Bollinger Bands (YENİ)
        bb_mid = closes.rolling(window=20).mean()
        bb_std = closes.rolling(window=20).std()
        df['BB_Upper'] = bb_mid + (bb_std * 2)
        df['BB_Lower'] = bb_mid - (bb_std * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / bb_mid * 100

        # Volume Ratio (YENİ)
        vol_sma20 = volumes.rolling(window=20).mean()
        df['Volume_Ratio'] = volumes / vol_sma20

        # CMF (YENİ)
        mfv = ((closes - lows) - (highs - closes)) / (highs - lows)
        mfv = mfv.fillna(0)
        volume_mfv = mfv * volumes
        df['CMF'] = volume_mfv.rolling(20).sum() / volumes.rolling(20).sum()

        # ICHIMOKU
        # Conversion Line (Tenkan)
        nine_period_high = highs.rolling(window=9).max()
        nine_period_low = lows.rolling(window=9).min()
        df['Tenkan'] = (nine_period_high + nine_period_low) / 2
        # Base Line (Kijun)
        period26_high = highs.rolling(window=26).max()
        period26_low = lows.rolling(window=26).min()
        df['Kijun'] = (period26_high + period26_low) / 2
        # Span A & B (Geleceğe Shift edilmiş)
        df['SpanA'] = ((df['Tenkan'] + df['Kijun']) / 2).shift(26)
        period52_high = highs.rolling(window=52).max()
        period52_low = lows.rolling(window=52).min()
        df['SpanB'] = ((period52_high + period52_low) / 2).shift(26)
        
        # ADX
        plus_dm = highs.diff()
        minus_dm = lows.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        tr14 = tr.rolling(window=14).sum()
        plus_di = 100 * (plus_dm.rolling(window=14).sum() / tr14)
        minus_di = 100 * (np.abs(minus_dm).rolling(window=14).sum() / tr14)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df['ADX'] = dx.rolling(window=14).mean()

        df = df.dropna()
        
        # 2. Simülasyon Değişkenleri
        initial_capital = 10000
        cash = initial_capital
        position = 0
        commission = 0.001 
        
        in_position = False
        trades_count = 0
        wins = 0
        
        # İşlem geçmişi (Grafik için)
        trades = []
        current_entry_date = None
        
        # Hız için numpy dizileri
        v_opens = df['Open'].values
        v_closes = df['Close'].values
        v_highs = df['High'].values
        v_lows = df['Low'].values
        
        # İndikatörler (Numpy)
        v_ema50 = df['EMA50'].values
        v_ema200 = df['EMA200'].values
        v_sma50 = df['SMA50'].values
        v_rsi = df['RSI'].values
        v_adx = df['ADX'].values
        v_cmf = df['CMF'].values
        v_atr = df['ATR'].values
        v_span_a = df['SpanA'].values
        v_span_b = df['SpanB'].values
        v_bb_upper = df['BB_Upper'].values
        v_bb_lower = df['BB_Lower'].values
        v_bb_width = df['BB_Width'].values
        v_vol_ratio = df['Volume_Ratio'].values
        v_change = df['Change_Pct'].values

        
        # Stop Takibi ve Kar Al
        trailing_stop_price = 0
        take_profit_price = 0
        entry_price = 0
        partial_exit_done = False  # Kademeli kâr alma için
        original_position = 0  # İlk pozisyon büyüklüğü
        
        # ─── BIST'E ÖZEL ÇIKIŞ STRATEJİLERİ ───
        # Endeks korelasyonu için XU100 verisi
        index_data = get_index_data()
        index_is_strong = index_data['is_strong'] if index_data else True  # Varsayılan güçlü
        
        # ATR Bazlı Volatilite Stopu (2x ATR)
        volatility_stop_mult = 2.0  # Sabit % yerine dinamik ATR
        
        for i in range(len(df) - 1):
            current_close = v_closes[i]
            
            # ─── ÇIKIŞ MANTIĞI ───
            if in_position:
                # 0. BREAKEVEN MEKANİZMASI (1 ATR kârda maliyet fiyatına çek)
                if current_close >= entry_price + (1.0 * v_atr[i]):
                    trailing_stop_price = max(trailing_stop_price, entry_price)  # Cost stop
                
                # 1. KADEMELİ KAR AL (İlk hedefte %50 pozisyon kapat)
                if tp_ratio > 0 and not partial_exit_done and v_highs[i] >= take_profit_price:
                    exit_price = take_profit_price
                    partial_size = position * 0.5  # %50'sini sat
                    cash += partial_size * exit_price * (1 - commission)
                    position = position - partial_size  # Kalan %50
                    partial_exit_done = True
                    # Breakeven'a çek (kalan pozisyon için)
                    trailing_stop_price = max(trailing_stop_price, entry_price)
                    # İkinci hedef belirle (2x TP)
                    take_profit_price = entry_price + (atr_mult * v_atr[i] * tp_ratio * 2)
                    # Kayıt (kısmi çıkış)
                    trades.append({
                        'type': 'partial_exit',
                        'date': df.index[i],
                        'price': exit_price,
                        'profit': True
                    })
                    continue
                
                # 2. TAM KAR AL (İkinci hedef - kalan pozisyon)
                if tp_ratio > 0 and partial_exit_done and v_highs[i] >= take_profit_price:
                    exit_price = take_profit_price
                    cash += position * exit_price * (1 - commission)
                    wins += 1
                    trades.append({
                        'type': 'exit',
                        'date': df.index[i],
                        'price': exit_price,
                        'profit': True
                    })
                    position = 0
                    in_position = False
                    partial_exit_done = False
                    continue

                # 3. Stop Kontrolü (Trailing)
                if v_lows[i] < trailing_stop_price:
                    exit_price = trailing_stop_price
                    if v_opens[i] < trailing_stop_price: exit_price = v_opens[i] 
                    
                    cash += position * exit_price * (1 - commission)
                    is_profit = exit_price > entry_price
                    if is_profit or partial_exit_done: wins += 1  # Kısmi kar alındıysa kazanç say
                    trades.append({
                        'type': 'exit',
                        'date': df.index[i],
                        'price': exit_price,
                        'profit': is_profit
                    })
                    position = 0
                    in_position = False
                    partial_exit_done = False
                    continue
                
                # 4. Stop Güncelleme (Trailing - ATR Bazlı)
                # BIST volatilite yapısına uyum: 2x ATR kullan
                new_stop = current_close - (volatility_stop_mult * v_atr[i])
                if new_stop > trailing_stop_price:
                    trailing_stop_price = new_stop

                # 4.5 BIST ENDEKS KORELASYONU ÇIKIŞI
                # Teknik SAT sinyali geldi ama endeks güçlüyse %25 pozisyon koru
                # RSI > 70 ve Fiyat dirençte = teknik SAT sinyali
                is_technical_sell = (v_rsi[i] > 70) and (current_close >= v_bb_upper[i])
                
                if is_technical_sell and index_is_strong and not partial_exit_done:
                    # Sadece %75'ini sat, %25'ini tut
                    exit_price = current_close
                    partial_size = position * 0.75
                    cash += partial_size * exit_price * (1 - commission)
                    position = position - partial_size  # Kalan %25
                    partial_exit_done = True
                    # Breakeven'a çek
                    trailing_stop_price = max(trailing_stop_price, entry_price)
                    trades.append({
                        'type': 'partial_exit',
                        'date': df.index[i],
                        'price': exit_price,
                        'profit': True,
                        'reason': 'index_correlation'
                    })
                    continue

                # 5. Acil Çıkış (Trend Çöküşü - %5 eşik)
                if current_close < v_ema200[i] * 0.95:  # %3 -> %5'e gevşetildi
                    exit_price = current_close
                    cash += position * exit_price * (1 - commission)
                    is_profit = exit_price > entry_price
                    if is_profit or partial_exit_done: wins += 1
                    trades.append({
                        'type': 'exit',
                        'date': df.index[i],
                        'price': exit_price,
                        'profit': is_profit
                    })
                    position = 0
                    in_position = False
                    partial_exit_done = False
                    continue

            # ─── GİRİŞ MANTIĞI (WYCKOFF ENTEGRE) ───
            if not in_position:
                # Veri sözlüğünü hazırla (Scalar değerler)
                row_data = {
                    'price': current_close,
                    'ema50': v_ema50[i],
                    'ema200': v_ema200[i],
                    'sma50': v_sma50[i],
                    'rsi': v_rsi[i],
                    'adx': v_adx[i],
                    'cmf': v_cmf[i],
                    'volume_ratio': v_vol_ratio[i],
                    'bb_upper': v_bb_upper[i],
                    'bb_lower': v_bb_lower[i],
                    'bb_width': v_bb_width[i],
                    'span_a': v_span_a[i],
                    'span_b': v_span_b[i],
                    'change_pct': v_change[i],
                    'divergence': 'YOK'
                }
                
                # WYCKOFF SKORLAMASI (DataFrame'in son N satırını kullan)
                lookback_window = min(i + 1, 60)  # En fazla 60 gün geriye bak
                df_slice = df.iloc[max(0, i - lookback_window + 1):i + 1].copy()
                
                if len(df_slice) >= 20:
                    score, _, _ = calculate_wyckoff_score(row_data, df_slice)
                else:
                    # Yeterli veri yoksa eski sistemi kullan
                    score, _ = calculate_decision_score(row_data, weekly_data=None, rsi_limit=rsi_limit)
                
                # ─── GİRİŞ FİLTRELERİ ───
                # 1. TREND FİLTRESİ: EMA50 > EMA200 ve Fiyat > EMA50 olmalı
                is_bullish_trend = v_ema50[i] > v_ema200[i] and current_close > v_ema50[i]
                
                # 2. RSI AŞIRI ALIM KONTROLÜ: RSI 75'in altında olmalı
                is_not_overbought = v_rsi[i] < 75
                
                # 3. HACİM DOĞRULAMASI: Hacim ortalamanın üstünde olmalı
                has_volume = v_vol_ratio[i] > 0.8
                
                # ALIM EŞİĞİ (Tüm filtreler geçmeli)
                if score >= 60 and is_bullish_trend and is_not_overbought and has_volume:
                    entry_price = v_opens[i+1]
                    current_entry_date = df.index[i+1]
                    size = cash / entry_price
                    cost = size * entry_price * (1 + commission)
                    cash -= cost
                    position = size
                    original_position = size  # Orijinal pozisyon kaydet
                    in_position = True
                    trades_count += 1
                    partial_exit_done = False  # Reset
                    trades.append({
                        'type': 'entry',
                        'date': current_entry_date,
                        'price': entry_price
                    })
                    
                    # Stop ve TP Belirleme
                    risk = atr_mult * v_atr[i]
                    trailing_stop_price = entry_price - risk
                    
                    if tp_ratio > 0:
                        take_profit_price = entry_price + (risk * tp_ratio)  # İlk hedef
                    else:
                        take_profit_price = 999999
                
        final_value = cash + (position * v_closes[-1] if in_position else 0)
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        win_rate = (wins / trades_count * 100) if trades_count > 0 else 0

        return {
            "total_pnl": total_return,
            "total_trades": trades_count,
            "win_rate": win_rate,
            "final_equity": final_value,
            "trades": trades
        }
    except Exception as e:
        return {"error": str(e)}

def optimize_strategy_robust(symbol):
    """
    Gelişmiş Grid Search:
    Hem Çıkış (ATR Stop) hem de Giriş (RSI Limiti) ayarlarını optimize eder.
    Veriyi tek seferde indirir.
    """
    try:
        # Veriyi burada sadece 1 kere indiriyoruz
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2y")
        
        if df.empty or len(df) < 200:
            return {'atr_multiplier': 2.5, 'take_profit_ratio': 2.0, 'rsi_limit': 75}

        # Taranacak parametreler
        # rsi_limit: 75 (Güvenli) vs 85 (Ralli/Agresif)
        param_grid = {
            'atr_multiplier': [2.0, 3.0], 
            'take_profit_ratio': [2.0, 3.0],
            'rsi_limit': [75, 85]  # Agresif mod eklendi
        }
        
        best_score = -9999
        # Varsayılan (Güvenli) ayarlar
        best_params = {
            'atr_multiplier': 2.5, 
            'take_profit_ratio': 2.0,
            'rsi_limit': 75
        }

        # Tüm kombinasyonları dene
        for atr_mult in param_grid['atr_multiplier']:
            for tp_ratio in param_grid['take_profit_ratio']:
                for rsi_lim in param_grid['rsi_limit']:
                    
                    # Artık sembol değil, indirilmiş df'i gönderiyoruz
                    result = run_robust_backtest(
                        df, 
                        atr_mult=atr_mult, 
                        tp_ratio=tp_ratio,
                        rsi_limit=rsi_lim
                    )
                    
                    if result and 'total_pnl' in result:
                        # PNL yüksekse ve en az 3 işlem yapmışsa seç
                        if result['total_trades'] >= 3:
                            score = result['total_pnl']
                            if score > best_score:
                                best_score = score
                                best_params = {
                                    'atr_multiplier': atr_mult,
                                    'take_profit_ratio': tp_ratio,
                                    'rsi_limit': rsi_lim
                                }
                            
        return best_params
    except Exception as e:
        return {'atr_multiplier': 2.5, 'take_profit_ratio': 2.0, 'rsi_limit': 75}

# ═══════════════════════════════════════════════════════════════════════════════
# 4. SİNYAL SKOR HESAPLAMA
# ═══════════════════════════════════════════════════════════════════════════════
def calculate_decision_score(data, weekly_data=None, rsi_limit=75, indicator_dna=None):
    """
    Dinamik ağırlıklı karar skorlama fonksiyonu.
    
    Args:
        data: Hisse teknik verileri
        weekly_data: Haftalık trend verileri
        rsi_limit: 75 (Muhafazakar) veya 85 (Agresif/Ralli Modu)
        indicator_dna: Hissenin indikatör başarı analizi (analyze_indicator_dna'dan)
    """
    base_score = 50
    score = 0
    reasons = []
    
    def get_val(key, default=0):
        val = data.get(key, default)
        return val if pd.notna(val) else default
    
    # ─── REJİM TESPİTİ (ADX Bazlı Dinamik Ağırlıklar) ───
    adx = get_val('adx')
    regime, osc_mult, trend_mult = detect_market_regime(adx)
    
    # ─── DİNAMİK KATSAYILAR ───
    # DNA varsa hisse-spesifik ağırlıkları kullan
    if indicator_dna:
        W_TREND = 1.0 * trend_mult * indicator_dna.get('trend_weight', 1.0)
        W_MOMENTUM = 2.0 * osc_mult * indicator_dna.get('momentum_weight', 1.0)
        W_VOLUME = 1.5 * indicator_dna.get('volume_weight', 1.0)
        W_PATTERN = 1.5
        reasons.append(f"Rejim: {regime}")
    else:
        # Sadece rejim bazlı ağırlıklar
        W_TREND = 1.0 * trend_mult
        W_MOMENTUM = 2.0 * osc_mult
        W_VOLUME = 1.5
        W_PATTERN = 1.5
        
    price = get_val('price')
    span_a = get_val('span_a')
    span_b = get_val('span_b')
    ema50 = get_val('ema50')
    ema200 = get_val('ema200')
    sma50 = get_val('sma50')
    rsi = get_val('rsi', 50)
    adx = get_val('adx')
    cmf = get_val('cmf')
    vol_ratio = get_val('volume_ratio')
    bb_width = get_val('bb_width', 10)
    bb_upper = get_val('bb_upper')
    
    # ─── EXTRA HESAPLAMALAR ───
    dist_to_ema50 = 0
    if ema50 > 0:
        dist_to_ema50 = ((price - ema50) / ema50) * 100
    
    # 1. TIER: TREND ANALİZİ
    trend_score = 0
    cloud_top = max(span_a, span_b)
    cloud_bottom = min(span_a, span_b)
    
    is_above_cloud = price > cloud_top if cloud_top > 0 else False
    is_below_cloud = price < cloud_bottom if cloud_bottom > 0 else False
    
    if is_above_cloud:
        trend_score += 15
        reasons.append("Fiyat Bulut Üstünde")
    elif is_below_cloud:
        trend_score -= 15
    
    if ema50 > ema200:
        if price > ema50: trend_score += 10
        elif price < ema50: trend_score += 5
    else:
        trend_score -= 10

    if weekly_data and weekly_data.get('ema_cross') == "BOĞA":
        trend_score += 10
    elif weekly_data: 
        trend_score -= 10

    # UZAMA CEZASI (Gevşetildi: %15)
    if dist_to_ema50 > 15:  
        trend_score -= 25  
        reasons.append("EMA50'den Çok Uzak")

    # 2. TIER: MOMENTUM
    mom_score = 0
    if rsi > 50 and is_above_cloud: mom_score += 5
    elif rsi < 50 and is_below_cloud: mom_score -= 5
    
    div = data.get('divergence', 'YOK')
    if div == "NEGATİF":
        mom_score -= 30
        reasons.append("Negatif Uyumsuzluk")
    elif div == "POZİTİF":
        mom_score += 25
        reasons.append("Pozitif Uyumsuzluk")
        
    if price > sma50 and rsi < 45:
        mom_score += 25
        reasons.append("Trend İçi Fırsat")
    
    # 3. TIER: HACİM
    vol_score = 0
    if cmf > 0.10:
        vol_score += 15
        reasons.append("Balina Girişi")
    elif cmf < -0.10:
        vol_score -= 15
        
    if vol_ratio > 2.0 and get_val('change_pct') > 0:
        vol_score += 10
        reasons.append("Hacim Patlaması")

    # 4. TIER: FORMASYON
    pat_score = 0
    if bb_width < 8:
        pat_score += 5
        if trend_score > 0 and vol_score > 0:
            pat_score += 20
            reasons.append("Sıkışma Kırılımı")

    # Hesaplama
    final_raw = (trend_score * W_TREND) + (mom_score * W_MOMENTUM) + \
                (vol_score * W_VOLUME) + (pat_score * W_PATTERN)
                
    normalized_score = base_score + max(-50, min(50, final_raw))
    
    # ─── AKILLI LİMİT (Optimized Cap Rules) ───
    # Robotun rsi_limit ayarına göre fren yapması sağlanır
    
    if rsi > (rsi_limit + 5): # Örn: Limit 85 ise 90'da durur
        normalized_score = min(normalized_score, 50)
        reasons.append(f"RSI > {rsi_limit+5} (Aşırı Isınma)")
    elif rsi > rsi_limit:     # Örn: Limit 85 ise 85'e kadar AL verir
        normalized_score = min(normalized_score, 60)
        reasons.append(f"RSI > {rsi_limit} (Dikkat)")
    
    # Haftalık ayı ise asla AL verme
    if weekly_data and weekly_data.get('ema_cross') == "AYI":
        normalized_score = min(normalized_score, 55)
        reasons.append("Haftalık Trend AYI")
        
    return int(normalized_score), reasons

def calculate_smart_score(data, weekly_data=None, atr_mult=None, tp_ratio=None, rsi_limit=75, indicator_dna=None, df=None, indicator_scores=None):
    """
    Akıllı skor hesaplama fonksiyonu - ADAPTİF KONSENSÜS ENTEGRE.
    
    Args:
        data: Hisse teknik verileri
        weekly_data: Haftalık trend verileri
        atr_mult: ATR çarpanı (stop-loss için)
        tp_ratio: Take-profit oranı
        rsi_limit: RSI limiti
        indicator_dna: Hissenin DNA analizi (eski sistem)
        df: DataFrame (Wyckoff analizi için gerekli)
        indicator_scores: Yeni adaptif sistem - calculate_indicator_confidence_scores çıktısı
    """
    active_indicators = []
    
    # ═══════════════════════════════════════════════════════════════════
    # YENİ ADAPTİF KONSENSÜS SİSTEMİ
    # ═══════════════════════════════════════════════════════════════════
    if indicator_scores:
        # Yeni sistem: Sadece kanıtlanmış indikatörlerin oy birliği ile karar ver
        score, reasons, active_indicators = generate_adaptive_signal(data, indicator_scores)
        
        # Wyckoff ile hibrit kontrol (opsiyonel güçlendirme)
        if df is not None and len(df) >= 20:
            wyckoff_score, wyckoff_reasons, wyckoff_data = calculate_wyckoff_score(data, df)
            
            # Wyckoff yapı bilgisini ekle
            if wyckoff_data.get('structure') == 'UPTREND':
                score = min(100, score + 5)
                reasons.append("📈 Wyckoff: Yükseliş Yapısı")
            elif wyckoff_data.get('structure') == 'DOWNTREND':
                score = max(0, score - 10)
                reasons.append("📉 Wyckoff: Düşüş Yapısı")
                
            # Spring veya CHoCH varsa bonus
            if wyckoff_data.get('liquidity_sweep', {}).get('sweep_type') == 'SPRING':
                score = min(100, score + 10)
                reasons.append("🎯 Spring Tespit!")
            if wyckoff_data.get('choch', {}).get('choch_type') == 'BULLISH':
                score = min(100, score + 10)
                reasons.append("✅ CHoCH: Trend Dönüşü!")
    
    # ═══════════════════════════════════════════════════════════════════
    # WYCKOFF SKORLAMASI (Adaptif sistem yoksa)
    # ═══════════════════════════════════════════════════════════════════
    elif df is not None and len(df) >= 20:
        score, reasons, wyckoff_data = calculate_wyckoff_score(data, df)
        
        # Wyckoff verisini reasons'a ekle
        if wyckoff_data.get('structure'):
            reasons.insert(0, f"📊 Yapı: {wyckoff_data['structure']}")
    
    # ═══════════════════════════════════════════════════════════════════
    # ESKİ SİSTEM (Geriye uyumluluk)
    # ═══════════════════════════════════════════════════════════════════
    else:
        score, reasons = calculate_decision_score(data, weekly_data, rsi_limit=rsi_limit, indicator_dna=indicator_dna)
    
    # Renk ve Etiket
    if score >= 80:
        signal, color = "GÜÇLÜ AL", "#10b981"
    elif score >= 60:
        signal, color = "AL", "#34d399"
    elif score <= 20:
        signal, color = "GÜÇLÜ SAT", "#ef4444"
    elif score <= 40:
        signal, color = "SAT", "#f87171"
    else:
        signal, color = "BEKLE", "#fbbf24"
        
    # Risk Yönetimi
    atr = data['atr']
    price = data['price']
    
    # Eğer optimize edilmiş parametre gelmediyse varsayılanları kullan
    if atr_mult is None:
        atr_mult = 2.5 if data['adx'] > 30 else 2.0
        
    stop_loss = price - (atr_mult * atr)
    
    # Take Profit hesaplama
    if tp_ratio is None:
         # Varsayılan TP mantığı
         tp1 = price + (atr_mult * 1.5 * atr)
         tp2 = price + (atr_mult * 3.0 * atr)
    else:
         tp1 = price + (atr * atr_mult * tp_ratio) # Optimize edilmiş TP
         tp2 = price + (atr * atr_mult * tp_ratio * 1.5) # İkinci hedef biraz daha yukarıda

    risk_levels = {
        "stop_loss": stop_loss,
        "take_profit_1": tp1,
        "take_profit_2": tp2,
        "risk_reward": tp_ratio if tp_ratio else 1.5,
        "active_indicators": active_indicators  # Yeni: Aktif indikatör listesi
    }

    return score, signal, color, reasons, risk_levels

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
def create_analysis_chart(data, trades=None):
    """Multi-panel gelişmiş analiz grafiği - İşlem noktaları dahil"""
    df = data['df'].tail(120)  # Son 120 gün
    chart_start_date = df.index[0]
    
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
    
    # ─── İŞLEM NOKTALARI (TRADES) ───
    if trades and len(trades) > 0:
        # Grafik tarih aralığında olan işlemleri filtrele
        visible_trades = [t for t in trades if t['date'] >= chart_start_date]
        
        # Alım noktaları (Yeşil üçgen yukarı)
        entries = [t for t in visible_trades if t['type'] == 'entry']
        if entries:
            entry_dates = [t['date'] for t in entries]
            entry_prices = [t['price'] for t in entries]
            
            fig.add_trace(go.Scatter(
                x=entry_dates,
                y=entry_prices,
                mode='markers',
                marker=dict(
                    symbol='triangle-up',
                    size=14,
                    color='#10b981',
                    line=dict(width=1, color='white')
                ),
                name='Alım',
                hovertemplate='<b>ALIŞ</b><br>Tarih: %{x}<br>Fiyat: %{y:.2f} ₺<extra></extra>'
            ), row=1, col=1)
        
        # Satış noktaları (Renk kâr/zarara göre)
        exits = [t for t in visible_trades if t['type'] == 'exit']
        if exits:
            # Kârlı ve zararlı satışları ayır
            profit_exits = [t for t in exits if t.get('profit', False)]
            loss_exits = [t for t in exits if not t.get('profit', False)]
            
            # Kârlı satışlar (Yeşil)
            if profit_exits:
                fig.add_trace(go.Scatter(
                    x=[t['date'] for t in profit_exits],
                    y=[t['price'] for t in profit_exits],
                    mode='markers',
                    marker=dict(
                        symbol='triangle-down',
                        size=14,
                        color='#10b981',
                        line=dict(width=1, color='white')
                    ),
                    name='Kârlı Satış',
                    hovertemplate='<b>SATIŞ (KÂR)</b><br>Tarih: %{x}<br>Fiyat: %{y:.2f} ₺<extra></extra>'
                ), row=1, col=1)
            
            # Zararlı satışlar (Kırmızı)
            if loss_exits:
                fig.add_trace(go.Scatter(
                    x=[t['date'] for t in loss_exits],
                    y=[t['price'] for t in loss_exits],
                    mode='markers',
                    marker=dict(
                        symbol='triangle-down',
                        size=14,
                        color='#ef4444',
                        line=dict(width=1, color='white')
                    ),
                    name='Zararlı Satış',
                    hovertemplate='<b>SATIŞ (ZARAR)</b><br>Tarih: %{x}<br>Fiyat: %{y:.2f} ₺<extra></extra>'
                ), row=1, col=1)
        
        # ─── ENTRY-EXIT BAĞLANTI ÇİZGİLERİ ───
        # Entry-Exit çiftlerini eşleştir ve çizgi çiz
        i = 0
        while i < len(visible_trades) - 1:
            if visible_trades[i]['type'] == 'entry' and visible_trades[i+1]['type'] == 'exit':
                entry_t = visible_trades[i]
                exit_t = visible_trades[i+1]
                line_color = '#10b981' if exit_t.get('profit', False) else '#ef4444'
                
                fig.add_trace(go.Scatter(
                    x=[entry_t['date'], exit_t['date']],
                    y=[entry_t['price'], exit_t['price']],
                    mode='lines',
                    line=dict(color=line_color, width=1, dash='dot'),
                    showlegend=False,
                    hoverinfo='skip'
                ), row=1, col=1)
                i += 2
            else:
                i += 1
    
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
    except Exception as e:
        st.error(f"Tarama Hatası ({symbol}): {str(e)}")
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
        
        # Her hisseden sonra bekleme (Rate Limit engellemek için)
        time.sleep(0.5)
    
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
        with st.spinner("Yapay zeka verileri işliyor ve Adaptif DNA analizi yapıyor..."):
            data = get_advanced_data(target_symbol.upper().strip())
            weekly_data = get_weekly_trend(target_symbol.upper().strip())
            
            # YENİ: ADAPTİF DNA ANALİZİ (22 İndikatörü Ayrı Ayrı Backtest Et)
            indicator_scores = calculate_indicator_confidence_scores(target_symbol.upper().strip())
            
            # Geriye uyumluluk için eski format
            indicator_dna = analyze_indicator_dna(target_symbol.upper().strip())
            
            # ÖNCE OPTİMİZASYON YAP
            best_params = optimize_strategy_robust(target_symbol.upper().strip())
            
            # SONRA BU PARAMETRELERLE BACKTEST ÇALIŞTIR
            # run_robust_backtest artık df istiyor, bu yüzden indiriyoruz
            ticker_bt = yf.Ticker(target_symbol.upper().strip())
            df_bt = ticker_bt.history(period="2y")
            
            backtest_results = run_robust_backtest(
                df_bt, 
                atr_mult=best_params['atr_multiplier'],
                tp_ratio=best_params['take_profit_ratio'],
                rsi_limit=best_params['rsi_limit'] # YENİ
            )
        
        if data:
            # YENİ: Piyasa Rejimi Tespiti
            regime, osc_mult, trend_mult = detect_market_regime(data.get('adx', 20))
            
            # ═══ SİNYAL SKORU (ADAPTİF KONSENSÜS SİSTEMİ) ═══
            # Yeni sistem: 22 indikatörün oy birliği ile karar ver
            score, signal, signal_color, reasons, risk_levels = calculate_smart_score(
                data, 
                weekly_data, 
                atr_mult=best_params['atr_multiplier'],
                tp_ratio=best_params['take_profit_ratio'],
                rsi_limit=best_params['rsi_limit'],
                indicator_dna=indicator_dna,
                df=data['df'],
                indicator_scores=indicator_scores  # YENİ: Adaptif sistem
            )
            
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
            
            # ═══ PİYASA REJİMİ & İNDİKATÖR DNA ═══
            st.markdown('<div class="section-title">Piyasa Rejimi & İndikatör DNA</div>', unsafe_allow_html=True)
            
            reg_col1, reg_col2 = st.columns([1, 2])
            
            with reg_col1:
                # Rejim renkleri
                regime_colors = {
                    "RANGE": "#fbbf24",      # Sarı - Yatay
                    "TRANSITION": "#60a5fa", # Mavi - Geçiş
                    "TREND": "#10b981"       # Yeşil - Trend
                }
                regime_labels = {
                    "RANGE": "📊 YATAY PİYASA",
                    "TRANSITION": "⚖️ GEÇİŞ",
                    "TREND": "📈 TREND"
                }
                regime_desc = {
                    "RANGE": "RSI ve Stokastik odaklı",
                    "TRANSITION": "Dengeli yaklaşım",
                    "TREND": "EMA ve MACD odaklı"
                }
                
                regime_color = regime_colors.get(regime, "#60a5fa")
                st.markdown(f'''
<div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 1rem; text-align: center;">
<div style="font-size: 0.65rem; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 1px;">Piyasa Rejimi</div>
<div style="font-size: 1.5rem; color: {regime_color}; font-weight: 700; margin: 0.5rem 0;">{regime_labels.get(regime, regime)}</div>
<div style="font-size: 0.7rem; color: rgba(255,255,255,0.5);">ADX: {data.get('adx', 0):.1f}</div>
<div style="font-size: 0.65rem; color: rgba(255,255,255,0.35); margin-top: 0.25rem;">{regime_desc.get(regime, "")}</div>
</div>
''', unsafe_allow_html=True)
            
            with reg_col2:
                # ADAPTİF DNA SONUÇLARI (Yeni Sistem)
                if indicator_scores:
                    active_count = sum(1 for i in indicator_scores.values() if i['active'])
                    total_count = len(indicator_scores)
                    buy_count = sum(1 for i in indicator_scores.values() if i['active'] and i['current_signal'] == 'AL')
                    
                    # En iyi 5 aktif indikatörü göster
                    active_list = sorted(
                        [(k, v) for k, v in indicator_scores.items() if v['active']],
                        key=lambda x: x[1]['confidence'],
                        reverse=True
                    )[:5]
                    
                    indicators_html = ""
                    for name, info in active_list:
                        signal_badge = "🟢" if info['current_signal'] == 'AL' else "⚪"
                        indicators_html += f'''
                        <div style="display: flex; justify-content: space-between; padding: 0.25rem 0; border-bottom: 1px solid rgba(255,255,255,0.03);">
                            <span style="color: rgba(255,255,255,0.7); font-size: 0.7rem;">{signal_badge} {name}</span>
                            <span style="color: #10b981; font-size: 0.65rem;">%{info['win_rate']:.0f} başarı</span>
                        </div>'''
                    
                    st.markdown(f'''
<div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 1rem;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
    <div style="font-size: 0.65rem; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 1px;">Adaptif DNA Analizi</div>
    <div style="font-size: 0.6rem; color: rgba(255,255,255,0.3);">{active_count}/{total_count} aktif</div>
</div>
<div style="display: flex; gap: 1rem; margin-bottom: 0.75rem;">
    <div style="flex: 1; background: rgba(16,185,129,0.1); border-radius: 8px; padding: 0.5rem; text-align: center;">
        <div style="font-size: 0.6rem; color: rgba(255,255,255,0.4);">AL Veriyor</div>
        <div style="font-size: 1.25rem; color: #10b981; font-weight: 700;">{buy_count}</div>
    </div>
    <div style="flex: 1; background: rgba(251,191,36,0.1); border-radius: 8px; padding: 0.5rem; text-align: center;">
        <div style="font-size: 0.6rem; color: rgba(255,255,255,0.4);">Bekle</div>
        <div style="font-size: 1.25rem; color: #fbbf24; font-weight: 700;">{active_count - buy_count}</div>
    </div>
</div>
<div style="font-size: 0.6rem; color: rgba(255,255,255,0.35); margin-bottom: 0.5rem;">En Güvenilir İndikatörler:</div>
{indicators_html}
</div>
''', unsafe_allow_html=True)
                elif indicator_dna:
                    # Eskiye uyumluluk (Fallback)
                    trend_w = indicator_dna.get('trend_weight', 1.0)
                    mom_w = indicator_dna.get('momentum_weight', 1.0)
                    vol_w = indicator_dna.get('volume_weight', 1.0)
                    
                    trend_success = indicator_dna.get('trend_success', 50)
                    mom_success = indicator_dna.get('momentum_success', 50)
                    vol_success = indicator_dna.get('volume_success', 50)
                    
                    st.markdown(f'''
<div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 1rem;">
<div style="font-size: 0.65rem; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.75rem;">İndikatör DNA (Son 60 Gün)</div>
<div style="display: flex; gap: 1rem;">
<div style="flex: 1;">
<div style="font-size: 0.6rem; color: rgba(255,255,255,0.35);">Trend (EMA/ADX)</div>
<div style="background: rgba(255,255,255,0.05); border-radius: 4px; height: 6px; margin: 0.25rem 0;">
<div style="height: 100%; width: {min(trend_success, 100)}%; background: #10b981; border-radius: 4px;"></div>
</div>
<div style="font-size: 0.7rem; color: #10b981;">%{trend_success:.0f} başarı → {trend_w:.1f}x</div>
</div>
<div style="flex: 1;">
<div style="font-size: 0.6rem; color: rgba(255,255,255,0.35);">Momentum (RSI)</div>
<div style="background: rgba(255,255,255,0.05); border-radius: 4px; height: 6px; margin: 0.25rem 0;">
<div style="height: 100%; width: {min(mom_success, 100)}%; background: #3b82f6; border-radius: 4px;"></div>
</div>
<div style="font-size: 0.7rem; color: #3b82f6;">%{mom_success:.0f} başarı → {mom_w:.1f}x</div>
</div>
<div style="flex: 1;">
<div style="font-size: 0.6rem; color: rgba(255,255,255,0.35);">Hacim (CMF)</div>
<div style="background: rgba(255,255,255,0.05); border-radius: 4px; height: 6px; margin: 0.25rem 0;">
<div style="height: 100%; width: {min(vol_success, 100)}%; background: #f59e0b; border-radius: 4px;"></div>
</div>
<div style="font-size: 0.7rem; color: #f59e0b;">%{vol_success:.0f} başarı → {vol_w:.1f}x</div>
</div>
</div>
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
            # Backtest işlemlerini grafiğe gönder
            trades_data = backtest_results.get('trades', []) if backtest_results else []
            chart = create_analysis_chart(data, trades=trades_data)
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
                    c1.metric("ATR Çarpanı (Stop)", best_params.get('atr_multiplier', 3.0))
                    c2.metric("Kar Al Oranı", best_params.get('take_profit_ratio', 2.0))
                    c3.metric("RSI Periyodu", best_params.get('rsi_period', 14))
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
