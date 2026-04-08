import streamlit as st
import google.generativeai as genai
import requests
import re

# 1. 화면 설정
st.set_page_config(page_title="Magentalab 안심이 비서", page_icon="🐾")
st.title("🧪 Magentalab 반려동물 연구소")
st.subheader("수석 연구원 '안심이'의 콘텐츠 제작소 👓✨")

# 2. 비밀 정보 가져오기
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
WP_URL = st.secrets["WP_URL"]
WP_USER = st.secrets["WP_USER"]
WP_APP_PW = st.secrets["WP_APP_PW"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# 3. 안심이의 기억장치
if "generated_content" not in st.session_state:
    st.session_state.generated_content = ""
if "image_prompts" not in st.session_state:
    st.session_state.image_prompts = []
if "classified_title" not in st.session_state:
    st.session_state.classified_title = ""
if "tags" not in st.session_state:
    st.session_state.tags = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "sympathy" not in st.session_state:
    st.session_state.sympathy = ""

# 4. 연구 과제 입력 (UI)
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dachshund.png") 
    st.markdown("""
    **안심 수석 연구원 프로필**
    - **성격:** 0.1% 오차도 잡는 완벽주의자
    - **특징:** 동그란 뿔테 안경, 황금 돋보기
    """)

command = st.text_input("안심이에게 맡길 연구 주제를 입력하세요", placeholder="예: 고양이 신부전 예방을 위한 식단")
img_count = st.slider("삽입할 이미지(안심이 출연) 개수를 선택하세요", min_value=1, max_value=8, value=4)

if st.button("🚀 안심이에게 콘텐츠 제작 요청!"):
    with st.spinner(f"수석 연구원 안심이가 연구 보고서를 작성 중입니다..."):
        
        full_prompt = f"""
        너는 Magentalab 반려동물 연구소의 수석 연구원, 닥스훈트 '안심이'야. 
        주제: '{command}'
        
        [과업 1: 카테고리 및 제목]
        - 다음 중 하나를 골라 제목 앞에 붙여줘: (건강/질병, 행동/훈련, 푸드/영양, 생활/용품, 초보 집사 가이드)
        - 형식: [카테고리] 제목

        [과업 2: 연구 보고서 작성]
        - 전문성과 따뜻한 위로를 섞어 SEO 최적화 HTML 구조(<h2>, <h3>)로 작성해.
        - 본문 중간에 [이미지 1] ~ [이미지 {img_count}]를 맥락에 맞게 배치해.
        - 말투는 안심이 특유의 "~군요!", "~입니다!"를 사용해.

        [과업 3: 안심이의 돋보기 요약 및 공감]
        - 이 글의 핵심 내용 3가지를 요약해줘.
        - 한 칸 엔터 치고, 아래 형식을 엄격히 지켜서 공감을 작성해.
        [공감]
        안심이의 따뜻한 공감 한마디(F형 스타일)

        [과업 4: 이미지 프롬프트 및 태그]
        - 이미지 프롬프트는 영문 실사 스타일로 작성해.
        - 이 글에 어울리는 SEO 최적화 태그 5개를 콤마(,)로 구분해서 추출해줘.

        결과 형식 (구분자를 반드시 지킬 것):
        ---TITLE---
        제목내용
        ---CONTENT---
        본문내용
        ---IMAGES---
        이미지 1: 프롬프트내용
        ...
        ---SUMMARY---
        요약내용
        ---SYMPATHY---
        [공감]
        공감내용
        ---TAGS---
        태그1, 태그2, 태그3, 태그4, 태그5
        """
        
        try:
            response = model.generate_content(full_prompt)
            full_text = response.text
            
            st.session_state.classified_title = full_text.split("---TITLE---")[1].split("---CONTENT---")[0].strip()
            st.session_state.generated_content = full_text.split("---CONTENT---")[1].split("---IMAGES---")[0].strip()
            img_raw = full_text.split("---IMAGES---")[1].split("---SUMMARY---")[0].strip().split("\n")
            st.session_state.image_prompts = [re.sub(r'^이미지 \d+:\s*', '', line).strip() for line in img_raw if line.strip()]
            st.session_state.summary = full_text.split("---SUMMARY---")[1].split("---SYMPATHY---")[0].strip()
            st.session_state.sympathy = full_text.split("---SYMPATHY---")[1].split("---TAGS---")[0].strip()
            st.session_state.tags = full_text.split("---TAGS---")[1].strip()
            
        except:
            st.error("안심이가 연구 중에 돋보기를 놓쳤나 봐요! 다시 시도해주세요.")

# 5. 결과 표시 및 전송
if st.session_state.generated_content:
    st.markdown(f"### 📌 제목: {st.session_state.classified_title}")
    
    with st.expander("🔍 안심 연구원의 요약 & 공감 미리보기", expanded=True):
        st.write(st.session_state.summary)
        st.write("")
        st.write(st.session_state.sympathy)

    st.markdown("---")
    st.markdown(st.session_state.generated_content, unsafe_allow_html=True)
    
    if st.button("📦 이 연구 보고서를 워드프레스 창고로 보내기"):
        auth = (WP_USER, WP_APP_PW)
        
        # 1. 본문 내 [이미지 n]을 텍스트 기반 프롬프트로 치환 (분홍 박스 제거)
        final_body = st.session_state.generated_content
        for i, prompt in enumerate(st.session_state.image_prompts, 1):
            prompt_text = f"\n\n(📸 안심 연구원의 촬영 가이드 {i}: {prompt})\n\n"
            final_body = final_body.replace(f"[이미지 {i}]", prompt_text)
        
        # 2. 하단 요약 및 공감 텍스트 구성
        summary_footer = f"""
        <br><br>
        <hr>
        <h3>🧪 안심 연구원의 돋보기 요약</h3>
        {st.session_state.summary.replace('\n', '<br>')}
        <br><br>
        {st.session_state.sympathy.replace('\n', '<br>')}
        <br><br>
        태그: {st.session_state.tags}
        """
        
        full_payload_content = final_body + summary_footer
        
        payload = {
            "title": st.session_state.classified_title, 
            "content": full_payload_content, 
            "status": "draft"
        }
        
        res = requests.post(WP_URL, auth=auth, json=payload)
        
        if res.status_code == 201:
            st.balloons()
            st.success("주인님! 카테고리 선정부터 요약, [공감]까지 모두 담아 전송했습니다! 오늘도 안심하세요! 💌🐾")
        else:
            st.error(f"배달 실패! 에러 코드: {res.status_code}")
