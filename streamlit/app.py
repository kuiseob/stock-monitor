import streamlit as st
import sys
import os
from pathlib import Path

# 부모 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="Stock Monitor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """세션 상태 초기화"""
    if "connected" not in st.session_state:
        st.session_state.connected = False
    if "stock_data" not in st.session_state:
        st.session_state.stock_data = {}
    if "client" not in st.session_state:
        st.session_state.client = None

def main():
    """메인 앱"""
    init_session_state()

    # 사이드바
    with st.sidebar:
        st.title("📊 Stock Monitor")
        st.markdown("---")

        # 상태 표시
        if st.session_state.connected:
            st.markdown('<span class="status-connected">✓ Connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-disconnected">✗ Disconnected</span>', unsafe_allow_html=True)

        st.markdown("---")

        # 종목 선택
        st.subheader("📌 모니터링 종목")
        stock_names = Config.get_stock_names()
        default_stocks = Config.DEFAULT_STOCKS[:5]  # 최대 5개

        selected_codes = st.multiselect(
            "종목 선택 (최대 5개)",
            options=Config.DEFAULT_STOCKS,
            default=default_stocks,
            max_selections=5,
            format_func=lambda x: f"{x} - {stock_names.get(x, '미등록')}"
        )

        st.markdown("---")

        # 앱 정보
        with st.expander("ℹ️ 정보"):
            st.markdown("""
            **삼성증권 API 기반**
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
        st.metric("모니터링 종목", f"{len(selected_codes)}/5")
    with col2:
        st.metric("연결 상태", "🟢 연결됨" if st.session_state.connected else "🔴 미연결")
    with col3:
        st.metric("데이터 수집", "활성화" if st.session_state.connected else "중지됨")
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
        if not selected_codes:
            st.warning("모니터링할 종목을 선택해주세요.")
        else:
            st.info(f"선택된 종목: {', '.join([f'{code} ({stock_names.get(code)})' for code in selected_codes])}")

            # 종목별 카드
            cols = st.columns(min(len(selected_codes), 3))
            for idx, code in enumerate(selected_codes):
                with cols[idx % 3]:
                    st.subheader(f"{stock_names.get(code, code)}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("현재가", "- 원", delta=None, help="API 연결 후 표시됩니다")
                    with col2:
                        st.metric("등락률", "- %", delta=None, help="API 연결 후 표시됩니다")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("외국인 순매수", "- 주", help="API 연결 후 표시됩니다")
                    with col2:
                        st.metric("기관 순매수", "- 주", help="API 연결 후 표시됩니다")

    with tab2:
        st.subheader("차트 및 분석")
        st.info("🔄 현재 데이터 수집 중입니다. 차트는 충분한 데이터가 수집된 후 표시됩니다.")

        # 차트 영역 (향후 구현)
        st.markdown("""
        **구현 예정 기능:**
        - 시간별 가격 차트 (24시간)
        - 외국인/기관 매매량 추이
        - 거래량 분석
        - 기술적 지표
        """)

    with tab3:
        st.subheader("과거 데이터")
        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input("시작 날짜")
        with col2:
            to_date = st.date_input("종료 날짜")

        st.info("📊 데이터 수집이 충분히 진행된 후 과거 데이터 조회가 가능합니다.")

    with tab4:
        st.subheader("설정")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**API 설정**")
            st.text_input("API 키", value="••••••••", type="password", disabled=True)
            st.text_input("계좌 ID", value="••••••••", type="password", disabled=True)

        with col2:
            st.markdown("**데이터 설정**")
            retention_days = st.slider("데이터 보관 기간 (일)", 7, 90, 30)
            update_interval = st.select_slider(
                "업데이트 간격 (초)",
                options=[1, 2, 5, 10],
                value=1
            )

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 재연결", use_container_width=True):
                st.info("재연결 기능은 Phase 2에서 구현됩니다.")
        with col2:
            if st.button("💾 데이터 정리", use_container_width=True):
                st.info("데이터 정리 기능은 Phase 2에서 구현됩니다.")
        with col3:
            if st.button("🔄 초기화", use_container_width=True):
                st.info("초기화 기능은 Phase 2에서 구현됩니다.")

    # 하단 정보
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
    <p>📌 Phase 1: 기본 인프라 완성</p>
    <p>다음 단계: API 연결 및 실시간 데이터 수집 구현</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"App error: {e}")
        st.error(f"❌ 앱 오류: {e}")
