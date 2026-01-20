import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import pandas as pd
import numpy as np

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
# 3.6 BACKTEST MOTORU
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def run_backtest(symbol, years=2):
    """
    Geriye dönük test - strateji performansını ölç
    ATR tabanlı stop-loss ve take-profit ile
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=f"{years}y")
        
        if df.empty or len(df) < 200:
            return None
        
        # İndikatörleri hesapla
        # EMA
        df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # ATR
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=14).mean()
        
        # ADX
        plus_dm = df['High'].diff()
        minus_dm = df['Low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        tr14 = tr.rolling(window=14).sum()
        plus_di = 100 * (plus_dm.rolling(window=14).sum() / tr14)
        minus_di = 100 * (np.abs(minus_dm).rolling(window=14).sum() / tr14)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df['ADX'] = dx.rolling(window=14).mean()
        
        # CMF
        mfv = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        mfv = mfv.fillna(0)
        volume_mfv = mfv * df['Volume']
        df['CMF'] = volume_mfv.rolling(20).sum() / df['Volume'].rolling(20).sum()
        
        # MACD
        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # NaN temizle
        df = df.dropna()
        
        # Backtest
        trades = []
        position = None
        
        for i in range(len(df) - 10):  # Son 10 günü test için bırak
            row = df.iloc[i]
            
            if position is None:
                # AL sinyali kontrol
                score = 0
                
                # Trend
                if row['Close'] > row['EMA200']:
                    if row['ADX'] > 25:
                        score += 25
                    elif row['ADX'] > 20:
                        score += 15
                    else:
                        score += 5
                else:
                    continue  # Düşüş trendinde işlem yapma
                
                # RSI Pullback
                if row['RSI'] < 40:
                    score += 20
                
                # CMF
                if row['CMF'] > 0.05:
                    score += 15
                
                # MACD
                if row['MACD'] > row['MACD_Signal']:
                    score += 10
                
                final_score = 50 + score
                
                # AL sinyali (skor >= 60)
                if final_score >= 60:
                    entry_price = row['Close']
                    atr = row['ATR']
                    stop_loss = entry_price - (2 * atr)
                    take_profit = entry_price + (2 * atr)  # 1:1 R/R
                    
                    position = {
                        "entry_date": df.index[i],
                        "entry_price": entry_price,
                        "stop_loss": stop_loss,
                        "take_profit": take_profit,
                        "score": final_score
                    }
            else:
                # Pozisyon var, çıkış kontrol
                current_price = row['Close']
                
                if current_price <= position['stop_loss']:
                    # Stop loss
                    pnl = ((current_price - position['entry_price']) / position['entry_price']) * 100
                    trades.append({
                        "entry_date": position['entry_date'],
                        "exit_date": df.index[i],
                        "entry_price": position['entry_price'],
                        "exit_price": current_price,
                        "pnl": pnl,
                        "result": "ZARAR",
                        "score": position['score']
                    })
                    position = None
                    
                elif current_price >= position['take_profit']:
                    # Take profit
                    pnl = ((current_price - position['entry_price']) / position['entry_price']) * 100
                    trades.append({
                        "entry_date": position['entry_date'],
                        "exit_date": df.index[i],
                        "entry_price": position['entry_price'],
                        "exit_price": current_price,
                        "pnl": pnl,
                        "result": "KAR",
                        "score": position['score']
                    })
                    position = None
        
        if len(trades) == 0:
            return {"total_trades": 0, "win_rate": 0, "avg_pnl": 0, "trades": []}
        
        # İstatistikler
        wins = len([t for t in trades if t['result'] == "KAR"])
        total = len(trades)
        win_rate = (wins / total) * 100
        avg_pnl = sum([t['pnl'] for t in trades]) / total
        total_pnl = sum([t['pnl'] for t in trades])
        
        return {
            "total_trades": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": win_rate,
            "avg_pnl": avg_pnl,
            "total_pnl": total_pnl,
            "trades": trades[-10:]  # Son 10 işlem
        }
    except Exception as e:
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 4. SİNYAL SKOR HESAPLAMA
# ═══════════════════════════════════════════════════════════════════════════════
def calculate_smart_score(data, weekly_data=None):
    """
    SNIPER STRATEJİSİ v3:
    - ADX filtresi ile yatay piyasada sinyal vermez
    - ATR ile dinamik stop-loss ve kar al seviyeleri
    - Haftalık trend teyidi ile çoklu zaman dilimi analizi
    - Trend + Momentum + Akıllı Para kombinasyonu
    """
    score = 0
    reasons = []
    
    # ═══ HAFTALIK TEYİT (Multi-Timeframe) ═══
    weekly_aligned = True
    if weekly_data:
        if weekly_data['ema_cross'] == "BOĞA":
            score += 10
            reasons.append("Haftalık Trend BOĞA (+10)")
        else:
            score -= 10
            reasons.append("Haftalık Trend AYI (-10)")
            weekly_aligned = False
    
    # ═══ ADX TREND GÜCÜ FİLTRESİ ═══
    # ADX < 20: Trend yok, yatay piyasa - sinyallere güvenme
    # ADX 20-25: Zayıf trend
    # ADX > 25: Güçlü trend
    
    adx_value = data['adx']
    is_trending = adx_value > 20
    is_strong_trend = adx_value > 25
    
    if not is_trending:
        # Yatay piyasa - tüm trend sinyallerinin ağırlığını düşür
        reasons.append(f"ADX {adx_value:.0f} - Trend Yok (Dikkat)")
    elif is_strong_trend:
        reasons.append(f"ADX {adx_value:.0f} - Güçlü Trend")
    else:
        reasons.append(f"ADX {adx_value:.0f} - Zayıf Trend")

    # 1. ANA TREND FİLTRESİ (ADX ile ağırlıklandırılmış)
    if data['price'] > data['ema200']:
        if is_strong_trend:
            score += 25
            reasons.append("Güçlü Boğa Trendi (+25)")
        elif is_trending:
            score += 15
            reasons.append("Zayıf Boğa Trendi (+15)")
        else:
            score += 5  # Yatay piyasada düşük ağırlık
            reasons.append("EMA200 Üstü (+5)")
    else:
        if is_strong_trend:
            score -= 25
            reasons.append("Güçlü Ayı Trendi (-25)")
        elif is_trending:
            score -= 15
            reasons.append("Zayıf Ayı Trendi (-15)")
        else:
            score -= 5
            reasons.append("EMA200 Altı (-5)")

    # 2. MOMENTUM (Sadece trend varken geçerli)
    if is_trending:
        if data['price'] > data['ema200']:
            if data['rsi'] < 40:
                score += 20
                reasons.append("Pullback Fırsatı (+20)")
            elif data['rsi'] > 70:
                score -= 10
                reasons.append("Aşırı Isınma (-10)")
        else:
            if data['rsi'] < 40:
                score -= 10
                reasons.append("Düşen Bıçak (-10)")

    # 3. AKILLI PARA (CMF)
    if data['cmf'] > 0.05:
        score += 15
        reasons.append("Para Girişi (+15)")
    elif data['cmf'] < -0.05:
        score -= 15
        reasons.append("Para Çıkışı (-15)")

    # 4. HACİM
    if data['volume_ratio'] > 1.5:
        if data['change_pct'] > 0:
            score += 10
            reasons.append("Hacimli Yükseliş (+10)")
        else:
            score -= 10
            reasons.append("Hacimli Düşüş (-10)")

    # 5. MACD
    if data['macd'] > data['macd_signal']:
        score += 10
    else:
        score -= 10

    # 6. BOLLINGER SIKIŞMASI
    if data['bb_width'] < 10:
        reasons.append("Sıkışma (Patlama Yakın)")
        if data['trend_direction'] == "YUKARI":
            score += 5
        else:
            score -= 5

    # NORMALİZASYON
    final_score = 50 + score
    final_score = max(0, min(100, final_score))

    # ═══ YATAY PİYASA KORUMASI ═══
    # ADX < 20 ise ve skor 40-60 arasındaysa BEKLE'ye zorla
    if not is_trending and 35 < final_score < 65:
        final_score = 50
        reasons.append("Yatay Piyasa → Bekle")

    # KARAR MEKANİZMASI
    if final_score >= 75:
        signal = "GÜÇLÜ AL"
        color = "#10b981"
    elif final_score >= 60:
        signal = "AL"
        color = "#34d399"
    elif final_score <= 25:
        signal = "GÜÇLÜ SAT"
        color = "#ef4444"
    elif final_score <= 40:
        signal = "SAT"
        color = "#f87171"
    else:
        signal = "BEKLE"
        color = "#fbbf24"

    # ═══ RİSK SEVİYELERİ (ATR Tabanlı) ═══
    atr = data['atr']
    price = data['price']
    
    risk_levels = {
        "stop_loss": price - (2 * atr),      # 2 ATR altı
        "take_profit_1": price + (1.5 * atr), # 1.5 ATR (konservatif)
        "take_profit_2": price + (3 * atr),   # 3 ATR (agresif)
        "risk_reward": 1.5,                   # Risk/Ödül oranı
    }

    return final_score, signal, color, reasons, risk_levels

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
# 6. ANA ARAYÜZ
# ═══════════════════════════════════════════════════════════════════════════════

# Başlık
st.markdown('''
<div class="brand-header">
    <div class="brand-logo">TRENDER <span>PRO</span></div>
    <div class="brand-tagline">Teknik Analiz Platformu</div>
</div>
''', unsafe_allow_html=True)

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
        analyze_btn = st.button("ANALIZ", type="primary", use_container_width=True)

# Analiz Butonu Tıklandığında
if analyze_btn:
    with st.spinner(""):
        data = get_advanced_data(symbol.upper().strip())
        weekly_data = get_weekly_trend(symbol.upper().strip())
        backtest_results = run_backtest(symbol.upper().strip())
    
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
        if backtest_results and backtest_results['total_trades'] > 0:
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
            </div>
            '''
        
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
            <div style="
                display: flex; 
                justify-content: center; 
                gap: 2rem; 
                margin-top: 1.5rem; 
                padding-top: 1rem; 
                border-top: 1px solid rgba(255,255,255,0.06);
            ">
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
            
    else:
        st.error("Veri bulunamadı. Sembolü kontrol edin.")
        st.info("BIST hisseleri için .IS ekleyin. Örnek: THYAO.IS")

# Footer
st.markdown('''
<div class="footer">
    TRENDER PRO · Teknik Analiz Platformu
</div>
''', unsafe_allow_html=True)

