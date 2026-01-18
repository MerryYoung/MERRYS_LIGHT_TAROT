import streamlit as st
import requests
import json
import time

# --- 1. 페이지 설정 및 세션 초기화 ---
st.set_page_config(page_title="MYSTIC INSIGHT", layout="wide", initial_sidebar_state="collapsed")

if 'page' not in st.session_state: st.session_state.page = 'info'
if 'data' not in st.session_state: st.session_state.data = {}
if 'chosen' not in st.session_state: st.session_state.chosen = [] 

# 골드 테마 스타일 적용
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
                st.session_state.chosen = [] 
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

# --- [PAGE 4] 결과 (성공할 때까지 시도하는 스마트 로직) ---
elif st.session_state.page == 'result':
    d = st.session_state.data
    cols = st.columns(4)
    with cols[0]: st.markdown(f"<div class='info-box'><div class='label'>TARGET</div><div class='value'>{d['gen']} / {d['age']}</div></div>", unsafe_allow_html=True)
    with cols[1]: st.markdown(f"<div class='info-box'><div class='label'>CATEGORY</div><div class='value'>{d['cat']}</div></div>", unsafe_allow_html=True)
    with cols[2]: st.markdown(f"<div class='info-box'><div class='label'>MODE</div><div class='value'>{d['mode']}</div></div>", unsafe_allow_html=True)
    with cols[3]: st.markdown(f"<div class='info-box'><div class='label'>TOPIC</div><div class='value'>{d['que']}</div></div>", unsafe_allow_html=True)
    
    # AI에게 보낼 공통 질문 세팅
    prompt = f"당신은 20년 경력의 타로 마스터입니다. {d['gen']} {d['age']} 내담자의 {d['cat']} 질문 '{d['que']}'에 대해 카드 3장을 활용해 과거, 현재, 미래 리딩을 해주세요. 첫 줄은 제목을 강조해서 적어주세요."
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    # 시도해볼 주소 목록 (모든 에러 케이스 대응)
    url_list = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta/gemini-1.5-flash:generateContent?key={api_key}"
    ]
    
    success = False
    answer = ""
    last_error = ""

    # 반복문을 통해 성공할 때까지 주소를 바꿔가며 요청
    for url in url_list:
        try:
            res = requests.post(url, json=payload, timeout=15)
            res_data = res.json()
            if 'candidates' in res_data:
                answer = res_data['candidates'][0]['content']['parts'][0]['text']
                success = True
                break
            else:
                last_error = res_data.get('error', {}).get('message', 'Unknown Error')
        except Exception as e:
            last_error = str(e)

    if success:
        st.markdown(f"<div class='result-content'>{answer}</div>", unsafe_allow_html=True)
    else:
        st.error(f"지속적인 오류 발생: {last_error}")
        st.info("API 키가 올바른지, 혹은 구글 클라우드에서 Gemini API가 활성화되었는지 확인이 필요할 수 있습니다.")

    if st.button("처음으로"):
        st.session_state.page = 'info'
        st.rerun()
