import streamlit as st
import google.generativeai as genai
import requests
import re

# 1. 화면 설정
st.set_page_config(page_title="Magentalab 콘텐츠 비서", page_icon="🐾")
st.title("🧪 Magentalab 반려동물 연구소")
st.subheader("수석 연구원 '안심이'의 콘텐츠 제작소")

# 2. 비밀 정보 가져오기
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
WP_URL = st.secrets["WP_URL"]
WP_USER = st.secrets["WP_USER"]
WP_APP_PW = st.secrets["WP_APP_PW"]

# [절대 고정] gemini-flash-latest 모델 사용
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# 3. 안심이의 기억장치
if "generated_content" not in st.session_state:
    st.session_state.generated_content = ""
if "image_prompts" not in st.session_state:
    st.session_state.image_prompts = []
if "classified_title" not in st.session_state:
    st.session_state.classified_title = ""

# 4. 연구 과제 입력 (UI)
command = st.text_input("연구 주제(포스팅 주제)를 입력하세요", placeholder="예: 노령견 관절 건강을 위한 마사지법")
img_count = st.slider("삽입할 실사 이미지 개수를 선택하세요", min_value=1, max_value=10, value=4)

if st.button("🚀 안심이에게 콘텐츠 제작 요청!"):
    with st.spinner(f"수석 연구원 안심이가 {img_count}장의 이미지를 설계하며 집필 중입니다..."):
        
        # [정체성 변경] 안심이 페르소나 적용
        full_prompt = f"""
        너는 Magentalab 반려동물 연구소의 수석 연구원 '안심이'야. 
        주제: '{command}'
        
        [과업 1: 연구 카테고리 분류 및 제목]
        다음 5가지 카테고리 중 적절한 하나를 골라 제목 앞에 [카테고리명]을 붙여줘:
        (건강/질병, 행동/훈련, 푸드/영양, 생활/용품, 초보 집사 가이드)

        [과업 2: 연구 보고서(블로그) 작성]
        - 수석 연구원답게 전문적이면서도 반려인들에게 신뢰를 주는 따뜻한 말투로 작성해.
        - <h2>, <h3> 태그를 사용한 SEO 구조화된 HTML로 작성할 것.
        - **이미지 배치**: 연구 데이터의 시각화를 위해 글의 흐름상 적절한 위치에 총 {img_count}개의 이미지 표시([이미지 1] ~ [이미지 {img_count}])를 본문에 삽입해.
        - 마지막에 광고 문구는 절대 넣지 마.

        [과업 3: 연구 보조 실사 이미지 설계]
        - 본문에 표시한 각 위치에 대응하는 영문 프롬프트를 {img_count}개 작성해줘.
        - 수석 연구원의 시각에서 본 '완벽한 실사(Hyper-realistic, Photorealistic)'여야 함.
        - 예: 엑스레이, 임상 현장, 실제 반려동물 생활 모습 등 전문적인 질감을 묘사할 것.
        
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
            st.session_state.image_prompts = ["프롬프트 생성 오류"]

        st.success(f"✅ 수석 연구원 안심이의 보고서 제작이 완료되었습니다!")

# 5. 결과 전시 및 배달
if st.session_state.generated_content:
    st.markdown(f"### 📌 제목: {st.session_state.classified_title}")
    st.markdown("---")
    st.markdown("### 📝 연구 보고서 내용")
    # 이미지 위치 시각적 강조
    display_content = re.sub(r'(\[이미지\s*\d+\])', r'<b style="color:red; background-color:yellow;">\1</b>', st.session_state.generated_content)
    st.markdown(display_content, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"### 📸 실사 이미지 설계도 (총 {len(st.session_state.image_prompts)}개)")
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
            st.success(f"주인님! 수석 연구원 안심이의 원고가 창고에 도착했습니다! 💌")
        else:
            st.error(f"배달 실패! (에러 코드: {res.status_code})")
