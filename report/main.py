import os
import boto3
import requests
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import altair as alt

load_dotenv()

@st.cache_data
def fetch_ai_report(q_code: str = "Q12345") -> str:
    dynamodb = boto3.client(
      'dynamodb',
      region_name=os.getenv('AWS_REGION'),
      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    )

    response = dynamodb.query(
      TableName='TargetPriceTB',
      KeyConditionExpression='qcode = :q',
      ExpressionAttributeValues={
        ':q': {'S': q_code}  
      },
      ScanIndexForward=False,  
      Limit=1                  
  ) 
    item = response.get('Items')[0]
    render_report(item)

def render_report(item):
    st.markdown("""
    <style>
    .report-box {
        border: 2px solid #003B5C;
        border-radius: 12px;
        padding: 20px 30px;
        background-color: #f9fbfc;
        margin-bottom: 25px;
    }
    .report-title {
        background-color: #003B5C;
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 18px;
        margin-bottom: 10px;
    }
    table.custom {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    table.custom th {
        background-color: #e6eef2;
        color: #003B5C;
        text-align: center;
        padding: 6px;
        border: 1px solid #cccccc;
    }
    table.custom td {
        text-align: center;
        padding: 6px;
        border: 1px solid #dddddd;
    }
    </style>
    """, unsafe_allow_html=True)

    price_list = item["가격비교표"]["L"]
    rows = []
    for entry in price_list:
        m = entry["M"]
        rows.append({
            "제조사": m["제조사"]["S"],
            "모델": m["모델"]["S"],
            "사양": m["사양"]["S"],
            "KRW 환산": m["KRW환산"]["S"],
            "MOQ / 리드타임": m["MOQ_리드타임"]["S"],
            "출처 URL": f"<a href='{m['출처URL']['S']}' target='_blank'>링크</a>"
        })
    df = pd.DataFrame(rows)

    html_table = df.to_html(escape=False, index=False, classes="custom")

    st.markdown(f"""
    <div class="report-box">
        <div class="report-title">시장가 비교표</div>
        {html_table}
    </div>
    """, unsafe_allow_html=True)

    stats = item["통계요약"]["M"]
    st.markdown(f"""
    <div class="report-box">
        <div class="report-title">통계 요약</div>
        <table class="custom">
            <tr><th>가중 중앙값</th><th>IQR (P25~P75)</th><th>권장 협상 밴드</th></tr>
            <tr>
                <td>{stats["가중중앙값"]["S"]}</td>
                <td>{stats["IQR_P25_P75"]["S"]}</td>
                <td>{stats["권장협상밴드"]["S"]}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=30)


    url = (
        f"https://api.apilayer.com/exchangerates_data/timeseries"
        f"?start_date={start_date}&end_date={end_date}&base=USD&symbols=KRW"
    )

    headers = {
        "apikey": os.getenv('APILAYER_ACCESS_KEY'),
    }
    # 3. API 요청
    response = requests.get(url, headers=headers)
    data = response.json()

    if data.get("success", False):
        rates = data["rates"]

    # DataFrame 생성
        df = pd.DataFrame([
            {"날짜": date, "환율(KRW/USD)": rates[date]["KRW"]}
            for date in sorted(rates.keys())
        ])

    # 날짜형 변환
        df["날짜"] = pd.to_datetime(df["날짜"])

    # Streamlit 꺾은선 그래프 표시
        st.subheader("📈 최근 1개월 USD → KRW 환율 추이")
        min_y = df["환율(KRW/USD)"].min()
        max_y = df["환율(KRW/USD)"].max()

        chart = alt.Chart(df).mark_line(point=True).encode(
            x="날짜:T",
            y=alt.Y("환율(KRW/USD):Q", scale=alt.Scale(domain=[min_y - 5, max_y + 5])),
            tooltip=["날짜", alt.Tooltip("환율(KRW/USD):Q", format=".2f")]
        ).properties(
            title="최근 1개월 원/달러 환율 추이",
            height=400
        )

        st.altair_chart(chart, use_container_width=True)
    else:
        st.error(f"데이터를 불러오지 못했습니다.\n{data}")

    insight = item["전략적구매인사이트"]["M"]
    st.markdown(f"""
    <div class="report-box">
        <div class="report-title">전략적 구매 인사이트</div>
        <table class="custom">
            <tr><th>시장 동향</th><td>{insight["시장동향"]["S"]}</td></tr>
            <tr><th>가격 포지셔닝</th><td>{insight["가격포지셔닝"]["S"]}</td></tr>
            <tr><th>조달 리스크</th><td>{insight["조달리스크"]["S"]}</td></tr>
            <tr><th>전략 제언</th><td>{insight["전략제언"]["S"]}</td></tr>
            <tr><th>권장 조치</th><td>{insight["권장조치"]["S"]}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

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

# query parameter에서 qcode 가져오기
q_code = st.query_params.get("qcode")

if not q_code:
    st.error("⚠️ qcode가 필요합니다. URL에 ?qcode=값을 추가해주세요.")
    st.info("예시: https://poscohackerthon-report.streamlit.app?qcode=123")
    st.stop()

# 페이지가 로드되면 스피너를 표시하며 API 호출 함수 실행
with st.spinner(f"{q_code} 리포트 데이터를 불러오는 중..."):
    try:
        report_data = fetch_ai_report(q_code)

    except Exception as e:
        st.error(f"리포트를 불러오는 중 오류가 발생했습니다: {e}")
