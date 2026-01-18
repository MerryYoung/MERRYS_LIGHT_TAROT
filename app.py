import streamlit as st
import requests
import json
import time

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="MYSTIC INSIGHT", layout="wide", initial_sidebar_state="collapsed")

# 고급스러운 다크 골드 테마 적용
st.markdown("""
    <style>
    .main { background-color: #050505; color: #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 8px; background: linear-gradient(135deg, #c09100, #8a6d3b); color: white; border: none; font-weight: bold; padding: 10px; }
    .info-box { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; }
    .label { color: #888; font-size: 0.8rem; margin-bottom: 5px; }
    .value { color: #c09100; font-weight: bold; font-size: 1rem; }
    .result-content { background: #161616; padding: 30px; border-radius: 15px; line-height: 1.8; border: 1px solid #222; }
    </style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")

# 세션 상태 초기화
if 'page' not in st.session_state: st.session_state.page = 'info'
if 'data' not in st.session_state: st.session_state.data = {}

# --- [PAGE 1] 상담 정보 입력 ---
if st.session_state.page == 'info':
    st.markdown("<h1 style='text-align: center; color: #c09100;'>MYSTIC INSIGHT</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>PREMIUM TAROT COUNSELING SERVICE</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("### 상담 기본 정보")
        mode = st.radio("상담 모드", ["무료 상담", "유료 정밀 상담"], horizontal=True)
        category = st.selectbox("운세 카테고리", ["연애운", "재회운", "재물운", "사업/직장운", "건강운", "학업운"])
        
        c1, c2 = st.columns(2)
        gender = c1.selectbox("성별", ["여성", "남성", "기타"])
        age = c2.selectbox("나이대", ["10대", "20대", "30대", "40대", "50대 이상"])
        
        situation = st.text_area("현재 상황 (선택)", placeholder="상대방과의 관계나 구체적인 정황을 적어주세요.")
        question = st.text_input("질문 내용 (필수)", placeholder="예: 언제 애인이 생길까요?")
        
        if st.button("카드 뽑기로 이동"):
            if not question: st.warning("질문을 입력해주세요.")
            else:
                st.session_state.data = {"mode": mode, "cat": category, "gen": gender, "age": age, "sit": situation, "que": question}
                st.session_state.page = 'shuffle'
                st.rerun()

# --- [PAGE 2] 카드 셔플 ---
elif st.session_state.page == 'shuffle':
    st.markdown("<h2 style='text-align: center; color: #c09100;'>THE DECK OF FATE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>무의식이 이끄는 카드 3장을 차례로 골라주세요.</p>", unsafe_allow_html=True)
    
    cols = st.columns(6)
    for i in range(18):
        with cols[i % 6]:
            if st.button("?", key=f"c_{i}"):
                st.session_state.page = 'loading'
                st.rerun()

# --- [PAGE 3] DECRYPTING AURA 로딩 ---
elif st.session_state.page == 'loading':
    st.markdown("<br><br><h2 style='text-align: center; letter-spacing: 5px; color: #c09100;'>DECRYPTING AURA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>내담자님의 에너지를 정밀하게 분석 중입니다...</p>", unsafe_allow_html=True)
    bar = st.progress(0)
    for i in range(100):
        time.sleep(0.015)
        bar.progress(i + 1)
    st.session_state.page = 'result'
    st.rerun()

# --- [PAGE 4] 결과 리딩 ---
elif st.session_state.page == 'result':
    d = st.session_state.data
    
    # 상단 요약 바 (이미지 626449.png 스타일)
    cols = st.columns(4)
    with cols[0]: st.markdown(f"<div class='info-box'><div class='label'>TARGET</div><div class='value'>{d['gen']} / {d['age']}</div></div>", unsafe_allow_html=True)
    with cols[1]: st.markdown(f"<div class='info-box'><div class='label'>CATEGORY</div><div class='value'>{d['cat']}</div></div>", unsafe_allow_html=True)
    with cols[2]: st.markdown(f"<div class='info-box'><div class='label'>MODE</div><div class='value' style='color:#4caf50;'>{d['mode']}</div></div>", unsafe_allow_html=True)
    with cols[3]: st.markdown(f"<div class='info-box'><div class='label'>TOPIC</div><div class='value'>{d['que']}</div></div>", unsafe_allow_html=True)
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        prompt = f"""
        당신은 타로 마스터입니다. 78장 타로 카드 중 3장을 뽑아 리딩하세요.
        상담정보: {d['gen']} {d['age']}, 주제: {d['cat']}, 질문: {d['que']}, 상황: {d['sit']}
        [요약] 리딩 제목을 큰따옴표 안에 임팩트 있게 작성할 것.
        [리딩] 과거, 현재, 미래 카드를 설명하고 다정한 말투로 상세히 리딩할 것.
        [전환] {d['mode']}가 무료면 마지막에 '더 깊은 조언은 유료 정밀 상담에서 가능합니다'라고 자연스럽게 언급할 것.
        """
        
        res = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}))
        ans = res.json()['candidates'][0]['content']['parts'][0]['text']
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-content'>{ans}</div>", unsafe_allow_html=True)
        
    except: st.error("리딩 정보를 불러오는 중 오류가 발생했습니다.")
    
    if st.button("처음으로"):
        st.session_state.page = 'info'
        st.rerun()
