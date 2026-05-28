import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="삼성전자 집중분석",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Bebas+Neue&family=Noto+Sans+KR:wght@300;400;700&display=swap');

  :root {
    --bg: #08090b;
    --surface: #0f1215;
    --surface2: #141820;
    --border: #1c2430;
    --samsung: #1428a0;   /* Samsung Blue */
    --samsung-light: #4d7eff;
    --accent: #00c6ff;
    --accent2: #ff6b35;
    --up: #00e5a0;
    --down: #ff4466;
    --text: #dde4ed;
    --muted: #556070;
  }

  html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background: var(--bg);
    color: var(--text);
  }
  .stApp { background: var(--bg); }

  section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
  }
  section[data-testid="stSidebar"] * { color: var(--text) !important; }

  .hero {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1535 50%, #0a1628 100%);
    border: 1px solid #1c2d5a;
    border-radius: 12px;
    padding: 2rem 2.4rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: 'SAMSUNG';
    position: absolute;
    right: -10px; top: 50%;
    transform: translateY(-50%);
    font-family: 'Bebas Neue', sans-serif;
    font-size: 7rem;
    color: rgba(20,40,160,0.12);
    letter-spacing: 0.1em;
    pointer-events: none;
    white-space: nowrap;
  }
  .hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.8rem;
    letter-spacing: 0.08em;
    background: linear-gradient(90deg, #4d7eff, #00c6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 0.3rem;
  }
  .hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.18em;
    text-transform: uppercase;
  }
  .hero-price {
    font-family: 'DM Mono', monospace;
    font-size: 2.6rem;
    font-weight: 500;
    color: var(--text);
    margin-top: 0.8rem;
  }
  .hero-change-up {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    color: var(--up);
  }
  .hero-change-down {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    color: var(--down);
  }

  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.8rem;
    margin-bottom: 1.2rem;
  }
  .kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
  }
  .kpi-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
  }
  .kpi-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.15rem;
    font-weight: 500;
    color: var(--text);
  }
  .kpi-sub {
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.15rem;
  }

  .section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.35rem;
    letter-spacing: 0.1em;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4rem;
    margin: 1.6rem 0 1rem 0;
  }

  .signal-box {
    border-radius: 8px;
    padding: 0.8rem 1.1rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    border-width: 1px;
    border-style: solid;
  }
  .signal-buy   { background: rgba(0,229,160,0.08); border-color: rgba(0,229,160,0.3); color: #00e5a0; }
  .signal-sell  { background: rgba(255,68,102,0.08); border-color: rgba(255,68,102,0.3); color: #ff4466; }
  .signal-hold  { background: rgba(255,204,0,0.08); border-color: rgba(255,204,0,0.3); color: #ffcc00; }
  .signal-title { font-size: 0.65rem; letter-spacing: 0.15em; opacity: 0.7; margin-bottom: 0.2rem; }
  .signal-val   { font-size: 1.1rem; font-weight: 500; }

  hr { border-color: var(--border) !important; }
  label { color: var(--muted) !important; font-size: 0.78rem !important; }
  div[data-testid="metric-container"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ─────────────────────────────────────────────────────────────────
TICKER      = "005930.KS"   # 삼성전자
TICKER_PREF = "005935.KS"   # 삼성전자 우선주
PEERS = {
    "삼성전자":   "005930.KS",
    "SK하이닉스": "000660.KS",
    "TSMC":      "TSM",
    "Intel":     "INTC",
    "Qualcomm":  "QCOM",
    "NVIDIA":    "NVDA",
}
PLOT_BG    = "rgba(8,9,11,0)"
GRID_COLOR = "#1c2430"
FONT_FAM   = "DM Mono, monospace"

# ─── Helper ────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_history(ticker: str, days: int) -> pd.DataFrame:
    end   = datetime.today()
    start = end - timedelta(days=days)
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    return df

@st.cache_data(ttl=600)
def get_info(ticker: str) -> dict:
    try:
        return yf.Ticker(ticker).info
    except Exception:
        return {}

@st.cache_data(ttl=600)
def get_financials(ticker: str):
    t = yf.Ticker(ticker)
    return t.financials, t.balance_sheet, t.cashflow, t.quarterly_financials

def fmt_krw(v):
    if v is None: return "—"
    if abs(v) >= 1e12: return f"₩{v/1e12:.1f}조"
    if abs(v) >= 1e8:  return f"₩{v/1e8:.0f}억"
    return f"₩{v:,.0f}"

def fmt_num(v, suffix=""):
    if v is None: return "—"
    if abs(v) >= 1e12: return f"{v/1e12:.2f}T{suffix}"
    if abs(v) >= 1e9:  return f"{v/1e9:.1f}B{suffix}"
    if abs(v) >= 1e6:  return f"{v/1e6:.1f}M{suffix}"
    return f"{v:.2f}{suffix}"

def pct(a, b):
    if a and b and b != 0: return (a - b) / abs(b) * 100
    return None

def compute_rsi(series: pd.Series, period=14) -> pd.Series:
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)

def compute_macd(series: pd.Series):
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist   = macd - signal
    return macd, signal, hist

def compute_bb(series: pd.Series, period=20, std=2):
    mid  = series.rolling(period).mean()
    sd   = series.rolling(period).std()
    return mid + std*sd, mid, mid - std*sd

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 분석 설정")
    st.markdown("---")

    period_label = st.selectbox(
        "📅 조회 기간",
        ["3개월","6개월","1년","2년","5년"],
        index=2,
    )
    DAYS = {"3개월":90,"6개월":180,"1년":365,"2년":730,"5년":1825}[period_label]

    show_pref = st.toggle("우선주 비교 표시", value=True)
    show_peers = st.toggle("경쟁사 수익률 비교", value=True)

    st.markdown("**기술적 지표**")
    show_bb   = st.checkbox("볼린저 밴드",  value=True)
    show_rsi  = st.checkbox("RSI",          value=True)
    show_macd = st.checkbox("MACD",         value=True)
    show_vol  = st.checkbox("거래량",        value=True)

    st.markdown("---")
    st.markdown(
        "<div style='font-family:DM Mono;font-size:0.65rem;color:#3a4a5a;'>"
        "데이터: Yahoo Finance · 5분 캐시<br>본 정보는 투자 조언이 아닙니다</div>",
        unsafe_allow_html=True
    )

# ─── Data Load ─────────────────────────────────────────────────────────────────
with st.spinner("삼성전자 데이터 불러오는 중..."):
    df      = get_history(TICKER, DAYS)
    df_pref = get_history(TICKER_PREF, DAYS)
    info    = get_info(TICKER)

if df.empty:
    st.error("데이터를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.")
    st.stop()

close = df["Close"].squeeze()
open_ = df["Open"].squeeze()
high  = df["High"].squeeze()
low   = df["Low"].squeeze()
vol   = df["Volume"].squeeze()

price_now  = float(close.iloc[-1])
price_prev = float(close.iloc[-2]) if len(close) > 1 else price_now
chg_day    = (price_now - price_prev) / price_prev * 100
ret_period = (price_now / float(close.iloc[0]) - 1) * 100

# ─── Hero ──────────────────────────────────────────────────────────────────────
chg_cls = "hero-change-up" if chg_day >= 0 else "hero-change-down"
chg_arrow = "▲" if chg_day >= 0 else "▼"

c1, c2 = st.columns([2, 1])
with c1:
    st.markdown(f"""
    <div class="hero">
      <div class="hero-sub">005930.KS · KRX · 반도체/전자</div>
      <div class="hero-title">삼성전자 집중분석</div>
      <div class="hero-price">₩{price_now:,.0f}</div>
      <div class="{chg_cls}">{chg_arrow} {abs(chg_day):.2f}% (전일 대비) &nbsp;|&nbsp; {period_label} 누적: {ret_period:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    # 52주 고/저
    hi52 = info.get("fiftyTwoWeekHigh")
    lo52 = info.get("fiftyTwoWeekLow")
    dist_hi = ((price_now - hi52) / hi52 * 100) if hi52 else None
    mktcap  = info.get("marketCap")
    avg_vol = info.get("averageVolume")

    st.markdown(f"""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1.2rem 1.4rem;height:100%;">
      <div style="font-family:'DM Mono';font-size:0.65rem;color:var(--muted);letter-spacing:0.12em;margin-bottom:0.6rem;">KEY STATS</div>
      <table style="width:100%;font-family:'DM Mono';font-size:0.82rem;border-collapse:collapse;">
        <tr><td style="color:var(--muted);padding:3px 0;">시가총액</td><td style="text-align:right;color:var(--text);">{fmt_num(mktcap)}</td></tr>
        <tr><td style="color:var(--muted);padding:3px 0;">52주 최고</td><td style="text-align:right;color:var(--text);">{f"₩{hi52:,.0f}" if hi52 else "—"}</td></tr>
        <tr><td style="color:var(--muted);padding:3px 0;">52주 최저</td><td style="text-align:right;color:var(--text);">{f"₩{lo52:,.0f}" if lo52 else "—"}</td></tr>
        <tr><td style="color:var(--muted);padding:3px 0;">고점 대비</td><td style="text-align:right;color:{'#ff4466' if dist_hi and dist_hi<0 else '#00e5a0'};">{f"{dist_hi:+.1f}%" if dist_hi else "—"}</td></tr>
        <tr><td style="color:var(--muted);padding:3px 0;">평균 거래량</td><td style="text-align:right;color:var(--text);">{fmt_num(avg_vol)}</td></tr>
        <tr><td style="color:var(--muted);padding:3px 0;">PER</td><td style="text-align:right;color:var(--text);">{f"{info.get('trailingPE'):.1f}x" if info.get('trailingPE') else "—"}</td></tr>
        <tr><td style="color:var(--muted);padding:3px 0;">PBR</td><td style="text-align:right;color:var(--text);">{f"{info.get('priceToBook'):.2f}x" if info.get('priceToBook') else "—"}</td></tr>
        <tr><td style="color:var(--muted);padding:3px 0;">배당수익률</td><td style="text-align:right;color:var(--text);">{f"{info.get('dividendYield',0)*100:.2f}%" if info.get('dividendYield') else "—"}</td></tr>
      </table>
    </div>
    """, unsafe_allow_html=True)

# ─── KPI Cards ─────────────────────────────────────────────────────────────────
rsi14    = compute_rsi(close).iloc[-1]
ma20     = close.rolling(20).mean().iloc[-1]
ma60     = close.rolling(60).mean().iloc[-1]
bb_u, bb_m, bb_l = compute_bb(close)
bb_pct   = (price_now - float(bb_l.iloc[-1])) / (float(bb_u.iloc[-1]) - float(bb_l.iloc[-1])) * 100
vol_ratio = float(vol.iloc[-1]) / float(vol.rolling(20).mean().iloc[-1]) if float(vol.rolling(20).mean().iloc[-1]) > 0 else 1
macd_line, macd_sig, macd_hist = compute_macd(close)
macd_val = float(macd_hist.iloc[-1])
mdd      = ((close / close.cummax()) - 1).min() * 100
volatility = close.pct_change().std() * np.sqrt(252) * 100

kpis = [
    ("RSI (14)", f"{rsi14:.1f}", "과매수>70 · 과매도<30"),
    ("BB 위치", f"{bb_pct:.0f}%", "0%=하단 · 100%=상단"),
    ("거래량 배율", f"{vol_ratio:.2f}x", "20일 평균 대비"),
    ("MACD 히스토그램", f"{macd_val:+.0f}", "양수=상승모멘텀"),
    ("연환산 변동성", f"{volatility:.1f}%", "가격 변동 리스크"),
    ("최대낙폭(MDD)", f"{mdd:.1f}%", f"기간 내 최대 하락폭"),
    ("MA20 괴리율", f"{(price_now/float(ma20)-1)*100:+.1f}%", f"MA20: ₩{float(ma20):,.0f}"),
    ("MA60 괴리율", f"{(price_now/float(ma60)-1)*100:+.1f}%", f"MA60: ₩{float(ma60):,.0f}"),
]

st.markdown('<div class="section-title">기술적 지표 KPI</div>', unsafe_allow_html=True)

row1 = st.columns(4)
row2 = st.columns(4)
for i, (label, val, sub) in enumerate(kpis):
    col = row1[i] if i < 4 else row2[i - 4]
    with col:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── Signal Summary ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">매매 신호 요약</div>', unsafe_allow_html=True)

def signal_rsi(r):
    if r >= 70: return "sell", f"RSI {r:.1f} — 과매수 구간"
    if r <= 30: return "buy",  f"RSI {r:.1f} — 과매도 구간"
    return "hold", f"RSI {r:.1f} — 중립 구간"

def signal_bb(b):
    if b >= 90: return "sell", f"BB {b:.0f}% — 상단 돌파 근접"
    if b <= 10: return "buy",  f"BB {b:.0f}% — 하단 이탈 근접"
    return "hold", f"BB {b:.0f}% — 밴드 내 중립"

def signal_macd(m):
    if m > 0:  return "buy",  f"MACD 히스토그램 양수 ({m:+.0f}) — 상승 모멘텀"
    if m < 0:  return "sell", f"MACD 히스토그램 음수 ({m:+.0f}) — 하락 모멘텀"
    return "hold", "MACD 교차 대기"

def signal_ma(p, m20, m60):
    if p > m20 > m60: return "buy",  "정배열 (주가 > MA20 > MA60)"
    if p < m20 < m60: return "sell", "역배열 (주가 < MA20 < MA60)"
    return "hold", "이동평균 배열 혼조"

sigs = [
    ("RSI 신호",  *signal_rsi(rsi14)),
    ("BB 신호",   *signal_bb(bb_pct)),
    ("MACD 신호", *signal_macd(macd_val)),
    ("MA 배열",   *signal_ma(price_now, float(ma20), float(ma60))),
]

sig_cols = st.columns(4)
for i, (title, stype, msg) in enumerate(sigs):
    with sig_cols[i]:
        st.markdown(f"""
        <div class="signal-box signal-{stype}">
          <div class="signal-title">{title}</div>
          <div class="signal-val">{'매수' if stype=='buy' else '매도' if stype=='sell' else '중립'}</div>
          <div style="font-size:0.7rem;margin-top:0.3rem;opacity:0.85;">{msg}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── Main Technical Chart ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">기술적 차트</div>', unsafe_allow_html=True)

n_rows  = 1 + show_vol + show_rsi + show_macd
heights = [0.55]
if show_vol:  heights.append(0.15)
if show_rsi:  heights.append(0.15)
if show_macd: heights.append(0.15)
total = sum(heights)
heights = [h / total for h in heights]

fig = make_subplots(
    rows=n_rows, cols=1,
    shared_xaxes=True,
    row_heights=heights,
    vertical_spacing=0.025,
)

# ── Candlestick
fig.add_trace(go.Candlestick(
    x=df.index, open=open_, high=high, low=low, close=close,
    increasing=dict(line=dict(color="#00e5a0", width=1), fillcolor="rgba(0,229,160,0.25)"),
    decreasing=dict(line=dict(color="#ff4466", width=1), fillcolor="rgba(255,68,102,0.25)"),
    name="삼성전자",
), row=1, col=1)

# MA lines
for ma_n, ma_col in [(20, "#4d9fff"), (60, "#ffcc00"), (120, "#c77dff")]:
    ma_s = close.rolling(ma_n).mean()
    fig.add_trace(go.Scatter(
        x=df.index, y=ma_s, name=f"MA{ma_n}",
        line=dict(color=ma_col, width=1.2, dash="dot"),
    ), row=1, col=1)

# Bollinger Bands
if show_bb:
    bb_u_s, bb_m_s, bb_l_s = compute_bb(close)
    fig.add_trace(go.Scatter(
        x=df.index, y=bb_u_s, name="BB 상단",
        line=dict(color="rgba(0,198,255,0.4)", width=1), showlegend=False,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=bb_l_s, name="BB 하단",
        line=dict(color="rgba(0,198,255,0.4)", width=1),
        fill="tonexty", fillcolor="rgba(0,198,255,0.04)", showlegend=False,
    ), row=1, col=1)

# Preferred stock overlay
if show_pref and not df_pref.empty:
    close_pref = df_pref["Close"].squeeze()
    # scale to same base for visual comparison
    scale = float(close.iloc[0]) / float(close_pref.iloc[0])
    fig.add_trace(go.Scatter(
        x=df_pref.index, y=close_pref * scale,
        name="삼성전자 우 (스케일조정)",
        line=dict(color="#ff6b35", width=1.2, dash="longdash"),
        opacity=0.7,
    ), row=1, col=1)

row_cur = 2

# Volume
if show_vol:
    colors_vol = ["#00e5a0" if c >= o else "#ff4466"
                  for c, o in zip(close, open_)]
    fig.add_trace(go.Bar(
        x=df.index, y=vol,
        marker_color=colors_vol,
        opacity=0.55, name="거래량",
    ), row=row_cur, col=1)
    fig.update_yaxes(title_text="거래량", row=row_cur, col=1,
                     gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                     title_font=dict(size=9), tickfont=dict(size=9))
    row_cur += 1

# RSI
if show_rsi:
    rsi_s = compute_rsi(close)
    fig.add_trace(go.Scatter(
        x=df.index, y=rsi_s, name="RSI(14)",
        line=dict(color="#c77dff", width=1.5),
    ), row=row_cur, col=1)
    fig.add_hline(y=70, line_color="rgba(255,68,102,0.5)", line_width=1,
                  line_dash="dash", row=row_cur, col=1)
    fig.add_hline(y=30, line_color="rgba(0,229,160,0.5)", line_width=1,
                  line_dash="dash", row=row_cur, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=row_cur, col=1,
                     gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                     title_font=dict(size=9), tickfont=dict(size=9))
    row_cur += 1

# MACD
if show_macd:
    macd_l, macd_s_l, macd_h = compute_macd(close)
    fig.add_trace(go.Bar(
        x=df.index, y=macd_h,
        marker_color=["#00e5a0" if v >= 0 else "#ff4466" for v in macd_h],
        opacity=0.6, name="MACD 히스토그램",
    ), row=row_cur, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=macd_l, name="MACD",
        line=dict(color="#4d9fff", width=1.4),
    ), row=row_cur, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=macd_s_l, name="Signal",
        line=dict(color="#ff6b35", width=1.2, dash="dot"),
    ), row=row_cur, col=1)
    fig.update_yaxes(title_text="MACD", row=row_cur, col=1,
                     gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                     title_font=dict(size=9), tickfont=dict(size=9))

fig.update_layout(
    paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
    font=dict(family=FONT_FAM, color="#8a9aaa", size=11),
    xaxis_rangeslider_visible=False,
    legend=dict(
        bgcolor="rgba(15,18,21,0.9)", bordercolor=GRID_COLOR, borderwidth=1,
        font=dict(size=10), orientation="h", x=0, y=1.02,
    ),
    height=650 + (show_vol + show_rsi + show_macd) * 120,
    margin=dict(l=10, r=10, t=40, b=10),
    hovermode="x unified",
)
fig.update_xaxes(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, showgrid=False)
fig.update_yaxes(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, row=1, col=1)

st.plotly_chart(fig, use_container_width=True)

# ─── Peer Comparison ──────────────────────────────────────────────────────────
if show_peers:
    st.markdown('<div class="section-title">글로벌 반도체 경쟁사 수익률 비교</div>', unsafe_allow_html=True)

    with st.spinner("경쟁사 데이터 로딩 중..."):
        peer_colors = {
            "삼성전자":   "#4d7eff",
            "SK하이닉스": "#00e5a0",
            "TSMC":      "#ffcc00",
            "Intel":     "#ff6b35",
            "Qualcomm":  "#c77dff",
            "NVIDIA":    "#ff4466",
        }
        fig_peer = go.Figure()
        for peer_name, peer_ticker in PEERS.items():
            try:
                df_p = get_history(peer_ticker, DAYS)
                if df_p.empty: continue
                c_p = df_p["Close"].squeeze()
                ret_p = (c_p / c_p.iloc[0] - 1) * 100
                lw = 2.5 if peer_name == "삼성전자" else 1.5
                dash = "solid" if peer_name == "삼성전자" else "dot"
                fig_peer.add_trace(go.Scatter(
                    x=ret_p.index, y=ret_p.values,
                    name=peer_name,
                    line=dict(color=peer_colors[peer_name], width=lw, dash=dash),
                    hovertemplate=f"<b>{peer_name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.2f}}%<extra></extra>",
                ))
            except Exception:
                pass

    fig_peer.add_hline(y=0, line_color="#2a3040", line_width=1)
    fig_peer.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family=FONT_FAM, color="#8a9aaa", size=11),
        legend=dict(bgcolor="rgba(15,18,21,0.9)", bordercolor=GRID_COLOR, borderwidth=1),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, ticksuffix="%"),
        hovermode="x unified",
        height=420,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_peer, use_container_width=True)

# ─── Financials ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">재무 현황 (연간)</div>', unsafe_allow_html=True)

try:
    fin, bs, cf, qfin = get_financials(TICKER)

    fin_tab, bs_tab, cf_tab, qfin_tab = st.tabs(["손익계산서", "재무상태표", "현금흐름표", "분기 실적"])

    def _safe(df, key):
        try:
            s = df.loc[key]
            return {str(c.year): v for c, v in s.items() if pd.notna(v)}
        except Exception:
            return {}

    def fin_table(items: list, df: pd.DataFrame, unit="억원"):
        rows = []
        for label, key in items:
            d = _safe(df, key)
            if not d: continue
            row = {"항목": label}
            for yr, val in d.items():
                row[yr] = fmt_krw(val)
            rows.append(row)
        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        else:
            st.info("데이터를 불러올 수 없습니다.")

    with fin_tab:
        fin_table([
            ("매출액",       "Total Revenue"),
            ("매출총이익",   "Gross Profit"),
            ("영업이익",     "Operating Income"),
            ("세전이익",     "Pretax Income"),
            ("순이익",       "Net Income"),
            ("R&D 비용",     "Research And Development"),
        ], fin)

    with bs_tab:
        fin_table([
            ("총자산",       "Total Assets"),
            ("총부채",       "Total Liabilities Net Minority Interest"),
            ("자기자본",     "Stockholders Equity"),
            ("현금 및 등가물","Cash And Cash Equivalents"),
            ("단기차입금",   "Current Debt"),
            ("장기부채",     "Long Term Debt"),
        ], bs)

    with cf_tab:
        fin_table([
            ("영업현금흐름",    "Operating Cash Flow"),
            ("투자현금흐름",    "Investing Cash Flow"),
            ("재무현금흐름",    "Financing Cash Flow"),
            ("CAPEX",           "Capital Expenditure"),
            ("잉여현금흐름",    "Free Cash Flow"),
        ], cf)

    with qfin_tab:
        q_items = [
            ("매출액",   "Total Revenue"),
            ("영업이익", "Operating Income"),
            ("순이익",   "Net Income"),
        ]
        rows = []
        for label, key in q_items:
            d = _safe(qfin, key)
            if not d: continue
            row = {"항목": label}
            for col_raw, val in d.items():
                try:
                    dt = pd.to_datetime(col_raw)
                    col_label = dt.strftime("%Y Q") + str((dt.month - 1) // 3 + 1)
                except Exception:
                    col_label = str(col_raw)
                row[col_label] = fmt_krw(val)
            rows.append(row)
        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

        # QoQ Revenue bar chart
        try:
            rev_q = qfin.loc["Total Revenue"].dropna()
            rev_q.index = pd.to_datetime(rev_q.index)
            rev_q = rev_q.sort_index()
            labels = [d.strftime("%Y Q") + str((d.month-1)//3+1) for d in rev_q.index]
            fig_q = go.Figure(go.Bar(
                x=labels, y=rev_q.values / 1e12,
                marker_color=["#4d7eff" if i == len(labels)-1 else "#1c2d5a" for i in range(len(labels))],
                text=[f"₩{v/1e12:.1f}조" for v in rev_q.values],
                textposition="outside",
                textfont=dict(size=10, color="#8a9aaa"),
            ))
            fig_q.update_layout(
                paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
                font=dict(family=FONT_FAM, color="#8a9aaa", size=11),
                yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, title="조원"),
                xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
                height=300, margin=dict(l=10, r=10, t=20, b=10),
                showlegend=False,
                title=dict(text="분기별 매출액", font=dict(size=13, color="#8a9aaa")),
            )
            st.plotly_chart(fig_q, use_container_width=True)
        except Exception:
            pass

except Exception as e:
    st.warning(f"재무 데이터를 불러오는 중 오류 발생: {e}")

# ─── Dividend History ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">배당 이력</div>', unsafe_allow_html=True)
try:
    divs = yf.Ticker(TICKER).dividends
    if not divs.empty:
        divs_df = divs.reset_index()
        divs_df.columns = ["날짜", "배당금(₩)"]
        divs_df["날짜"] = divs_df["날짜"].dt.strftime("%Y-%m-%d")
        divs_df["배당금(₩)"] = divs_df["배당금(₩)"].apply(lambda v: f"₩{v:,.0f}")

        fig_div = go.Figure(go.Bar(
            x=divs.index, y=divs.values,
            marker_color="#4d7eff",
            opacity=0.8,
            name="배당금",
        ))
        fig_div.update_layout(
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font=dict(family=FONT_FAM, color="#8a9aaa", size=11),
            yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, title="₩"),
            xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
            height=260, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_div, use_container_width=True)
        st.dataframe(divs_df.tail(12).sort_values("날짜", ascending=False),
                     hide_index=True, use_container_width=True)
    else:
        st.info("배당 데이터가 없습니다.")
except Exception as e:
    st.warning(f"배당 데이터 오류: {e}")

# ─── Price Distribution ───────────────────────────────────────────────────────
st.markdown('<div class="section-title">가격 분포 분석</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    # Returns histogram
    daily_ret = close.pct_change().dropna() * 100
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=daily_ret, nbinsx=60,
        marker_color="#4d7eff", opacity=0.75, name="일간 수익률",
    ))
    fig_hist.add_vline(x=float(daily_ret.mean()), line_color="#ffcc00",
                       line_width=1.5, line_dash="dash",
                       annotation_text=f"평균 {daily_ret.mean():.2f}%",
                       annotation_font=dict(color="#ffcc00", size=10))
    fig_hist.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family=FONT_FAM, color="#8a9aaa", size=11),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, title="일간 수익률 (%)"),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, title="빈도"),
        height=300, margin=dict(l=10, r=10, t=30, b=10),
        title=dict(text="일간 수익률 분포", font=dict(size=12, color="#8a9aaa")),
        showlegend=False,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col_b:
    # Rolling volatility
    roll_vol = close.pct_change().rolling(20).std() * np.sqrt(252) * 100
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Scatter(
        x=df.index, y=roll_vol,
        line=dict(color="#c77dff", width=1.5),
        fill="tozeroy", fillcolor="rgba(199,125,255,0.08)",
        name="20일 롤링 변동성",
    ))
    fig_vol.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family=FONT_FAM, color="#8a9aaa", size=11),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                   title="연환산 변동성 (%)", ticksuffix="%"),
        height=300, margin=dict(l=10, r=10, t=30, b=10),
        title=dict(text="롤링 변동성 (20일)", font=dict(size=12, color="#8a9aaa")),
        showlegend=False,
    )
    st.plotly_chart(fig_vol, use_container_width=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='font-family:DM Mono;font-size:0.68rem;color:#2a3a4a;text-align:center;padding:0.5rem 0;'>"
    "데이터 출처: Yahoo Finance (yfinance) · 본 정보는 투자 조언이 아닙니다 · "
    f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>",
    unsafe_allow_html=True
)
