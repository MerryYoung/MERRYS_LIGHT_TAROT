import streamlit as st
import google.generativeai as genai
import time

# --- [설정] 페이지 및 API 연결 ---
st.set_page_config(page_title="MYSTIC INSIGHT", layout="wide")

# 스트림릿 시크릿에서 키 가져오기
api_key = st.secrets.get("GEMINI_API_KEY", "")
genai.configure(api_key=api_key)

if 'page' not in st.session_state: st.session_state.page = 'info'
if 'data' not in st.session_state: st.session_state.data = {}
if 'chosen' not in st.session_state: st.session_state.chosen = []

# 디자인 스타일
st.markdown("""
    <style>
    .main { background-color: #050505; color: #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 8px; background: #8a6d3b; color: white; border: none; font-weight: bold; height: 45px; }
    .result-box { background: #161616; padding: 30px; border-radius: 15px; border: 1px solid #c09100; white-space: pre-wrap; line-height: 1.8; }
    </style>
""", unsafe_allow_html=True)

# --- [PAGE 1] 정보 입력 ---
if st.session_state.page == 'info':
    st.markdown("<h1 style='text-align: center; color: #c09100;'>MYSTIC INSIGHT</h1>", unsafe_allow_html=True)
    with st.container():
        cat = st.selectbox("카테고리", ["연애운", "재회운", "재물운", "사업운"])
        gender = st.selectbox("성별", ["여성", "남성"])
        age = st.selectbox("나이대", ["20대", "30대", "40대"])
        question = st.text_input("질문", placeholder="예: 언제쯤 인연이 나타날까요?")
        
        if st.button("운명 확인하기"):
            if not question: st.warning("질문을 입력해주세요.")
            else:
                st.session_state.data = {"cat": cat, "gen": gender, "age": age, "que": question}
                st.session_state.page = 'result'
                st.rerun()

# --- [PAGE 2] 결과 (공식 라이브러리 방식) ---
elif st.session_state.page == 'result':
    d = st.session_state.data
    st.markdown(f"<h2 style='text-align: center;'>{d['cat']} 리딩 결과</h2>", unsafe_allow_html=True)
    
    with st.spinner("운명의 메시지를 해석 중입니다..."):
        try:
            # 주소를 직접 적지 않고 모델명만 호출 (가장 안전한 방식)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"당신은 타로 마스터입니다. {d['gen']} {d['age']} 내담자의 {d['cat']} 질문 '{d['que']}'에 대해 카드 3장(과거, 현재, 미래)을 사용해 정중하고 상세하게 리딩해주세요."
            
            response = model.generate_content(prompt)
            
            if response.text:
                st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)
            else:
                st.error("답변 생성에 실패했습니다.")

        except Exception as e:
            st.error(f"시스템 오류가 발생했습니다: {str(e)}")
            st.info("API 키가 올바른지 다시 확인해 주세요.")

    if st.button("처음으로 돌아가기"):
        st.session_state.page = 'info'
        st.rerun()
