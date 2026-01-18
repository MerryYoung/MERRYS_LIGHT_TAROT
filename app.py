import streamlit as st
import requests
import json
import time

# --- 1. 페이지 설정 및 세션 초기화 ---
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

# --- [PAGE 4] 결과 (에러 원천 차단 로직) ---
elif st.session_state.page == 'result':
    d = st.session_state.data
    cols = st.columns(4)
    with cols[0]: st.markdown(f"<div class='info-box'><div class='label'>TARGET</div><div class='value'>{d['gen']} / {d['age']}</div></div>", unsafe_allow_html=True)
    with cols[1]: st.markdown(f"<div class='info-box'><div class='label'>CATEGORY</div><div class='value'>{d['cat']}</div></div>", unsafe_allow_html=True)
    with cols[2]: st.markdown(f"<div class='info-box'><div class='label'>MODE</div><div class='value'>{d['mode']}</div></div>", unsafe_allow_html=True)
    with cols[3]: st.markdown(f"<div class='info-box'><div class='label'>TOPIC</div><div class='value'>{d['que']}</div></div>", unsafe_allow_html=True)
    
    try:
        # [해결책] 구글 API의 가장 표준적인 엔드포인트와 데이터 구조 사용
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"당신은 품격 있는 타로 마스터입니다. 내담자({d['gen']}, {d['age']})의 {d['cat']} 질문 '{d['que']}'에 대해 카드 3장을 활용해 과거, 현재, 미래 관점에서 깊이 있는 리딩을 제공하세요. 첫 줄은 강렬한 제목을 달아주세요."}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 1000
            }
        }
        
        # 실제 요청 및 에러 핸들링
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            res_json = response.json()
            if 'candidates' in res_json:
                answer = res_json['candidates'][0]['content']['parts'][0]['text']
                st.markdown(f"<div class='result-content'>{answer}</div>", unsafe_allow_html=True)
            else:
                st.error("AI가 답변을 생성하지 못했습니다. 질문 내용을 조금 더 구체적으로 적어주세요.")
        else:
            # 에러 발생 시 상세 정보 노출 (디버깅용)
            st.error(f"통신 에러가 발생했습니다. (Code: {response.status_code})")
            with st.expander("에러 상세 내용 보기"):
                st.write(response.text)

    except Exception as e:
        st.error(f"시스템 오류: {str(e)}")
    
    if st.button("처음으로"):
        st.session_state.page = 'info'
        st.rerun()
