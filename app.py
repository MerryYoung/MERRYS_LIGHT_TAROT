import streamlit as st
import google.generativeai as genai
import time

# --- 1. 초기 설정 및 API 연결 ---
st.set_page_config(page_title="MYSTIC INSIGHT", layout="wide", initial_sidebar_state="collapsed")

# API 키 설정 (공식 라이브러리 방식)
api_key = st.secrets.get("GEMINI_API_KEY", "")
genai.configure(api_key=api_key)

if 'page' not in st.session_state: st.session_state.page = 'info'
if 'data' not in st.session_state: st.session_state.data = {}
if 'chosen' not in st.session_state: st.session_state.chosen = [] 

# 스타일 정의
st.markdown("""
    <style>
    .main { background-color: #050505; color: #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 8px; background: #8a6d3b; color: white; border: none; font-weight: bold; height: 45px; }
    .info-box { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; margin-bottom: 10px;}
    .label { color: #888; font-size: 0.8rem; }
    .value { color: #c09100; font-weight: bold; font-size: 1rem; }
    .result-content { background: #161616; padding: 30px; border-radius: 15px; line-height: 1.8; border: 1px solid #222; white-space: pre-wrap; font-size: 1.1rem; color: #f0f0f0; }
    </style>
""", unsafe_allow_html=True)

# --- [PAGE 1] 정보 입력 ---
if st.session_state.page == 'info':
    st.markdown("<h1 style='text-align: center; color: #c09100;'>MYSTIC INSIGHT</h1>", unsafe_allow_html=True)
    with st.container():
        mode = st.radio("상담 모드", ["무료 상담", "유료 정밀 상담"], horizontal=True)
        category = st.selectbox("운세 카테고리", ["연애운", "재회운", "재물운", "사업/직장운", "건강운", "학업운"])
        c1, c2 = st.columns(2)
        gender = c1.selectbox("성별", ["여성", "남성", "기타"])
        age = c2.selectbox("나이대", ["10대", "20대", "30대", "40대", "50대 이상"])
        question = st.text_input("질문 내용 (필수)", placeholder="예: 언제 애인이 생길까요?")
        
        if st.button("카드 뽑기로 이동"):
            if not question: st.warning("질문을 입력해주세요.")
            else:
                st.session_state.data = {"mode": mode, "cat": category, "gen": gender, "age": age, "que": question}
                st.session_state.page = 'shuffle'
                st.rerun()

# --- [PAGE 2] 카드 셔플 ---
elif st.session_state.page == 'shuffle':
    st.markdown("<h2 style='text-align: center; color: #c09100;'>THE DECK OF FATE</h2>", unsafe_allow_html=True)
    st.write(f"현재 선택된 카드: {len(st.session_state.chosen)} / 3")
    cols = st.columns(6)
    for i in range(18):
        with cols[i % 6]:
            is_selected = i in st.session_state.chosen
            if st.button(f"{'★' if is_selected else '?'}", key=f"c_{i}", disabled=is_selected):
                st.session_state.chosen.append(i)
                if len(st.session_state.chosen) >= 3:
                    st.session_state.page = 'loading'
                st.rerun()

# --- [PAGE 3] 로딩 ---
elif st.session_state.page == 'loading':
    st.markdown("<br><br><h2 style='text-align: center; color: #c09100;'>DECRYPTING AURA</h2>", unsafe_allow_html=True)
    bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        bar.progress(i + 1)
    st.session_state.page = 'result'
    st.rerun()

# --- [PAGE 4] 결과 (가장 안전한 라이브러리 호출 방식) ---
elif st.session_state.page == 'result':
    d = st.session_state.data
    st.markdown(f"<h3 style='color:#c09100;'>{d['cat']} 리딩 결과</h3>", unsafe_allow_html=True)
    
    try:
        # 모델 설정 (공식 라이브러리가 경로를 알아서 찾아줍니다)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        당신은 신비롭고 통찰력 있는 타로 마스터입니다. 
        내담자({d['gen']}, {d['age']})가 '{d['que']}'라는 질문을 가지고 카드 3장을 뽑았습니다.
        이 상황에 대해 과거, 현재, 미래의 흐름을 분석하여 매우 구체적이고 따뜻하게 리딩해 주세요.
        가독성을 위해 문단 사이에 줄바꿈을 많이 넣어주세요.
        """
        
        # 답변 생성
        response = model.generate_content(prompt)
        
        if response.text:
            st.markdown(f"<div class='result-content'>{response.text}</div>", unsafe_allow_html=True)
        else:
            st.error("AI가 답변을 생성하지 못했습니다. 다시 시도해 주세요.")
            
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
        st.info("API 키 설정이 올바른지 다시 한번 확인 부탁드립니다.")
    
    if st.button("처음으로"):
        st.session_state.page = 'info'
        st.session_state.chosen = []
        st.rerun()
