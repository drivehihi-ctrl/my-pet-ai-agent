import streamlit as st
import google.generativeai as genai
import requests
import re

# 1. 화면 설정
st.set_page_config(page_title="반려동물 비서 PRO", page_icon="🐶")
st.title("🐾 멍냥이 콘텐츠 & 이미지 비서")

# 2. 비밀 정보 가져오기
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
WP_URL = st.secrets["WP_URL"]
WP_USER = st.secrets["WP_USER"]
WP_APP_PW = st.secrets["WP_APP_PW"]

# [고정] gemini-flash-latest 모델 사용
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# 3. 비서의 기억장치
if "generated_content" not in st.session_state:
    st.session_state.generated_content = ""
if "image_prompts" not in st.session_state:
    st.session_state.image_prompts = []
if "classified_title" not in st.session_state:
    st.session_state.classified_title = ""

# 4. 명령 내리기 (UI 업그레이드)
command = st.text_input("주제 입력", placeholder="예: 강아지 슬개골 탈구 자가진단법")

# [주인님 제안 반영] 이미지 개수를 선택하는 슬라이더 추가
img_count = st.slider("삽입할 이미지 개수를 선택하세요", min_value=1, max_value=10, value=4)

if st.button("🚀 콘텐츠 & 이미지 프롬프트 제작!"):
    with st.spinner(f"이미지 {img_count}장을 배치하며 글을 작성 중입니다..."):
        
        full_prompt = f"""
        너는 반려동물 전문 블로거이자 전문 사진작가야. 
        주제: '{command}'
        
        [과업 1: 카테고리 분류 및 제목 작성]
        다음 5가지 카테고리 중 적절한 하나를 골라 제목 앞에 [카테고리명]을 붙여줘:
        (건강/질병, 행동/훈련, 푸드/영양, 생활/용품, 초보 집사 가이드)

        [과업 2: 블로그 글 작성]
        - <h2>, <h3> 태그를 사용한 SEO 구조화된 HTML로 작성해.
        - 전문적인 E-E-A-T 스타일로 작성하되, 마지막 광고 문구는 절대 넣지 마.
        - **이미지 배치**: 글의 흐름상 적절한 위치에 총 {img_count}개의 이미지 표시([이미지 1] ~ [이미지 {img_count}])를 본문에 삽입해.

        [과업 3: 실사 이미지 프롬프트 {img_count}개 제작]
        - 본문에 표시한 각 위치에 대응하는 영문 프롬프트를 {img_count}개 작성해줘.
        - 모든 이미지는 반드시 '완벽한 실사(Hyper-realistic, Photorealistic)'여야 해.
        
        결과 형식:
        ---TITLE---
        [카테고리명] 제목
        ---CONTENT---
        (본문 내용)
        ---IMAGES---
        이미지 1: (영문 프롬프트)
        ... (이미지 {img_count}까지)
        """
        
        response = model.generate_content(full_prompt)
        full_text = response.text
        
        try:
            title_part = full_text.split("---TITLE---")[1].split("---CONTENT---")[0].strip()
            content_part = full_text.split("---CONTENT---")[1].split("---IMAGES---")[0].strip()
            image_part = full_text.split("---IMAGES---")[1].strip().split("\n")
            
            st.session_state.classified_title = title_part
            st.session_state.generated_content = content_part
            st.session_state.image_prompts = [line for line in image_part if line.strip()]
        except:
            st.session_state.classified_title = command
            st.session_state.generated_content = full_text
            st.session_state.image_prompts = ["제작 중 오류 발생"]

        st.success(f"✅ 이미지 {img_count}장이 포함된 고품질 콘텐츠 제작 완료!")

# 5. 결과 화면 보여주기
if st.session_state.generated_content:
    st.markdown(f"### 📌 제목: {st.session_state.classified_title}")
    st.markdown("---")
    st.markdown("### 📝 작성된 SEO 블로그 글")
    # 이미지 위치 시각적 강조
    display_content = re.sub(r'(\[이미지\s*\d+\])', r'<b style="color:red; background-color:yellow;">\1</b>', st.session_state.generated_content)
    st.markdown(display_content, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"### 📸 실사 이미지 생성용 프롬프트 (총 {len(st.session_state.image_prompts)}개)")
    for p in st.session_state.image_prompts:
        st.code(p)
        
    if st.button("📦 이 원고를 워드프레스 창고로 배달하기"):
        auth = (WP_USER, WP_APP_PW)
        payload = {
            "title": st.session_state.classified_title, 
            "content": st.session_state.generated_content, 
            "status": "draft"
        }
        res = requests.post(WP_URL, auth=auth, json=payload)
        
        if res.status_code == 201:
            st.balloons()
            st.success("주인님! 원고가 워드프레스 창고에 안전하게 도착했습니다! 💌")
        else:
            st.error(f"배달 실패! (에러 코드: {res.status_code})")
