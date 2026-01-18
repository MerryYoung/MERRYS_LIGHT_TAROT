import streamlit as st
import requests
import json
import time

# --- 1. 페이지 설정 및 세션 상태 초기화 ---
st.set_page_config(page_title="MYSTIC INSIGHT", layout="wide", initial_sidebar_state="collapsed")

if 'page' not in st.session_state: st.session_state.page = 'info'
if 'data' not in st.session_state: st.session_state.data = {}
if 'chosen' not in st.session_state: st.session_state.chosen = [] 

# 스타일 정의 (골드 테마 재현)
st.markdown("""
    <style>
    .main { background-color: #050505; color: #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 8px; background: #8a6d3b; color: white; border: none; font-weight: bold; }
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
    st.markdown("<h2 style='text-align: center; color: #c09100;'>DECRYPTING AURA</h2>", unsafe_allow_html=True)
    bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        bar.progress(i + 1)
    st.session_state.page = 'result'
    st.rerun()

# --- [PAGE 4] 결과 (가장 많이 수정된 구간) ---
elif st.session_state.page == 'result':
    d = st.session_state.data
    cols = st.columns(4)
    with cols[0]: st.markdown(f"<div class='info-box'><div class='label'>TARGET</div><div class='value'>{d['gen']} / {d['age']}</div></div>", unsafe_allow_html=True)
    with cols[1]: st.markdown(f"<div class='info-box'><div class='label'>CATEGORY</div><div class='value'>{d['cat']}</div></div>", unsafe_allow_html=True)
    with cols[2]: st.markdown(f"<div class='info-box'><div class='label'>MODE</div><div class='value'>{d['mode']}</div></div>", unsafe_allow_html=True)
    with cols[3]: st.markdown(f"<div class='info-box'><div class='label'>TOPIC</div><div class='value'>{d['que']}</div></div>", unsafe_allow_html=True)
    
    try:
        # 1. 주소 및 데이터(payload) 설정
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        prompt_text = f"""
        당신은 20년 경력의 타로 마스터입니다. 
        내담자 정보: {d['gen']} {d['age']}, 주제: {d['cat']}, 질문: {d['que']}
        
        유니버셜 웨이트 78장 타로 카드 중 무작위로 3장을 선택하여 과거, 현재, 미래 관점에서 리딩해주세요.
        리딩 제목을 첫 줄에 "큰따옴표"와 함께 아주 강렬하게 적어주시고, 
        내담자의 마음을 어루만지는 품격 있는 말투로 아주 상세하게 작성하세요.
        {d['mode']}가 '무료 상담'인 경우 마지막에 '더 디테일한 미래 조언은 유료 정밀 상담에서 확인 가능하다'는 멘트를 자연스럽게 넣으세요.
        """
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt_text
                }]
            }]
        }
        
        # 2. API 호출
        res = requests.post(
            url, 
            headers={'Content-Type': 'application/json'}, 
            data=json.dumps(payload), 
            timeout=15
        )
        res_data = res.json()
        
        # 3. 결과 출력 로직
        if 'candidates' in res_data:
            ans = res_data['candidates'][0]['content']['parts'][0]['text']
            st.markdown(f"<div class='result-content'>{ans}</div>", unsafe_allow_html=True)
            st.button("전체 복사 (기능은 추후 보강)")
        else:
            st.error(f"AI 응답 오류: {res_data.get('error', {}).get('message', '알 수 없는 오류')}")
            st.write("상세 에러 내용:", res_data) 
            
    except Exception as e:
        st.error(f"통신 중 예기치 못한 오류 발생: {str(e)}")
    
    if st.button("처음으로"):
        st.session_state.page = 'info'
        st.rerun()
