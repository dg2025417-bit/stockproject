import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 비교 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Bebas+Neue&family=Noto+Sans+KR:wght@300;400;700&display=swap');

  :root {
    --bg: #0a0d0f;
    --surface: #111518;
    --border: #1e2730;
    --accent: #00e5a0;
    --accent2: #ff6b35;
    --accent3: #4d9fff;
    --text: #e8edf2;
    --muted: #5a6a7a;
    --up: #00e5a0;
    --down: #ff4466;
  }

  html, body, [class*="css"] {
    font-family: 'Noto Sans KR', 'DM Mono', monospace;
    background: var(--bg);
    color: var(--text);
  }

  .stApp { background: var(--bg); }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
  }
  section[data-testid="stSidebar"] * { color: var(--text) !important; }

  /* Header */
  .main-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.2rem;
    letter-spacing: 0.08em;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent3) 60%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
    line-height: 1;
  }
  .sub-header {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
  }

  /* Metric Cards */
  .metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }
  .metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent3));
  }
  .metric-card:hover { border-color: var(--accent); }
  .metric-ticker {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    color: var(--muted);
    text-transform: uppercase;
  }
  .metric-name {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text);
    margin: 0.2rem 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .metric-price {
    font-family: 'DM Mono', monospace;
    font-size: 1.4rem;
    font-weight: 500;
    color: var(--text);
    margin: 0.3rem 0;
  }
  .metric-change-up {
    font-family: 'DM Mono', monospace;
    font-size: 0.9rem;
    color: var(--up);
    font-weight: 500;
  }
  .metric-change-down {
    font-family: 'DM Mono', monospace;
    font-size: 0.9rem;
    color: var(--down);
    font-weight: 500;
  }

  /* Section titles */
  .section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.4rem;
    letter-spacing: 0.1em;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4rem;
    margin: 1.5rem 0 1rem 0;
  }

  /* Divider */
  hr { border-color: var(--border) !important; }

  /* Plotly tweaks */
  .js-plotly-plot .plotly { background: transparent !important; }

  /* Streamlit overrides */
  .stMultiSelect [data-baseweb="select"] {
    background: var(--surface);
    border-color: var(--border);
  }
  .stSlider { color: var(--accent); }
  label { color: var(--muted) !important; font-size: 0.8rem !important; }
  .stSelectbox div[data-baseweb="select"] { background: var(--surface); }
  div[data-testid="metric-container"] { display: none; }

  /* Badge */
  .badge-kr {
    background: rgba(77,159,255,0.15);
    color: var(--accent3);
    border: 1px solid rgba(77,159,255,0.3);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.65rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.08em;
  }
  .badge-us {
    background: rgba(0,229,160,0.12);
    color: var(--accent);
    border: 1px solid rgba(0,229,160,0.3);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.65rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.08em;
  }
</style>
""", unsafe_allow_html=True)

# ─── Stock Definitions ──────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "현대차": "005380.KS",
    "카카오": "035720.KS",
    "네이버(NAVER)": "035420.KS",
    "삼성바이오로직스": "207940.KS",
    "셀트리온": "068270.KS",
    "POSCO홀딩스": "005490.KS",
    "KB금융": "105560.KS",
    "LG화학": "051910.KS",
    "현대모비스": "012330.KS",
}

US_STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet (Google)": "GOOGL",
    "Meta": "META",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK-B",
    "JPMorgan Chase": "JPM",
    "Visa": "V",
    "Johnson & Johnson": "JNJ",
    "Walmart": "WMT",
}

INDICES = {
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "다우존스": "^DJI",
}

PERIOD_MAP = {
    "1개월": 30,
    "3개월": 90,
    "6개월": 180,
    "1년": 365,
    "3년": 1095,
}

COLORS = [
    "#00e5a0", "#4d9fff", "#ff6b35", "#ffcc00",
    "#c77dff", "#ff4466", "#00ccff", "#ff9f1c",
    "#a8ff78", "#f72585", "#7209b7", "#3a86ff",
]

# ─── Helper Functions ───────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_data(tickers: list, days: int) -> dict:
    end = datetime.today()
    start = end - timedelta(days=days)
    result = {}
    for t in tickers:
        try:
            df = yf.download(t, start=start, end=end, progress=False, auto_adjust=True)
            if not df.empty:
                result[t] = df
        except Exception:
            pass
    return result

@st.cache_data(ttl=300)
def fetch_quote(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).fast_info
        return {
            "price": getattr(info, "last_price", None),
            "prev_close": getattr(info, "previous_close", None),
        }
    except Exception:
        return {}

def compute_returns(df: pd.DataFrame) -> pd.Series:
    close = df["Close"].squeeze()
    return (close / close.iloc[0] - 1) * 100

def pct_change(current, prev):
    if current and prev and prev != 0:
        return (current - prev) / prev * 100
    return None


# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ 설정")
    st.markdown("---")

    period_label = st.selectbox("📅 기간", list(PERIOD_MAP.keys()), index=3)
    period_days = PERIOD_MAP[period_label]

    st.markdown("**🇰🇷 한국 주식**")
    kr_selected = st.multiselect(
        "종목 선택 (최대 6개)",
        list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "카카오"],
        max_selections=6,
    )

    st.markdown("**🇺🇸 미국 주식**")
    us_selected = st.multiselect(
        "종목 선택 (최대 6개)",
        list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Tesla"],
        max_selections=6,
    )

    show_index = st.toggle("지수 오버레이 표시", value=True)
    chart_type = st.radio("차트 타입", ["수익률 비교 (%)", "캔들스틱"], horizontal=True)

    st.markdown("---")
    st.markdown(
        "<div style='font-family:DM Mono;font-size:0.65rem;color:#5a6a7a;'>데이터: Yahoo Finance · 5분 캐시</div>",
        unsafe_allow_html=True
    )


# ─── Main Layout ────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">GLOBAL STOCK DASHBOARD</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">한국 · 미국 주요 종목 수익률 비교 분석</div>', unsafe_allow_html=True)

# Build ticker lists
kr_tickers = {n: KR_STOCKS[n] for n in kr_selected}
us_tickers = {n: US_STOCKS[n] for n in us_selected}
all_tickers = {**kr_tickers, **us_tickers}

if not all_tickers:
    st.warning("사이드바에서 종목을 하나 이상 선택해주세요.")
    st.stop()

# ─── Quote Cards ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">실시간 시세</div>', unsafe_allow_html=True)

all_names = list(all_tickers.keys())
cols = st.columns(min(len(all_names), 4))

for i, name in enumerate(all_names):
    ticker = all_tickers[name]
    quote = fetch_quote(ticker)
    price = quote.get("price")
    prev = quote.get("prev_close")
    chg = pct_change(price, prev)
    is_kr = name in kr_tickers
    badge = '<span class="badge-kr">KR</span>' if is_kr else '<span class="badge-us">US</span>'

    if price:
        price_str = f"₩{price:,.0f}" if is_kr else f"${price:,.2f}"
    else:
        price_str = "—"

    if chg is not None:
        chg_cls = "metric-change-up" if chg >= 0 else "metric-change-down"
        chg_str = f"{'▲' if chg >= 0 else '▼'} {abs(chg):.2f}%"
    else:
        chg_cls = "metric-change-up"
        chg_str = "—"

    col = cols[i % 4]
    with col:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-ticker">{ticker} &nbsp;{badge}</div>
          <div class="metric-name">{name}</div>
          <div class="metric-price">{price_str}</div>
          <div class="{chg_cls}">{chg_str}</div>
        </div>
        """, unsafe_allow_html=True)

# Extra rows if more than 4 stocks
if len(all_names) > 4:
    cols2 = st.columns(min(len(all_names) - 4, 4))
    for j, name in enumerate(all_names[4:]):
        ticker = all_tickers[name]
        quote = fetch_quote(ticker)
        price = quote.get("price")
        prev = quote.get("prev_close")
        chg = pct_change(price, prev)
        is_kr = name in kr_tickers
        badge = '<span class="badge-kr">KR</span>' if is_kr else '<span class="badge-us">US</span>'
        price_str = (f"₩{price:,.0f}" if is_kr else f"${price:,.2f}") if price else "—"
        if chg is not None:
            chg_cls = "metric-change-up" if chg >= 0 else "metric-change-down"
            chg_str = f"{'▲' if chg >= 0 else '▼'} {abs(chg):.2f}%"
        else:
            chg_cls = "metric-change-up"; chg_str = "—"
        col = cols2[j % 4]
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-ticker">{ticker} &nbsp;{badge}</div>
              <div class="metric-name">{name}</div>
              <div class="metric-price">{price_str}</div>
              <div class="{chg_cls}">{chg_str}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Fetch Historical Data ───────────────────────────────────────────────────────
with st.spinner("시세 데이터 로딩 중..."):
    fetch_tickers = list(all_tickers.values())
    if show_index and chart_type == "수익률 비교 (%)":
        fetch_tickers += list(INDICES.values())
    data = fetch_data(tuple(fetch_tickers), period_days)

# ─── Main Chart ─────────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-title">{period_label} 수익률 비교</div>', unsafe_allow_html=True)

PLOT_BG = "rgba(10,13,15,0)"
GRID_COLOR = "#1e2730"
FONT_FAMILY = "DM Mono, monospace"

if chart_type == "수익률 비교 (%)":
    fig = go.Figure()
    color_idx = 0

    for group_name, tickers_dict, dash_style in [
        ("KR", kr_tickers, "solid"),
        ("US", us_tickers, "dot"),
    ]:
        for name, ticker in tickers_dict.items():
            if ticker not in data:
                continue
            df = data[ticker]
            ret = compute_returns(df)
            fig.add_trace(go.Scatter(
                x=ret.index,
                y=ret.values,
                name=name,
                line=dict(color=COLORS[color_idx % len(COLORS)], width=2, dash=dash_style),
                hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>수익률: %{{y:.2f}}%<extra></extra>",
            ))
            color_idx += 1

    if show_index:
        for idx_name, idx_ticker in INDICES.items():
            if idx_ticker in data:
                ret = compute_returns(data[idx_ticker])
                fig.add_trace(go.Scatter(
                    x=ret.index, y=ret.values,
                    name=f"[지수] {idx_name}",
                    line=dict(color="#3a3f4a", width=1.5, dash="longdash"),
                    opacity=0.6,
                    hovertemplate=f"<b>{idx_name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.2f}}%<extra></extra>",
                ))

    fig.add_hline(y=0, line_color="#3a3f4a", line_width=1)
    fig.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family=FONT_FAMILY, color="#8a9aaa", size=11),
        legend=dict(
            bgcolor="rgba(17,21,24,0.9)", bordercolor=GRID_COLOR, borderwidth=1,
            font=dict(size=11), orientation="v", x=1.01, y=1,
        ),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, showgrid=True),
        yaxis=dict(
            gridcolor=GRID_COLOR, linecolor=GRID_COLOR, showgrid=True,
            ticksuffix="%", zeroline=False,
        ),
        hovermode="x unified",
        height=520,
        margin=dict(l=10, r=160, t=20, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    # Candlestick mode — show one per row
    selected_for_candle = st.selectbox(
        "캔들스틱 종목 선택",
        list(all_tickers.keys()),
    )
    ticker_c = all_tickers[selected_for_candle]
    if ticker_c in data:
        df_c = data[ticker_c]
        close_c = df_c["Close"].squeeze()
        open_c = df_c["Open"].squeeze()
        high_c = df_c["High"].squeeze()
        low_c = df_c["Low"].squeeze()
        vol_c = df_c["Volume"].squeeze()

        fig2 = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            row_heights=[0.75, 0.25], vertical_spacing=0.03,
        )
        fig2.add_trace(go.Candlestick(
            x=df_c.index, open=open_c, high=high_c, low=low_c, close=close_c,
            increasing=dict(line=dict(color="#00e5a0"), fillcolor="rgba(0,229,160,0.3)"),
            decreasing=dict(line=dict(color="#ff4466"), fillcolor="rgba(255,68,102,0.3)"),
            name=selected_for_candle,
        ), row=1, col=1)
        fig2.add_trace(go.Bar(
            x=df_c.index, y=vol_c,
            marker_color=["#00e5a0" if c >= o else "#ff4466"
                          for c, o in zip(close_c, open_c)],
            opacity=0.6, name="거래량",
        ), row=2, col=1)

        # MA lines
        for ma, color in [(20, "#4d9fff"), (60, "#ffcc00")]:
            ma_s = close_c.rolling(ma).mean()
            fig2.add_trace(go.Scatter(
                x=df_c.index, y=ma_s, name=f"MA{ma}",
                line=dict(color=color, width=1.2, dash="dot"),
            ), row=1, col=1)

        fig2.update_layout(
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font=dict(family=FONT_FAMILY, color="#8a9aaa", size=11),
            xaxis_rangeslider_visible=False,
            legend=dict(bgcolor="rgba(17,21,24,0.9)", bordercolor=GRID_COLOR, borderwidth=1),
            height=600,
            margin=dict(l=10, r=20, t=20, b=10),
        )
        for ax in ["xaxis", "xaxis2", "yaxis", "yaxis2"]:
            fig2.update_layout(**{ax: dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR)})
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.error("해당 종목 데이터를 불러올 수 없습니다.")

# ─── Return Summary Table ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">수익률 요약 테이블</div>', unsafe_allow_html=True)

rows = []
for name, ticker in all_tickers.items():
    if ticker not in data:
        continue
    df = data[ticker]
    close = df["Close"].squeeze()
    ret_total = (close.iloc[-1] / close.iloc[0] - 1) * 100
    ret_1m = None
    if len(close) >= 21:
        ret_1m = (close.iloc[-1] / close.iloc[-21] - 1) * 100
    volatility = close.pct_change().std() * np.sqrt(252) * 100
    max_dd = ((close / close.cummax()) - 1).min() * 100
    is_kr = name in kr_tickers

    rows.append({
        "종목": name,
        "시장": "🇰🇷 KR" if is_kr else "🇺🇸 US",
        f"{period_label} 수익률": f"{ret_total:+.2f}%",
        "1개월 수익률": f"{ret_1m:+.2f}%" if ret_1m is not None else "—",
        "변동성(연환산)": f"{volatility:.1f}%",
        "최대낙폭(MDD)": f"{max_dd:.2f}%",
    })

if rows:
    df_table = pd.DataFrame(rows)
    st.dataframe(
        df_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "종목": st.column_config.TextColumn(width="medium"),
            "시장": st.column_config.TextColumn(width="small"),
        },
    )

# ─── Correlation Heatmap ─────────────────────────────────────────────────────────
if len(all_tickers) >= 3:
    st.markdown('<div class="section-title">종목 간 상관관계 히트맵</div>', unsafe_allow_html=True)

    returns_dict = {}
    for name, ticker in all_tickers.items():
        if ticker in data:
            close = data[ticker]["Close"].squeeze()
            returns_dict[name] = close.pct_change().dropna()

    if len(returns_dict) >= 2:
        ret_df = pd.DataFrame(returns_dict).dropna()
        corr = ret_df.corr()

        fig3 = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale=[
                [0.0, "#ff4466"], [0.5, "#111518"], [1.0, "#00e5a0"]
            ],
            zmin=-1, zmax=1,
            text=[[f"{v:.2f}" for v in row] for row in corr.values],
            texttemplate="%{text}",
            textfont=dict(size=11, family=FONT_FAMILY),
            hoverongaps=False,
        ))
        fig3.update_layout(
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font=dict(family=FONT_FAMILY, color="#8a9aaa", size=11),
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(tickangle=-30),
        )
        st.plotly_chart(fig3, use_container_width=True)

# ─── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='font-family:DM Mono;font-size:0.7rem;color:#3a4a5a;text-align:center;padding:0.5rem 0;'>"
    "데이터 출처: Yahoo Finance (yfinance) · 본 정보는 투자 조언이 아닙니다 · "
    f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>",
    unsafe_allow_html=True
)
