import streamlit as st
import google.generativeai as genai
import requests

# 1. 화면 설정
st.set_page_config(page_title="반려동물 비서", page_icon="🐶")
st.title("🐾 멍냥이 콘텐츠 비서")

# 2. 비밀 정보 가져오기
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
WP_URL = st.secrets["WP_URL"]
WP_USER = st.secrets["WP_USER"]
WP_APP_PW = st.secrets["WP_APP_PW"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# 3. 비서가 글을 기억하게 하는 장치 (중요!)
if "generated_content" not in st.session_state:
    st.session_state.generated_content = ""

# 4. 명령 내리기
command = st.text_input("주제 입력", placeholder="예: 푸들 성격 3가지")

if st.button("🚀 콘텐츠 마법 시작!"):
    with st.spinner("글 쓰는 중..."):
        prompt = f"너는 반려동물 전문가야. '{command}' 주제로 블로그 글을 HTML 형식(h2, h3 사용)으로 정성껏 써줘."
        response = model.generate_content(prompt)
        # 쓴 글을 기억장치에 저장!
        st.session_state.generated_content = response.text
        st.success("✅ 작성이 완료되었습니다!")

# 5. 글이 있을 때만 화면에 보여주고 배달하기
if st.session_state.generated_content:
    st.markdown("---")
    st.markdown(st.session_state.generated_content, unsafe_allow_html=True)
    
    if st.button("📦 이 글을 워드프레스로 배달하기"):
        auth = (WP_USER, WP_APP_PW)
        # 기억장치에 있는 글을 꺼내서 배달!
        payload = {
            "title": command, 
            "content": st.session_state.generated_content, 
            "status": "draft"
        }
        res = requests.post(WP_URL, auth=auth, json=payload)
        
        if res.status_code == 201:
            st.balloons()
            st.success("주인님! 워드프레스 창고(임시저장)에 무사히 배달했습니다! 💌")
        else:
            st.error(f"배달 실패! 에러: {res.status_code}")
            st.write(res.text)
