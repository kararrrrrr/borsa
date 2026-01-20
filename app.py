import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import pandas as pd
import numpy as np

# ═══════════════════════════════════════════════════════════════════════════════
# 1. SAYFA AYARLARI & PREMIUM CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Finansal Analiz Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Koyu Tema CSS
st.markdown("""
<style>
    /* Ana Tema - Koyu Gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Glassmorphism Kartlar */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
        transform: translateY(-2px);
    }
    
    /* Başlık Stili */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .sub-title {
        text-align: center;
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
    
    /* Metrik Kartları */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.12);
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 0.85rem !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
    }
    
    /* Pozitif/Negatif Değişim */
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    
    /* Input Alanı */
    .stTextInput > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Buton Stili */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Expander Stili */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* Status Widget */
    [data-testid="stStatusWidget"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 16px !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.8rem;
        padding: 2rem 0 1rem 0;
        margin-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Mobil Responsive */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        
        .glass-card {
            padding: 1rem;
            margin: 0.3rem 0;
        }
    }
    
    /* İndikatör Badge'leri */
    .indicator-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    .badge-bullish {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .badge-bearish {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .badge-neutral {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    
    /* Sinyal Gücü Barı */
    .signal-bar {
        height: 8px;
        border-radius: 4px;
        background: rgba(255, 255, 255, 0.1);
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .signal-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
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
# 4. SİNYAL SKOR HESAPLAMA
# ═══════════════════════════════════════════════════════════════════════════════
def calculate_signal_score(data):
    """Teknik verilere göre 0-100 arası sinyal skoru hesapla"""
    score = 50  # Başlangıç nötr
    
    # RSI Katkısı (-15 / +15)
    if data['rsi'] < 30:
        score += 15  # Aşırı satım = Alım fırsatı
    elif data['rsi'] < 40:
        score += 8
    elif data['rsi'] > 70:
        score -= 15  # Aşırı alım = Satış sinyali
    elif data['rsi'] > 60:
        score -= 8
    
    # MACD Katkısı (-12 / +12)
    if data['macd_status'] == "AL":
        score += 12
        if data['macd_hist'] > 0:
            score += 3  # Histogram pozitif bonus
    else:
        score -= 12
        if data['macd_hist'] < 0:
            score -= 3
    
    # Trend Katkısı (-10 / +10)
    if data['trend_direction'] == "YUKARI":
        score += 10
    else:
        score -= 10
    
    # Bollinger Pozisyonu (-8 / +8)
    if data['bb_position'] < 20:
        score += 8  # Alt bantta = potansiyel alım
    elif data['bb_position'] > 80:
        score -= 8  # Üst bantta = potansiyel satış
    
    # Hacim Katkısı (-5 / +5)
    if data['volume_ratio'] > 1.5 and data['obv_trend'] == "YUKARI":
        score += 5
    elif data['volume_ratio'] > 1.5 and data['obv_trend'] == "AŞAĞI":
        score -= 5
    
    # ADX Trend Gücü (±5)
    if data['adx'] > 25:
        if data['trend_direction'] == "YUKARI":
            score += 5
        else:
            score -= 5
    
    # Sınırla
    score = max(0, min(100, score))
    
    # Sinyal belirleme
    if score >= 70:
        signal = "GÜÇLÜ AL"
        color = "#10b981"
    elif score >= 55:
        signal = "AL"
        color = "#34d399"
    elif score <= 30:
        signal = "GÜÇLÜ SAT"
        color = "#ef4444"
    elif score <= 45:
        signal = "SAT"
        color = "#f87171"
    else:
        signal = "BEKLE"
        color = "#fbbf24"
    
    return score, signal, color

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
    
    model = genai.GenerativeModel('gemini-3-pro-preview')
    
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
st.markdown('<h1 class="main-title">📊 Finansal Analiz Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Gelişmiş Teknik Analiz & Yapay Zeka Destekli Piyasa Yorumu</p>', unsafe_allow_html=True)

# Input Alanı
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    input_col, btn_col = st.columns([3, 1])
    with input_col:
        symbol = st.text_input(
            "Hisse Kodu",
            value="THYAO.IS",
            label_visibility="collapsed",
            placeholder="Hisse Kodu Girin (Örn: GARAN.IS, EREGL.IS)"
        )
    with btn_col:
        analyze_btn = st.button("🔍 Analiz", type="primary", use_container_width=True)

# Analiz Butonu Tıklandığında
if analyze_btn:
    with st.spinner(""):
        data = get_advanced_data(symbol.upper().strip())
    
    if data:
        st.markdown("---")
        
        # ═══ SİNYAL SKORU ═══
        score, signal, signal_color = calculate_signal_score(data)
        
        # Büyük Sinyal Kartı
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {signal_color}22 0%, {signal_color}11 100%);
            border: 2px solid {signal_color};
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            margin-bottom: 1.5rem;
        ">
            <div style="font-size: 3rem; font-weight: 800; color: {signal_color};">{signal}</div>
            <div style="font-size: 1.5rem; color: rgba(255,255,255,0.8);">Skor: {score}/100</div>
            <div style="
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                height: 12px;
                margin-top: 1rem;
                overflow: hidden;
            ">
                <div style="
                    width: {score}%;
                    height: 100%;
                    background: {signal_color};
                    border-radius: 10px;
                    transition: width 0.5s ease;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ═══ KPI METRİKLERİ ═══
        st.markdown("### 📈 Teknik Göstergeler")
        
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        
        # Fiyat
        delta_color = "normal" if data['change_pct'] >= 0 else "inverse"
        kpi1.metric(
            "💰 Fiyat",
            f"{data['price']:.2f} ₺",
            f"{data['change_pct']:+.2f}%",
            delta_color=delta_color
        )
        
        # RSI - daha net açıklama
        if data['rsi'] > 70:
            rsi_label = "🔥 Pahalı"
            rsi_desc = "Satış baskısı olası"
        elif data['rsi'] < 30:
            rsi_label = "❄️ Ucuz"
            rsi_desc = "Alım fırsatı olası"
        else:
            rsi_label = "⚖️ Normal"
            rsi_desc = "Dengeli bölge"
        kpi2.metric(rsi_label, f"{data['rsi']:.1f}", rsi_desc)
        
        # MACD - daha net açıklama
        macd_icon = "🟢" if data['macd_status'] == "AL" else "🔴"
        macd_desc = "Yukarı momentum" if data['macd_status'] == "AL" else "Aşağı momentum"
        kpi3.metric(f"MACD {macd_icon}", data['macd_status'], macd_desc)
        
        # ADX - daha net açıklama
        if data['adx'] > 25:
            adx_desc = "Trend güçlü"
        else:
            adx_desc = "Trend zayıf"
        kpi4.metric("📊 Trend Gücü", f"{data['adx']:.1f}", adx_desc)
        
        # Volatilite - daha net açıklama
        if data['atr_pct'] > 3:
            vol_desc = "Yüksek oynaklık"
        elif data['atr_pct'] > 1.5:
            vol_desc = "Normal oynaklık"
        else:
            vol_desc = "Düşük oynaklık"
        kpi5.metric("⚡ Oynaklık", f"%{data['atr_pct']:.2f}", vol_desc)
        
        st.markdown("---")
        
        # ═══ DETAYLI METRİKLER ═══
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 📊 Momentum Detayları")
            m1, m2 = st.columns(2)
            
            # Stoch RSI açıklaması
            if data['stoch_rsi'] > 80:
                stoch_desc = "Çok pahalı"
            elif data['stoch_rsi'] < 20:
                stoch_desc = "Çok ucuz"
            else:
                stoch_desc = "Normal"
            m1.metric("Stoch RSI", f"{data['stoch_rsi']:.1f}", stoch_desc)
            
            # Bollinger açıklaması
            if data['bb_position'] > 80:
                bb_desc = "Üst bant (tehlike)"
            elif data['bb_position'] < 20:
                bb_desc = "Alt bant (fırsat)"
            else:
                bb_desc = "Orta bölge"
            m2.metric("Bollinger %", f"{data['bb_position']:.1f}%", bb_desc)
            
            m3, m4 = st.columns(2)
            m3.metric("50G Ortalama", f"{data['sma50']:.2f} ₺", "Kısa vade trend")
            m4.metric("200G Ortalama", f"{data['sma200']:.2f} ₺" if pd.notna(data['sma200']) else "N/A", "Uzun vade trend")
        
        with col_right:
            st.markdown("### 🎯 Kritik Seviyeler")
            s1, s2 = st.columns(2)
            
            # Direnç mesafesi
            res_dist = ((data['resistance'] - data['price']) / data['price']) * 100
            s1.metric("Direnç", f"{data['resistance']:.2f} ₺", f"%{res_dist:+.1f} uzaklık")
            
            # Destek mesafesi
            sup_dist = ((data['support'] - data['price']) / data['price']) * 100
            s2.metric("Destek", f"{data['support']:.2f} ₺", f"%{sup_dist:+.1f} uzaklık")
            
            s3, s4 = st.columns(2)
            s3.metric("Pivot", f"{data['pivot']:.2f} ₺", "Denge noktası")
            
            # Hacim açıklaması
            if data['volume_ratio'] > 1.5:
                vol_status = "Yoğun işlem"
            elif data['volume_ratio'] < 0.5:
                vol_status = "Düşük işlem"
            else:
                vol_status = "Normal işlem"
            s4.metric("Hacim", f"{data['volume_ratio']:.2f}x", vol_status)
        
        st.markdown("---")
        
        # ═══ GRAFİK ═══
        st.markdown("### 📈 Teknik Grafik")
        chart = create_analysis_chart(data)
        st.plotly_chart(chart, use_container_width=True)
        
        st.markdown("---")
        
        # ═══ YAPAY ZEKA ANALİZİ ═══
        with st.status("🤖 Yapay Zeka Analizi Hazırlanıyor...", expanded=True) as status:
            ai_comment = get_ai_analysis(data, score, signal)
            st.markdown(ai_comment)
            status.update(label="✅ Analiz Tamamlandı", state="complete", expanded=True)
            
    else:
        st.error("❌ Veri bulunamadı. Lütfen hisse kodunu kontrol edin.")
        st.info("💡 **İpucu:** BIST hisseleri için sonuna `.IS` eklemeyi unutmayın. Örnek: `THYAO.IS`, `GARAN.IS`")

# Footer
st.markdown("""
<div class="footer">
    <p>📊 Finansal Analiz Pro | Teknik Analiz & AI Yorumu</p>
    <p style="font-size: 0.7rem; margin-top: 0.5rem;">
        ⚠️ Bu uygulama yalnızca eğitim amaçlıdır. Yatırım tavsiyesi değildir.
    </p>
</div>
""", unsafe_allow_html=True)
