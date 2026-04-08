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

# 3. 안심이의 기억장치 확장
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
    - **직함:** Magentalab 수석 연구원
    - **특징:** 0.1% 오차도 잡는 돋보기
    - **필살기:** 따뜻한 F형 공감 한마디
    """)

command = st.text_input("안심이에게 맡길 연구 주제를 입력하세요", placeholder="예: 강아지 분리불안 해결법")
img_count = st.slider("삽입할 이미지(안심이 출연) 개수를 선택하세요", min_value=1, max_value=8, value=4)

if st.button("🚀 안심이에게 콘텐츠 제작 요청!"):
    with st.spinner(f"수석 연구원 안심이가 돋보기를 들고 연구 보고서를 작성 중입니다..."):
        
        full_prompt = f"""
        너는 Magentalab 반려동물 연구소의 수석 연구원, 닥스훈트 '안심이'야. 
        주제: '{command}'
        
        [과업 1: 페르소나 적용 본문 작성]
        - 전문성과 따뜻한 위로를 섞어 SEO 최적화 HTML 구조(<h2>, <h3>)로 작성해.
        - 본문 중간에 [이미지 1] ~ [이미지 {img_count}]를 맥락에 맞게 배치해.
        - 말투는 안심이 특유의 "~군요!", "~입니다!"를 사용해.

        [과업 2: 안심이의 돋보기 요약 및 공감]
        - 이 글의 핵심 내용 3가지를 요약해줘.
        - 반려인의 마음을 어루만지는 안심이의 따뜻한 공감 한마디(F형 스타일)를 작성해.

        [과업 3: 이미지 프롬프트 및 태그]
        - 이미지 프롬프트는 "A brown Dachshund wearing round glasses and a white lab coat"를 포함한 영문 실사 스타일로 작성해.
        - 글에 어울리는 SEO 태그 5개를 추출해줘.

        결과 형식 (반드시 아래 구분자를 지킬 것):
        ---TITLE---
        [카테고리] 제목
        ---CONTENT---
        (본문 HTML)
        ---IMAGES---
        이미지 1: (영문 프롬프트)
        ...
        ---SUMMARY---
        (요약 내용 3줄)
        ---SYMPATHY---
        (안심이의 공감 한마디)
        ---TAGS---
        (태그1, 태그2, 태그3, 태그4, 태그5)
        """
        
        try:
            response = model.generate_content(full_prompt)
            full_text = response.text
            
            # 파싱 작업
            st.session_state.classified_title = full_text.split("---TITLE---")[1].split("---CONTENT---")[0].strip()
            st.session_state.generated_content = full_text.split("---CONTENT---")[1].split("---IMAGES---")[0].strip()
            img_raw = full_text.split("---IMAGES---")[1].split("---SUMMARY---")[0].strip().split("\n")
            st.session_state.image_prompts = [re.sub(r'^이미지 \d+:\s*', '', line).strip() for line in img_raw if line.strip()]
            st.session_state.summary = full_text.split("---SUMMARY---")[1].split("---SYMPATHY---")[0].strip()
            st.session_state.sympathy = full_text.split("---SYMPATHY---")[1].split("---TAGS---")[0].strip()
            st.session_state.tags = full_text.split("---TAGS---")[1].strip()
            
        except Exception as e:
            st.error(f"앗! 연구 중에 돋보기에 지문이 묻었나 봐요. 다시 시도해 주세요! ({e})")

# 5. 결과 표시 및 전송
if st.session_state.generated_content:
    st.markdown(f"### 📌 제목: {st.session_state.classified_title}")
    
    # UI용 요약 미리보기
    with st.expander("🔍 안심 연구원의 미리보기 요약", expanded=True):
        st.info(f"**핵심 요약:**\n{st.session_state.summary}")
        st.warning(f"**안심이의 마음:** {st.session_state.sympathy}")

    st.markdown("---")
    # 화면 표시용 본문 (이미지 태그 강조)
    display_content = re.sub(r'(\[이미지\s*\d+\])', r'<b style="color:#FF00FF; background-color:#FFF0F5; padding:2px 5px; border-radius:3px; border:1px dashed #FF00FF;">📸 \1 (프롬프트 자동 삽입 예정)</b>', st.session_state.generated_content)
    st.markdown(display_content, unsafe_allow_html=True)
    
    if st.button("📦 이 연구 보고서를 워드프레스 창고로 보내기"):
        auth = (WP_USER, WP_APP_PW)
        
        # 1. 본문 내 [이미지 n]을 실제 프롬프트 박스로 치환
        final_body = st.session_state.generated_content
        for i, prompt in enumerate(st.session_state.image_prompts, 1):
            prompt_html = f"""
            <div style="background-color: #f9f9f9; border: 1px dashed #FF00FF; padding: 15px; margin: 20px 0; border-radius: 8px;">
                <p style="margin: 0; color: #FF00FF; font-weight: bold;">📸 안심 연구원의 촬영 가이드 {i}</p>
                <code style="display: block; margin-top: 10px; color: #333;">{prompt}</code>
            </div>
            """
            final_body = final_body.replace(f"[이미지 {i}]", prompt_html)
        
        # 2. 하단 요약 박스 구성 (인라인 CSS)
        summary_footer = f"""
        <div style="background-color: #FFF0F5; border: 2px solid #FF00FF; padding: 25px; border-radius: 15px; margin-top: 40px;">
            <h3 style="color: #FF00FF; margin-top: 0;">🧪 안심 연구원의 돋보기 요약</h3>
            <div style="color: #444; line-height: 1.6;">{st.session_state.summary.replace('\n', '<br>')}</div>
            <hr style="border: 0; border-top: 1px solid #FFB6C1; margin: 20px 0;">
            <p style="font-style: italic; color: #D100D1; font-weight: 500;">" {st.session_state.sympathy} "</p>
        </div>
        <p style="margin-top: 20px; color: #888; font-size: 0.9em;">태그: {st.session_state.tags}</p>
        """
        
        # 3. 최종 통합 본문
        full_payload_content = final_body + summary_footer
        
        payload = {
            "title": st.session_state.classified_title, 
            "content": full_payload_content, 
            "status": "draft"
        }
        
        res = requests.post(WP_URL, auth=auth, json=payload)
        
        if res.status_code == 201:
            st.balloons()
            st.success("주인님! 요약부터 프롬프트까지 안심이가 봇짐에 꽉꽉 채워 워드프레스에 배달 완료했습니다! 💌🐾")
        else:
            st.error(f"앗! 배달 중에 꼬리가 문에 걸렸어요. (에러: {res.status_code})")
