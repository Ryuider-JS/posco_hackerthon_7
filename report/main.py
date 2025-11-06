import streamlit as st
import time

# --- 1. AI 에이전트 API 호출 시뮬레이션 ---
# @st.cache_data: 이 함수는 입력값(report_id)이 동일하면
# 이전에 실행한 결과를 캐시했다가 즉시 반환합니다.
# 실제 API 호출 시 네트워크 비용을 절약하고 앱 속도를 향상시킵니다.
@st.cache_data
def fetch_ai_report() -> str:
    """
    지정된 report_id를 기반으로 AI 에이전트 API를 호출한다고 가정하는 함수.
    실제 구현 시 이 부분에 `requests.get(...)` 등의 로직이 들어갑니다.
    """
    print(f"--- API 호출 실행--- ")
    
    # API 호출에 시간이 걸리는 것을 시뮬레이션
    time.sleep(2) 
    
    # AI가 마크다운 형식의 텍스트를 반환했다고 가정
    report_text = f"""
    

    ## 1. 종합 요약
    
    본 리포트는 000 항목에 대한 심층 분석 결과를 제공합니다. 
    분석 결과, 긍정적인 신호가 70%, 주의가 필요한 신호가 30%로 감지되었습니다.

    - **주요 긍정 요인:**
        - 시장 점유율 지속적 증가
        - 신규 유저 유입률 20% 상승
    - **주요 리스크 요인:**
        - 경쟁사 신제품 출시
        - 운영 비용 소폭 증가

    ## 2. 상세 데이터 분석

    ### 2.1. 사용자 동향
    최근 30일간 사용자 유입 경로는 다음과 같습니다.
    
    | 유입 경로 | 비율 | 전월 대비 |
    | :--- | :---: | :---: |
    | 오가닉 검색 | 45% | +5% |
    | 소셜 미디어 | 30% | +2% |
    | 유료 광고 | 25% | -7% |

    ### 2.2. 감성 분석 (Sentiment)
    관련 소셜 데이터에서 "만족", "추천"과 같은 긍정 키워드가 15% 증가했습니다. 
    반면, "불편", "오류"와 같은 부정 키워드는 3% 감소하여 전반적인 사용자 만족도가 
    개선된 것으로 보입니다.

    ## 3. 결론 및 제언
    
    종합적으로 볼 때,  항목은 긍정적인 성장 궤도에 있습니다. 
    유료 광고 효율성 개선에 집중하고, 감지된 리스크 요인을 지속적으로 
    모니터링할 것을 권장합니다.
    """
    return report_text

# --- 2. Streamlit 앱 메인 페이지 구성 ---

# 페이지 설정을 넓은 레이아웃으로 변경
st.set_page_config(page_title="AI 분석 리포트", layout="wide")

# --- 2.1. 커스텀 CSS 스타일 적용 ---
st.markdown(f"""
<style>
/* 메인 타이틀 (h1) */
[data-testid="stAppViewContainer"] h1 {{
    color: #003B5C; /* Main Color */
}}

/* 마크다운 헤더 (h2, h3) */
[data-testid="stAppViewContainer"] h2, 
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h5,
[data-testid="stAppViewContainer"] h6 {{
    color: #336B87; /* Sub Color */
}}

/* 사이드바 배경 */
[data-testid="stSidebar"] {{
    background-color: #003B5C; /* Main Color */
}}

/* 사이드바 헤더 */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6 {{
    color: #FFFFFF; /* White text for contrast */
}}

/* 사이드바 일반 텍스트 (캡션 포함) */
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stText,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] p {{
    color: #FFFFFF; /* White text for contrast */
}}



/* 스피너 텍스트 */
.stSpinner > div {{
    color: #336B87 !important; /* Sub Color */
}}

/* Expander (펼치기) 텍스트 */
.st-expander summary {{
    color: #336B87; /* Sub Color */
}}

</style>
""", unsafe_allow_html=True)
# --- ---------------------- ---


st.title("AI 에이전트 분석 리포트 📄")
st.caption("AI가 생성한 텍스트를 기반으로 자동 생성된 페이지입니다.")

# --- 3. 메인 로직 실행 (페이지 로드 시 즉시) ---
# 페이지가 로드되면 항상 API를 호출하도록 변경
# (쿼리 파라미터 로직 제거)

# 고정된 리포트 ID를 사용하거나, API가 ID를 요구하지 않는다면 None
# 여기서는 시뮬레이션을 위해 고정 ID 사용

# 사이드바에 현재 리포트 ID 표시
st.sidebar.header("리포트 정보")


# 페이지가 로드되면 스피너를 표시하며 API 호출 함수 실행
with st.spinner(f"000 리포트 데이터를 불러오는 중..."):
    try:
        # 캐시된 함수 호출 (실제 API 요청 시뮬레이션)
        report_data = fetch_ai_report()
        
        # AI가 반환한 마크다운 텍스트를 페이지에 렌더링
        st.markdown(report_data)

        # AI가 반환한 원본 텍스트를 확인하고 싶을 경우를 대비
        with st.expander("AI 원본 응답 (Raw Text) 보기"):
            st.text(report_data)

    except Exception as e:
        st.error(f"리포트를 불러오는 중 오류가 발생했습니다: {e}")