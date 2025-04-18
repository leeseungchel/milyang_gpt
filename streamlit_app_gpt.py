import streamlit as st
from openai import OpenAI

# ====== 1. OpenAI API 키 로드 ======
api_key = st.secrets["general"]["OPEN_API_KEY"]
client = OpenAI(api_key=api_key)

# ====== 2. 페이지 기본 설정 ======
st.set_page_config(page_title="AI 자동 작성기", layout="wide")  # 페이지 제목과 레이아웃 설정

# ====== 상단 메뉴바, 푸터, 헤더 숨기기 ======
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ====== 3. 사이드바: 생성기 종류 선택 ======
option = st.sidebar.radio("🧭 생성기 선택", ["🎤 인사말씀 생성기", "📰 보도자료 생성기"])

# ====== 4. 🎤 인사말씀 생성기 ======
if option == "🎤 인사말씀 생성기":
    st.title("🎤 GPT 자동 연설문 작성 서비스")  # 상단 제목
    col1, col2 = st.columns([1, 1])  # 좌우 두 컬럼 나누기

    with col2:
        st.header("🎤 연설문 생성 옵션")  # 우측 옵션 입력 영역
        # 사용자 입력값 수집
        title = st.text_input("인사말 제목", placeholder="예) 시민과 함께하는 봄맞이 행사")
        greeting = st.selectbox("인사말 성격", ["대중적", "축제행사", "위원회", "명정"])
        speaker = st.selectbox("연설자 선택", ["밀양시장", "시의회 의장", "국장", "위원장"])
        audience1 = st.selectbox("청중 선택 1", ["밀양시민", "관광객", "공직자", "개별위원"])
        audience2 = st.selectbox("청중 선택 2", ["없음", "청년", "장애인", "여성단체"])
        season = st.selectbox("계절 선택", ["봄", "여름", "가을", "겨울"])
        quote = st.selectbox("인용구 선택", ["없음", "감정이입", "사자성어", "속담", "영어격언"])
        disaster = st.selectbox("재난 상황", ["없음", "재난피해", "재난복구"])

        # 입력값을 기반으로 프롬프트 구성
        parts = []
        parts.append(f"『{title}』의 성격은 {greeting}입니다.")
        parts.append(f"{speaker} ~님의 인사말씀은 {audience1}과(와) {audience2}를 청중으로 작성해야 합니다.")
        parts.append(f"계절적 요소인 {season}에 어울리며,")
        
        # 인용문 선택 여부에 따라 프롬프트 다르게 구성
        if quote != "없음":
            parts.append({
                "감정이입": "감정을 이입할 수 있는 문장을 1회 언급하며,",
                "사자성어": "적절한 사자성어를 1회 인용하고,",
                "속담": "속담을 활용하여 표현을 풍부하게 하며,",
                "영어격언": "영어 격언을 통해 인상 깊게 전달합니다."
            }[quote])
        else:
            parts.append("인용 없이 간결하게 구성됩니다.")
        
        # 재난 관련 상황에 따라 내용 추가
        if disaster == "재난피해":
            parts.append("최근 재난피해를 고려하여 위로와 공감을 담고,")
        elif disaster == "재난복구":
            parts.append("복구 현황과 감사 인사를 포함하며,")
        else:
            parts.append("재난 관련 내용은 포함되지 않습니다.")

        parts.append("이와 같이 전체 인사말씀은 풍부하고 품격 있게 구성되어야 합니다.")
        generated_text = " ".join(parts)  # 리스트를 하나의 문자열로 합침

        # 사용자가 수정할 수 있는 텍스트 영역 제공
        prompt = st.text_area("✏️ 생성된 연설문 (수정 가능)", value=generated_text, height=200)

        # GPT 연설문 생성 버튼 클릭 시
        if st.button("🎯 연설문 생성"):
            with st.spinner("GPT 연설문 생성 중..."):  # 로딩 스피너 표시
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",  # 모델 선택
                        messages=[
                            {"role": "system", "content": "당신은 연설문 작성 전문가입니다. 아래 연설문 가이드를 참고해 실제 연설문을 작성해주세요."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    gpt_output = response.choices[0].message.content
                    st.session_state['speech_result'] = gpt_output  # 결과 저장
                except Exception as e:
                    st.error(f"⚠️ GPT 호출 실패: {str(e)}")

    with col1:
        st.header("📄 GPT 결과")
        speech_result = st.session_state.get('speech_result', "아직 생성된 연설문이 없습니다.")
        st.text_area("📝 GPT가 작성한 연설문", value=speech_result, height=500, key="speech_display", disabled=True)
        if speech_result and speech_result != "아직 생성된 연설문이 없습니다.":
            st.download_button("📥 연설문 다운로드", data=speech_result, file_name="연설문.txt")

# ====== 5. 📰 보도자료 생성기 ======
elif option == "📰 보도자료 생성기":
    st.title("📰 GPT 자동 보도자료 작성 서비스")
    col1, col2 = st.columns([1, 1])

    with col2:
        st.header("🛠️ 보도자료 입력 정보")
        title = st.text_input("1. 보도자료 초안 제목", placeholder="예) 2025년 밀양 봄꽃축제 개최 안내")
        person = st.text_input("2. 담당자", placeholder="예) 홍길동")
        contact = st.text_input("3. 연락처", placeholder="예) 010-1234-5678")
        content = st.text_area("4. 보도자료 핵심 내용", height=300, placeholder="예) 밀양시는 오는 4월 10일부터 봄꽃축제를 개최합니다...")

        # GPT 요청
        if st.button("🎯 보도자료 생성"):
            with st.spinner("GPT가 보도자료 제목 5개와 전문을 작성 중입니다..."):
                try:
                    with open("template/template_보도.txt", "r", encoding="utf-8") as file:
                        template = file.read()
                    prompt = template.format(title=title, person=person, contact=contact, content=content)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "당신은 보도자료 작성 전문가입니다. 포맷과 문체를 전문적으로 구성해 주세요."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    gpt_output = response.choices[0].message.content
                    st.session_state['press_result'] = gpt_output
                except Exception as e:
                    st.error(f"⚠️ GPT 호출 실패: {str(e)}")

    with col1:
        st.header("📄 GPT 결과")
        press_result = st.session_state.get('press_result', "아직 생성된 보도자료가 없습니다.")
        st.text_area("📰 추천 제목 & 보도자료", value=press_result, height=600, key="press_display", disabled=True)
        if press_result and press_result != "아직 생성된 보도자료가 없습니다.":
            st.download_button("📥 보도자료 다운로드", data=press_result, file_name="보도자료.txt")

# # ====== 6. 📁 공적조서 작성기 ======
# elif option == "📁 공적조서 작성기":
#     # GPT 호출 함수 정의
#     def generate_merit_statement(grade, unit, details):
#         with open("template/template_공적.txt", "r", encoding="utf-8") as file:
#             template = file.read()
#         prompt = template.format(grade=grade, unit=unit, details=details)
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": "당신은 공적조서를 작성하는 전문가입니다."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7
#         )
#         return response.choices[0].message.content

#     # 제목
#     st.title("📁 GPT 자동 공적조서 작성기")

#     # 상태 변수 초기화
#     if "confirmed_list" not in st.session_state:
#         st.session_state.confirmed_list = []  # 확정된 결과 저장 리스트
#     if "gpt_result" not in st.session_state:
#         st.session_state.gpt_result = ""  # 생성된 결과
#     if "inputs" not in st.session_state:
#         st.session_state.inputs = {"grade": "", "unit": "", "details": ""}
#     if "show_result" not in st.session_state:
#         st.session_state.show_result = False
#     if "form_reset_key" not in st.session_state:
#         st.session_state.form_reset_key = 0  # 입력값 리셋용 키

#     col1, col2 = st.columns([1, 1])

#     # 왼쪽: 확정된 결과 리스트
#     with col1:
#         st.header("✅ 확정된 공적조서")
#         if st.session_state.confirmed_list:
#             remove_index = None
#             for idx, (unit_title, content) in enumerate(st.session_state.confirmed_list):
#                 col_l, col_r = st.columns([0.8, 0.2])
#                 with col_l:
#                     st.markdown(f"**{idx+1}. {unit_title}**")
#                 with col_r:
#                     if st.button("❌삭제", key=f"delete_{idx}"):
#                         remove_index = idx
#                 with st.expander("📝 내용 보기", expanded=False):
#                     st.write(content)
#             if remove_index is not None:
#                 st.session_state.confirmed_list.pop(remove_index)
#                 st.rerun()
#             all_text = "\n\n".join([f"[{i+1}] {title}\n{body}" for i, (title, body) in enumerate(st.session_state.confirmed_list)])
#             st.download_button("📥 전체 공적조서 다운로드", data=all_text, file_name="공적조서.txt")
#             if st.button("🗑️ 전체 삭제"):
#                 st.session_state.confirmed_list = []
#                 st.rerun()
#         else:
#             st.write("아직 확정된 공적조서가 없습니다.")

#     # 오른쪽: 입력 및 생성
#     with col2:
#         st.header("🛠️ 공적조서 입력")
#         grade = st.text_input("1. 공적조서 훈격", value=st.session_state.inputs["grade"], key=f"grade_input_{st.session_state.form_reset_key}")
#         unit = st.text_input("2. 단위 공적 입력", value=st.session_state.inputs["unit"], key=f"unit_input_{st.session_state.form_reset_key}")
#         details = st.text_area("3. 주요 실적 입력", value=st.session_state.inputs["details"], height=200, key=f"details_input_{st.session_state.form_reset_key}")

#         col_a, col_b, col_c = st.columns([1, 1, 1])
#         generate = col_a.button("🎯 공적조서 생성")
#         regenerate = col_b.button("🔁 다시 생성")
#         confirm = col_c.button("📌 확정")

#         if generate or regenerate:
#             st.session_state.inputs = {"grade": grade, "unit": unit, "details": details}
#             with st.spinner("GPT가 공적조서를 작성 중입니다..."):
#                 gpt_output = generate_merit_statement(grade, unit, details)
#                 st.session_state.gpt_result = gpt_output
#                 st.session_state.show_result = True

#         if confirm and st.session_state.gpt_result:
#             st.session_state.confirmed_list.append((unit, st.session_state.gpt_result))
#             st.session_state.inputs = {"grade": "", "unit": "", "details": ""}
#             st.session_state.gpt_result = ""
#             st.session_state.show_result = False
#             st.session_state.form_reset_key += 1  # 입력 필드 리셋을 위한 키 증가
#             st.rerun()

#         if st.session_state.show_result and st.session_state.gpt_result:
#             st.text_area("📝 생성된 공적조서", value=st.session_state.gpt_result, height=300, disabled=True)
#             st.download_button("📥 공적조서 다운로드", data=st.session_state.gpt_result, file_name="merit.txt")

