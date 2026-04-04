import streamlit as st
import google.generativeai as genai
import requests

# 1. 예쁜 화면 꾸미기
st.set_page_config(page_title="반려동물 비서", page_icon="🐶")
st.title("🐾 멍냥이 콘텐츠 비서")
st.write("주인님, 오늘 어떤 글을 써서 워드프레스에 배달할까요?")

# 2. 비밀 정보 가져오기 (나중에 설정할 거예요)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
WP_URL = st.secrets["WP_URL"]
WP_USER = st.secrets["WP_USER"]
WP_APP_PW = st.secrets["WP_APP_PW"]

# Gemini 로봇 연결
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# 3. 명령 내리기
command = st.text_input("여기에 명령을 적어주세요", placeholder="예: 인기 있는 강아지 품종 5개 추천해줘")

if st.button("🚀 콘텐츠 마법 시작!"):
    with st.spinner("비서가 열심히 글을 쓰고 있어요... 잠시만 기다려주세요!"):
        # 글 쓰기 지시
        prompt = f"너는 반려동물 전문가야. '{command}' 주제로 블로그 글을 HTML 형식(h2, h3 사용)으로 아주 정성껏 써줘."
        response = model.generate_content(prompt)
        content = response.text
        
        st.success("✅ 글 작성이 완료되었습니다! 아래는 미리보기예요.")
        st.markdown(content, unsafe_allow_html=True)
        
      # 수정된 배달 코드 부분
if st.button("📦 이 글을 워드프레스로 배달하기"):
    auth = (WP_USER, WP_APP_PW)
    payload = {"title": command, "content": content, "status": "draft"}
    res = requests.post(WP_URL, auth=auth, json=payload)
    
    if res.status_code == 201:
        st.balloons()
        st.success("배달 성공!")
    else:
        # 배달 실패시 이유를 화면에 보여줌
        st.error(f"배달 실패! 에러 코드: {res.status_code}")
        st.write(res.text) # 왜 안됐는지 이유를 알려줍니다.
