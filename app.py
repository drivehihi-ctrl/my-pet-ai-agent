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

# gemini-flash-latest 모델 사용
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
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dachshund.png") # 닥스훈트 아이콘 예시
    st.markdown("""
    **안심 수석 연구원 프로필**
    - **직함:** Magentalab 수석 연구원
    - **성격:** 0.1% 성분도 잡아내는 완벽주의자
    - **특징:** 동그란 뿔테 안경, 황금 돋보기
    """)

command = st.text_input("안심이에게 맡길 연구 주제를 입력하세요", placeholder="예: 고양이 신부전 예방을 위한 식단")
img_count = st.slider("삽입할 이미지(안심이 출연) 개수를 선택하세요", min_value=1, max_value=8, value=4)

if st.button("🚀 안심이에게 콘텐츠 제작 요청!"):
    with st.spinner(f"수석 연구원 안심이가 돋보기를 들고 연구 보고서를 작성 중입니다..."):
        
        # [페르소나 강화 프롬프트]
        full_prompt = f"""
        너는 Magentalab 반려동물 연구소의 수석 연구원, 닥스훈트 '안심이'야. 
        주제: '{command}'
        
        [안심이의 페르소나 지침]
        1. 말투: 차분하고 신뢰감 있지만, 중요한 정보에선 목소리가 한 톤 높아짐. 말끝은 "~군요!", "~입니다!"를 주로 사용함.
        2. 성격: 0.1%의 수치도 놓치지 않는 완벽주의자이면서, 반려인의 슬픔에 공감하여 눈시울이 붉어지는 따뜻한 'F형' 연구원임.
        3. 행동: 연구에 집중하다 자기 꼬리를 보고 놀라는 허당미를 한 번씩 노출함.
        4. 비주얼: 동그란 뿔테 안경을 쓰고 황금 돋보기를 들고 있음.

        [과업 1: 카테고리 및 제목]
        다음 중 하나를 골라 제목 앞에 붙여줘: (건강/질병, 행동/훈련, 푸드/영양, 생활/용품, 초보 집사 가이드)

        [과업 2: 연구 보고서 작성]
        - 전문적인 지식과 따뜻한 위로를 섞어 SEO 최적화 HTML 구조(<h2>, <h3>)로 작성해.
        - 중간에 '안심이가 돋보기로 확인해본 결과...' 같은 문구를 넣어줘.
        - 본문 흐름상 적절한 곳에 [이미지 1] ~ [이미지 {img_count}]를 배치해.
        - 영상의 마지막처럼 "오늘도 안심하세요!"라고 마무리 인사를 해줘.

        [과업 3: 안심이 출연 실사 이미지 설계]
        - 모든 이미지는 안심이(Dachshund researcher)가 주인공으로 등장해야 함.
        - 시각적 고정값: "A brown long-haired Dachshund wearing round horn-rimmed glasses, holding a small golden magnifying glass, wearing a white lab coat."
        - 각 프롬프트는 위 고정값에 주제와 관련된 상황을 더해 'Hyper-realistic 3D render style' 영문으로 작성해.
        - 예: 돋보기로 사료 알갱이를 관찰하는 모습, 칠판 앞에서 그래프를 가리키는 모습 등.
        
        결과 형식:
        ---TITLE---
        [카테고리명] 제목
        ---CONTENT---
        (본문 내용)
        ---IMAGES---
        이미지 1: (영문 프롬프트)
        ... (이미지 {img_count}까지)
        """
        
        try:
            response = model.generate_content(full_prompt)
            full_text = response.text
            
            title_part = full_text.split("---TITLE---")[1].split("---CONTENT---")[0].strip()
            content_part = full_text.split("---CONTENT---")[1].split("---IMAGES---")[0].strip()
            image_part = full_text.split("---IMAGES---")[1].strip().split("\n")
            
            st.session_state.classified_title = title_part
            st.session_state.generated_content = content_part
            st.session_state.image_prompts = [line for line in image_part if line.strip()]
        except:
            st.error("안심이가 연구 중에 간식 냄새를 맡고 잠시 길을 잃었나 봐요! 다시 시도해주세요.")

if st.session_state.generated_content:
    st.markdown(f"### 📌 제목: {st.session_state.classified_title}")
    st.markdown("---")
    
    # 안심이 박스 디자인
    st.info(f"💡 **안심 수석 연구원의 코멘트:** {st.session_state.classified_title}에 대해 돋보기를 들고 꼼꼼히 조사했으니 안심하세요!")
    
    st.markdown("### 📝 연구 보고서 내용")
    # 이미지 위치 시각적 강조
    display_content = re.sub(r'(\[이미지\s*\d+\])', r'<b style="color:#FF00FF; background-color:#FFF0F5; padding:2px 5px; border-radius:3px; border:1px dashed #FF00FF;">📸 \1 (안심이 등장)</b>', st.session_state.generated_content)
    st.markdown(display_content, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"### 📸 안심이의 촬영 가이드 (총 {len(st.session_state.image_prompts)}컷)")
    for p in st.session_state.image_prompts:
        st.code(p)
        
    if st.button("📦 이 연구 보고서를 워드프레스 창고로 보내기"):
        auth = (WP_USER, WP_APP_PW)
        payload = {
            "title": st.session_state.classified_title, 
            "content": st.session_state.generated_content, 
            "status": "draft"
        }
        res = requests.post(WP_URL, auth=auth, json=payload)
        
        if res.status_code == 201:
            st.balloons()
            st.success(f"주인님! 안심이가 작성한 원고를 워드프레스에 무사히 배달했습니다! 오늘도 안심하세요! 💌🐾")
        else:
            st.error(f"앗! 배달 중에 안심이가 꼬리를 쫓느라 멈췄나 봐요. (에러 코드: {res.status_code})")
