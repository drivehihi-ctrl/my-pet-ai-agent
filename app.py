import streamlit as st
import google.generativeai as genai
import requests

# 1. 화면 설정
st.set_page_config(page_title="반려동물 비서 PRO", page_icon="🐶")
st.title("🐾 멍냥이 콘텐츠 비서 (SEO 특화)")

# 2. 비밀 정보 가져오기
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
WP_URL = st.secrets["WP_URL"]
WP_USER = st.secrets["WP_USER"]
WP_APP_PW = st.secrets["WP_APP_PW"]

genai.configure(api_key=GEMINI_API_KEY)
# 모델명을 최신 버전으로 고정했습니다!
model = genai.GenerativeModel('gemini-flash-latest')

# 3. 비서의 기억장치
if "generated_content" not in st.session_state:
    st.session_state.generated_content = ""

# 4. 명령 내리기
command = st.text_input("주제 입력", placeholder="예: 강아지 슬개골 탈구 예방법")

if st.button("🚀 SEO 콘텐츠 마법 시작!"):
    with st.spinner("구글 상단 노출을 위한 글을 작성 중입니다..."):
        # [SEO 지침 강화] 프롬프트에 아예 박아버렸습니다.
        seo_prompt = f"""
        너는 반려동물 전문 블로거이자 SEO 마케팅 전문가야. 
        주제: '{command}'
        
        [작성 규칙]
        1. 반드시 <h2>, <h3> 태그를 사용하여 구조화된 HTML로 작성해.
        2. 독자의 체류시간을 늘리기 위해 도입부는 흥미롭게, 본문은 전문적인 팁을 포함해.
        3. 구글 E-E-A-T 기준에 맞춰 경험적인 조언처럼 들리도록 써줘.
        4. 글 마지막에는 반드시 아래 문구를 포함해:
           "<br><hr><p><b>💡 더 건강한 반려생활을 위한 추천 아이템:</b> <a href='주인님_쇼핑몰_URL_넣기'>여기에서 확인해보세요!</a></p>"
        5. 가독성 점수(Flesch Score) 60-70점을 유지해.
        """
        response = model.generate_content(seo_prompt)
        st.session_state.generated_content = response.text
        st.success("✅ SEO 최적화 완료!")

# 5. 글 보여주기 및 배달
if st.session_state.generated_content:
    st.markdown("---")
    st.markdown(st.session_state.generated_content, unsafe_allow_html=True)
    
    if st.button("📦 이 고품질 글을 워드프레스로 배달하기"):
        auth = (WP_USER, WP_APP_PW)
        payload = {
            "title": f"[추천] {command}", # 제목에도 클릭을 부르는 문구 자동 추가
            "content": st.session_state.generated_content, 
            "status": "draft"
        }
        res = requests.post(WP_URL, auth=auth, json=payload)
        
        if res.status_code == 201:
            st.balloons()
            st.success("배달 성공! 이제 워드프레스에서 이미지 한 장만 넣고 '발행' 하세요!")
        else:
            st.error(f"배달 실패! (코드: {res.status_code})")
            st.write("실패 이유:", res.text)
