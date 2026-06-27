import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 부모 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.services.stock_service import StockService
from src.services.cache_service import CacheService, DataService
from src.database.manager import DatabaseManager

logger = setup_logger(__name__)

# 페이지 설정 (안전하게 처리)
try:
    st.set_page_config(
        page_title="Stock Monitor",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception as e:
    logger.warning(f"set_page_config failed: {e}")

# 커스텀 CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .status-connected {
        color: #00ff00;
        font-weight: bold;
    }
    .status-disconnected {
        color: #ff0000;
        font-weight: bold;
    }
    .up-price {
        color: #ff4444;
    }
    .down-price {
        color: #4444ff;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_service():
    """서비스 초기화"""
    service = StockService(
        api_key=Config.SAMSUNG_API_KEY,
        account_id=Config.SAMSUNG_ACCOUNT_ID,
        api_secret=Config.SAMSUNG_API_SECRET
    )
    return service

def init_session_state():
    """세션 상태 초기화"""
    if "service" not in st.session_state:
        st.session_state.service = init_service()
    if "running" not in st.session_state:
        st.session_state.running = False
    if "stock_codes" not in st.session_state:
        st.session_state.stock_codes = []

def main():
    """메인 앱"""
    init_session_state()

    service = st.session_state.service
    stock_names = Config.get_stock_names()
    db = DatabaseManager()
    data_service = DataService()

    # 사이드바
    with st.sidebar:
        st.title("📊 Stock Monitor")
        st.markdown("---")

        # 상태 표시
        is_healthy = service.is_running() if st.session_state.running else False
        if is_healthy:
            st.markdown('<span class="status-connected">✓ 연결됨</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-disconnected">✗ 미연결</span>', unsafe_allow_html=True)

        st.markdown("---")

        # 종목 선택
        st.subheader("📌 모니터링 종목")
        default_stocks = Config.DEFAULT_STOCKS[:5]

        selected_codes = st.multiselect(
            "종목 선택 (최대 5개)",
            options=Config.DEFAULT_STOCKS,
            default=default_stocks,
            max_selections=5,
            format_func=lambda x: f"{x} - {stock_names.get(x, '미등록')}"
        )

        st.markdown("---")

        # 서비스 제어
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ 시작", use_container_width=True):
                if not st.session_state.running and selected_codes:
                    try:
                        service.start(selected_codes)
                        st.session_state.running = True
                        st.session_state.stock_codes = selected_codes
                        st.success("✓ 데이터 수집 시작")
                    except Exception as e:
                        st.error(f"❌ 시작 실패: {e}")
                        logger.error(f"Service start error: {e}")

        with col2:
            if st.button("⏹️ 중지", use_container_width=True):
                if st.session_state.running:
                    service.stop()
                    st.session_state.running = False
                    st.info("⏹️ 데이터 수집 중지")

        st.markdown("---")

        # 앱 정보
        with st.expander("ℹ️ 정보"):
            st.markdown("""
            **삼성증권 Atosplus API 기반**
            실시간 주식 모니터링 대시보드

            **주요 기능:**
            - 실시간 가격 및 거래량
            - 외국인/기관 매매 현황
            - 차트 및 통계

            **데이터 출처:**
            - Atosplus WebSocket API
            - SQLite 데이터베이스

            **업데이트 간격:**
            1초 단위
            """)

    # 메인 콘텐츠
    st.title("📈 Stock Monitor Dashboard")

    # 상단 정보
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("모니터링 종목", f"{len(st.session_state.stock_codes)}/5")
    with col2:
        status = "🟢 연결됨" if is_healthy else "🔴 미연결"
        st.metric("연결 상태", status)
    with col3:
        data_status = "활성화" if st.session_state.running else "중지됨"
        st.metric("데이터 수집", data_status)
    with col4:
        st.metric("데이터베이스", "✓ 준비됨")

    st.markdown("---")

    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "📈 Analytics",
        "📋 History",
        "⚙️ Settings"
    ])

    with tab1:
        st.subheader("실시간 종목 현황")
        if not st.session_state.stock_codes:
            st.warning("⚠️ 모니터링할 종목을 선택하고 '시작' 버튼을 눌러주세요.")
        else:
            st.info(f"선택된 종목: {', '.join([f'{code} ({stock_names.get(code)})' for code in st.session_state.stock_codes])}")

            # 종목별 카드
            cols = st.columns(min(len(st.session_state.stock_codes), 3))
            for idx, code in enumerate(st.session_state.stock_codes):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.subheader(f"{stock_names.get(code, code)}")

                        # 최신 데이터 조회
                        latest_price = db.get_latest_price(code)
                        latest_trade = db.get_latest_trade(code)

                        if latest_price:
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric(
                                    "현재가",
                                    data_service.format_price(latest_price["price"])
                                )
                            with col_b:
                                st.metric(
                                    "거래량",
                                    data_service.format_volume(latest_price.get("volume", 0))
                                )
                        else:
                            st.info("📊 데이터 수집 중...")

                        if latest_trade:
                            col_a, col_b = st.columns(2)
                            with col_a:
                                net_foreign = latest_trade.get("net_foreign", 0)
                                color = "green" if net_foreign > 0 else "red"
                                st.metric(
                                    "외국인 순매수",
                                    f"{net_foreign:,}주"
                                )
                            with col_b:
                                net_inst = latest_trade.get("net_institution", 0)
                                st.metric(
                                    "기관 순매수",
                                    f"{net_inst:,}주"
                                )

    with tab2:
        st.subheader("차트 및 분석")

        if not st.session_state.stock_codes:
            st.warning("⚠️ 먼저 종목을 선택하고 데이터 수집을 시작하세요.")
        else:
            selected_stock = st.selectbox(
                "분석할 종목 선택",
                options=st.session_state.stock_codes,
                format_func=lambda x: f"{x} - {stock_names.get(x)}"
            )

            prices = db.get_prices(selected_stock, hours=24)

            if prices:
                # 데이터 프레임 생성
                df = pd.DataFrame(prices)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')

                # 가격 차트
                st.line_chart(
                    data=df.set_index('timestamp')[['price']],
                    title="24시간 가격 추이"
                )

                # 거래량 차트
                st.bar_chart(
                    data=df.set_index('timestamp')[['volume']],
                    title="거래량"
                )

                # 통계
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    min_price = df['price'].min()
                    st.metric("최저가", data_service.format_price(min_price))
                with col2:
                    max_price = df['price'].max()
                    st.metric("최고가", data_service.format_price(max_price))
                with col3:
                    avg_price = df['price'].mean()
                    st.metric("평균가", data_service.format_price(avg_price))
                with col4:
                    total_volume = df['volume'].sum()
                    st.metric("총 거래량", data_service.format_volume(int(total_volume)))
            else:
                st.info("📊 수집된 데이터가 없습니다.")

    with tab3:
        st.subheader("과거 데이터")
        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input("시작 날짜", value=datetime.now() - timedelta(days=7))
        with col2:
            to_date = st.date_input("종료 날짜", value=datetime.now())

        if st.button("조회", use_container_width=True):
            if not st.session_state.stock_codes:
                st.warning("⚠️ 먼저 종목을 선택하세요.")
            else:
                selected_stock = st.selectbox(
                    "종목 선택",
                    options=st.session_state.stock_codes,
                    format_func=lambda x: f"{x} - {stock_names.get(x)}"
                )

                prices = db.get_prices(selected_stock, hours=24*7)  # 7일간
                if prices:
                    df = pd.DataFrame(prices)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df[(df['timestamp'].dt.date >= from_date) & (df['timestamp'].dt.date <= to_date)]

                    if len(df) > 0:
                        st.dataframe(df, use_container_width=True)

                        # CSV 다운로드
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 CSV 다운로드",
                            data=csv,
                            file_name=f"{selected_stock}_{from_date}_{to_date}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("해당 기간의 데이터가 없습니다.")
                else:
                    st.info("📊 수집된 데이터가 없습니다.")

    with tab4:
        st.subheader("설정")

        # 종목 관리 섹션
        st.markdown("**📌 모니터링 종목 관리**")

        col1, col2 = st.columns([2, 1])
        with col1:
            new_stock_code = st.text_input(
                "새 종목 코드 입력 (예: 005930)",
                placeholder="6자리 종목 코드"
            )
        with col2:
            st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
            if st.button("➕ 종목 추가", use_container_width=True):
                if new_stock_code and len(new_stock_code) == 6:
                    if new_stock_code not in Config.DEFAULT_STOCKS:
                        Config.DEFAULT_STOCKS.append(new_stock_code)
                        st.success(f"✓ {new_stock_code} 추가됨")
                        st.rerun()
                    else:
                        st.warning("⚠️ 이미 등록된 종목입니다")
                else:
                    st.error("❌ 6자리 종목 코드를 입력해주세요")

        st.markdown("**현재 모니터링 종목:**")
        cols = st.columns(3)
        for idx, code in enumerate(Config.DEFAULT_STOCKS):
            with cols[idx % 3]:
                col_delete, col_name = st.columns([1, 2])
                with col_name:
                    st.write(f"📊 {code} ({stock_names.get(code, '미등록')})")
                with col_delete:
                    if st.button("❌", key=f"delete_{code}", use_container_width=True):
                        Config.DEFAULT_STOCKS.remove(code)
                        st.success(f"✓ {code} 삭제됨")
                        st.rerun()

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**API 설정**")
            if Config.SAMSUNG_API_KEY:
                st.success("✓ API 키 설정됨")
            else:
                st.warning("⚠️ API 키 미설정")

        with col2:
            st.markdown("**데이터 설정**")
            retention_days = st.slider(
                "데이터 보관 기간 (일)",
                min_value=7,
                max_value=90,
                value=Config.RETENTION_DAYS,
                step=1
            )

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 데이터 정리", use_container_width=True):
                deleted = db.cleanup_old_data(retention_days)
                st.success(f"✓ {deleted}개의 오래된 데이터 삭제됨")

        with col2:
            if st.button("🔄 캐시 초기화", use_container_width=True):
                CacheService.clear_all_cache()
                st.success("✓ 캐시가 초기화되었습니다")

    # 하단 정보
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
    <p>📌 Phase 3: UI 개발 완성</p>
    <p>Ready for production deployment</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"App error: {e}")
        st.error(f"❌ 앱 오류: {e}")
