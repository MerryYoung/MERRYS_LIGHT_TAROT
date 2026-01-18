import streamlit as st
import requests
import json
import time

# --- 1. 기본 설정 ---
st.set_page_config(page_title="MYSTIC INSIGHT", layout="wide", initial_sidebar_state="collapsed")

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

api_key = st.secrets.get("GEMINI_API_KEY", "")

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
    st.write(f"선택된 카드: {len(st.session_state.chosen)} / 3")
    cols = st.columns(6)
    for i in range(18):
        with cols[i % 6]:
            if st.button("?", key=f"card_{i}", disabled=i in st.session_state.chosen):
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

# --- [PAGE 4] 결과 (가장 안정적인 호출 방식) ---
elif st.session_state.page == 'result':
    d = st.session_state.data
    st.markdown(f"### {d['cat']} 리딩 결과")
    
    # API 호출 부분
    try:
        # 1. 주소에서 'models/'를 명시적으로 포함 (v1beta 기준 최신 규격)
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        # 2. 페이로드 구조를 구글 가이드라인에 100% 맞춤
        headers = {'Content-Type': 'application/json'}
        body = {
            "contents": [{
                "parts": [{"text": f"당신은 전문 타로 마스터입니다. {d['gen']} {d['age']} 내담자의 {d['cat']}에 대한 고민 '{d['que']}'을 타로 카드 3장으로 아주 상세하고 친절하게 리딩해주세요. 가독성 좋게 줄바꿈을 많이 사용하세요."}]
            }]
        }
        
        response = requests.post(api_url, headers=headers, data=json.dumps(body), timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            # 결과 파싱 시 안전하게 get() 사용
            answer = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '리딩 내용을 가져오지 못했습니다.')
            st.markdown(f"<div class='result-content'>{answer}</div>", unsafe_allow_html=True)
        else:
            st.error(f"서버 응답 오류 (코드: {response.status_code})")
            st.info("API 키가 유효한지 다시 확인해주세요.")
            
    except Exception as e:
        st.error(f"통신 중 오류가 발생했습니다: {str(e)}")

    if st.button("처음으로 돌아가기"):
        st.session_state.page = 'info'
        st.session_state.chosen = []
        st.rerun()
