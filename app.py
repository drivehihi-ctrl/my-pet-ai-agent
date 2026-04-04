import streamlit as st
import google.generativeai as genai
import requests

# 1. 화면 설정
st.set_page_config(page_title="반려동물 비서 PRO", page_icon="🐶")
st.title("🐾 멍냥이 콘텐츠 & 이미지 비서")

# 2. 비밀 정보 가져오기
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
WP_URL = st.secrets["WP_URL"]
WP_USER = st.secrets["WP_USER"]
WP_APP_PW = st.secrets["WP_APP_PW"]

# [절대 고정] 주인님 지시대로 'gemini-flash-latest' 모델만 사용합니다.
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# 3. 비서의 기억장치 (세션 스테이트 - 절대 삭제 금지)
if "generated_content" not in st.session_state:
    st.session_state.generated_content = ""
if "image_prompts" not in st.session_state:
    st.session_state.image_prompts = []

# 4. 명령 내리기
command = st.text_input("주제 입력", placeholder="예: 강아지 슬개골 탈구 자가진단법")

if st.button("🚀 콘텐츠 & 이미지 프롬프트 제작!"):
    with st.spinner("이미지 위치를 지정하며 글을 작성 중입니다..."):
        # 기존 SEO 지침에 '이미지 위치 표시' 지침을 강력하게 추가했습니다.
        full_prompt = f"""
        너는 반려동물 전문 블로거이자 전문 사진작가야. 
        주제: '{command}'
        
        [과업 1: 블로그 글 작성]
        - <h2>, <h3> 태그를 사용한 SEO 구조화된 HTML로 작성해.
        - 전문적이고 신뢰감 있는 E-E-A-T 스타일로 작성할 것.
        - **중요**: 글의 흐름상 적절한 위치에 [이미지 1], [이미지 2], [이미지 3], [이미지 4]라는 문구를 본문에 직접 삽입해.
        - 각 이미지 표시는 단락 사이사이에 배치하여 시각적 이해를 도와야 해.

        [과업 2: 실사 이미지 프롬프트 4개 제작]
        - 본문에 표시한 [이미지 1~4]에 각각 대응하는 영문 프롬프트를 작성해줘.
        - 모든 이미지는 반드시 '완벽한 실사(Hyper-realistic, Photorealistic)'여야 해.
        
        결과 형식 (반드시 지킬 것):
        ---CONTENT---
        (본문 내용 중 적절한 곳에 [이미지 1] 등이 포함된 블로그 내용)
        ---IMAGES---
        이미지 1: (영문 프롬프트)
        이미지 2: (영문 프롬프트)
        이미지 3: (영문 프롬프트)
        이미지 4: (영문 프롬프트)
        """
        
        response = model.generate_content(full_prompt)
        full_text = response.text
        
        # 결과 나누기
        if "---CONTENT---" in full_text and "---IMAGES---" in full_text:
            parts = full_text.split("---IMAGES---")
            st.session_state.generated_content = parts[0].replace("---CONTENT---", "").strip()
            st.session_state.image_prompts = [line for line in parts[1].strip().split("\n") if line.strip()]
        else:
            st.session_state.generated_content = full_text
            st.session_state.image_prompts = ["프롬프트 생성 오류"]

        st.success("✅ 제작 완료!")

# 5. 결과 화면 보여주기
if st.session_state.generated_content:
    st.markdown("### 📝 작성된 SEO 블로그 글 (이미지 위치 포함)")
    # 본문의 [이미지 X]를 강조해서 보여주기 위해 살짝 가공해서 출력
    display_content = st.session_state.generated_content.replace("[이미지", "<b style='color:red;'>[이미지")
    st.markdown(display_content, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📸 실사 이미지 생성용 프롬프트")
    for p in st.session_state.image_prompts:
        st.code(p)
        
    if st.button("📦 이 원고를 워드프레스 창고로 배달하기"):
        auth = (WP_USER, WP_APP_PW)
        payload = {
            "title": command, 
            "content": st.session_state.generated_content, 
            "status": "draft"
        }
        res = requests.post(WP_URL, auth=auth, json=payload)
        
        if res.status_code == 201:
            st.balloons()
            st.success("주인님! 이미지 위치까지 지정된 원고가 배달되었습니다! 💌")
        else:
            st.error(f"배달 실패! (에러 코드: {res.status_code})")
