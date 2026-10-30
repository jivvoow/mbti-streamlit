import html
import streamlit as st

st.set_page_config(page_title="MBTI 성향 검사", page_icon="🧭", layout="centered")

# ═════════════════════════════════════════════
# 1. 데이터
# ═════════════════════════════════════════════

# 4가지 지표: (첫 글자, 둘째 글자, 지표 이름, 첫 글자 이름, 둘째 글자 이름, 설명)
AXES = [
    ("E", "I", "에너지 방향", "외향", "내향", "에너지를 사람들과의 만남에서 얻는지, 혼자만의 시간에서 얻는지"),
    ("S", "N", "정보 인식", "감각", "직관", "눈앞의 사실과 경험을 믿는지, 가능성과 의미를 먼저 보는지"),
    ("T", "F", "판단 기준", "사고", "감정", "결정할 때 논리와 원칙을 따르는지, 사람과 관계를 고려하는지"),
    ("J", "P", "생활 방식", "판단", "인식", "계획을 세워 정리하는 것이 편한지, 상황에 맞춰 유연한 것이 편한지"),
]

# 지표별 문장 6개씩: (이 문장에 동의하면 점수가 올라가는 글자, 문장)
STATEMENTS = {
    "EI": [
        ("E", "처음 보는 사람과도 금방 대화를 시작하는 편이다"),
        ("I", "혼자 보내는 시간이 있어야 에너지가 충전된다"),
        ("E", "생각을 정리할 때 말하면서 정리하는 편이다"),
        ("I", "모임이 끝나면 쉬고 싶다는 생각이 먼저 든다"),
        ("E", "주말에 약속이 없으면 심심하다"),
        ("I", "여러 사람과 함께 있는 것보다 일대일 대화가 편하다"),
    ],
    "SN": [
        ("S", "새로운 걸 배울 때 구체적인 예시가 있어야 이해가 잘 된다"),
        ("N", "'만약에 ~라면?' 같은 상상을 자주 한다"),
        ("S", "설명서를 순서대로 따라 하는 것이 편하다"),
        ("N", "대화하다 보면 생각이 다른 주제로 자주 뻗어 나간다"),
        ("S", "새로운 방법보다 검증된 방법에 더 믿음이 간다"),
        ("N", "사실 그 자체보다 그 속에 담긴 의미가 더 궁금하다"),
    ],
    "TF": [
        ("T", "친구가 고민을 말하면 해결책부터 떠오른다"),
        ("F", "결정을 내릴 때 다른 사람의 기분이 신경 쓰인다"),
        ("T", "논리적으로 맞지 않는 말을 들으면 짚고 넘어가고 싶다"),
        ("F", "칭찬 한마디에 하루 기분이 크게 달라진다"),
        ("T", "배려보다 공정함이 더 중요하다고 생각한다"),
        ("F", "영화나 드라마를 보다가 쉽게 감정이입한다"),
    ],
    "JP": [
        ("J", "여행 전에 일정을 미리 꼼꼼하게 짜 둔다"),
        ("P", "계획이 갑자기 바뀌어도 크게 스트레스받지 않는다"),
        ("J", "할 일은 미리 끝내 놓아야 마음이 편하다"),
        ("P", "마감이 다가와야 집중력이 올라간다"),
        ("J", "물건은 정해진 자리에 두는 편이다"),
        ("P", "즉흥적인 약속이 오히려 더 재미있다"),
    ],
}

# 지표가 골고루 섞이도록 E→S→T→J 순서로 번갈아 배치 (총 24문항)
QUESTIONS = []
for k in range(6):
    for first, second, axis_name, *_ in AXES:
        letter, text = STATEMENTS[first + second][k]
        QUESTIONS.append({"axis": first + second, "axis_name": axis_name, "letter": letter, "text": text})
N = len(QUESTIONS)
MAX_SCORE = 6 * 2  # 지표당 6문항 × 최대 2점

# 5점 척도
SCALE = [("매우 그렇다", 2), ("그렇다", 1), ("보통이다", 0), ("아니다", -1), ("전혀 아니다", -2)]
SCALE_LABEL = {v: label for label, v in SCALE}

# 16가지 유형: (별명, 설명, 강점, 주의할 점, 잘 맞는 일)
TYPES = {
    "ISTJ": ("믿음직한 원칙주의자", "약속과 책임을 무엇보다 중요하게 여기고, 맡은 일은 끝까지 해내는 타입이에요.",
             ["꼼꼼함", "책임감", "꾸준함"], "갑작스러운 변화에 쉽게 지칠 수 있어요. 계획에 여유 칸을 남겨 두세요.",
             "회계·재무, 공무원, 데이터 관리, 품질 관리"),
    "ISFJ": ("따뜻한 수호자", "조용히 주변을 챙기며 안정적인 분위기를 만드는 타입이에요.",
             ["배려심", "성실함", "세심함"], "거절을 어려워해 일을 혼자 떠안기 쉬워요.",
             "간호·보건, 교육, 인사, 고객 지원"),
    "INFJ": ("통찰력 있는 조언자", "사람의 마음을 깊이 읽고 의미 있는 방향을 찾는 타입이에요.",
             ["통찰력", "공감", "신념"], "모든 걸 완벽하게 하려다 스스로 지칠 수 있어요.",
             "상담, 작가, 기획, 교육"),
    "INTJ": ("치밀한 전략가", "큰 그림을 설계하고 효율적으로 실행하는 타입이에요.",
             ["분석력", "독립성", "장기 계획"], "과정 설명 없이 결론만 말해 오해를 살 수 있어요.",
             "전략 기획, 연구원, 개발자, 컨설턴트"),
    "ISTP": ("만능 해결사", "직접 부딪혀 원리를 파악하고 문제를 고치는 타입이에요.",
             ["침착함", "손재주", "실용성"], "감정 표현이 적어 무심해 보일 수 있어요.",
             "엔지니어, 정비, 보안, 개발자"),
    "ISFP": ("감성 예술가", "지금 이 순간과 자기만의 취향을 소중히 여기는 타입이에요.",
             ["감수성", "온화함", "유연함"], "갈등을 피하다 속마음을 말할 타이밍을 놓칠 수 있어요.",
             "디자이너, 사진·영상, 요리, 반려동물 관련"),
    "INFP": ("꿈꾸는 이상주의자", "자기만의 가치와 상상력으로 세상을 바라보는 타입이에요.",
             ["상상력", "진정성", "공감"], "생각이 많아 실행이 늦어질 수 있어요. 작은 목표부터 시작해 보세요.",
             "작가, 콘텐츠 기획, 상담, 일러스트"),
    "INTP": ("호기심 많은 탐구자", "'왜?'라는 질문을 끝까지 파고드는 논리적인 타입이에요.",
             ["논리력", "창의성", "객관성"], "마무리하기 전에 다른 흥미로 넘어가기 쉬워요.",
             "연구원, 개발자, 데이터 분석, 기획"),
    "ESTP": ("행동파 모험가", "생각보다 행동이 빠르고 현장에서 빛나는 타입이에요.",
             ["순발력", "추진력", "현실 감각"], "결정이 빨라 세부 사항을 놓칠 수 있어요.",
             "영업, 창업, 스포츠, 현장 관리"),
    "ESFP": ("분위기 메이커", "어디서든 사람들을 즐겁게 만드는 에너지의 주인공이에요.",
             ["친화력", "긍정 에너지", "표현력"], "당장의 즐거움 때문에 장기 계획이 밀릴 수 있어요.",
             "방송·공연, 서비스, 마케팅, 이벤트 기획"),
    "ENFP": ("열정적인 아이디어 뱅크", "새로운 가능성에 설레고 사람들에게 영감을 주는 타입이에요.",
             ["열정", "창의성", "사교성"], "시작은 많지만 마무리가 약해질 수 있어요.",
             "마케팅, 크리에이터, 기획, 교육"),
    "ENTP": ("재치 있는 발명가", "토론과 새로운 시도를 즐기는 아이디어형 도전가예요.",
             ["재치", "순발력", "문제 해결"], "논쟁이 상대에게는 공격처럼 느껴질 수 있어요.",
             "창업, 기획, 법률, 컨설턴트"),
    "ESTJ": ("든든한 관리자", "체계를 세우고 사람과 일을 효율적으로 이끄는 타입이에요.",
             ["추진력", "조직력", "결단력"], "내 방식만 고집하면 팀이 지칠 수 있어요.",
             "관리자, 행정, 금융, 프로젝트 매니저"),
    "ESFJ": ("다정한 사교가", "모두가 함께 잘 지내도록 챙기는 분위기 조율자예요.",
             ["협동심", "친절함", "책임감"], "다른 사람의 평가에 쉽게 흔들릴 수 있어요.",
             "교육, 서비스, 인사, 의료"),
    "ENFJ": ("따뜻한 리더", "사람들의 성장을 돕고 한 방향으로 이끄는 타입이에요.",
             ["리더십", "공감", "소통"], "남을 챙기느라 정작 나를 놓치기 쉬워요.",
             "교사, 코치, 홍보, 인사"),
    "ENTJ": ("대담한 지휘관", "목표를 정하면 거침없이 밀고 나가는 리더예요.",
             ["결단력", "리더십", "효율성"], "속도를 내다 사람들의 감정을 놓칠 수 있어요.",
             "경영, 전략 기획, 컨설턴트, 창업"),
}

# ═════════════════════════════════════════════
# 2. 상태(session_state)
#    stage    : intro(시작) → test(검사) → result(결과)
#    idx      : 지금 보고 있는 문항 번호
#    answers  : {문항 번호: 점수(-2~2)}
#    direction: 카드가 넘어가는 방향 (next / prev) → 애니메이션 방향 결정
#    round    : 다시 하기를 누를 때마다 증가 → 위젯 key를 새로 만들어 깨끗하게 초기화
# ═════════════════════════════════════════════
ss = st.session_state
for key, value in {"stage": "intro", "idx": 0, "answers": {}, "direction": "next",
                   "round": 0, "name": "", "result": None, "do_scroll": False, "scroll_id": 0}.items():
    ss.setdefault(key, value)


# ═════════════════════════════════════════════
# 3. 콜백 함수 (버튼을 눌렀을 때 실행)
# ═════════════════════════════════════════════
def start_test():
    ss.name = ss[f"name_{ss.round}"].strip()
    ss.stage, ss.idx, ss.answers, ss.direction = "test", 0, {}, "next"
    ss.do_scroll = True


def choose(i, value):
    """답을 고르면 저장하고, 마지막 문항이 아니면 다음 카드로 자동으로 넘김"""
    ss.answers[i] = value
    if i < N - 1:
        ss.idx, ss.direction = i + 1, "next"


def move(step):
    ss.idx += step
    ss.direction = "next" if step > 0 else "prev"


def finish():
    scores = {}
    for first, second, *_ in AXES:
        axis = first + second
        # 첫 글자 쪽 문장에 동의하면 +, 둘째 글자 쪽 문장에 동의하면 -
        scores[axis] = sum(v if QUESTIONS[i]["letter"] == first else -v
                           for i, v in ss.answers.items() if QUESTIONS[i]["axis"] == axis)
    mbti = "".join(f if scores[f + s] >= 0 else s for f, s, *_ in AXES)
    ss.result = {"type": mbti, "scores": scores}
    ss.stage = "result"
    ss.do_scroll = True


def restart():
    ss.round += 1
    ss.stage, ss.idx, ss.answers, ss.result = "intro", 0, {}, None
    ss.do_scroll = True


def scroll_to_top():
    """화면을 맨 위로 올리는 작은 스크립트 (화면이 바뀐 직후 한 번만 실행)"""
    ss.scroll_id += 1
    script = f"""<script>
    // {ss.scroll_id}
    const d = window.parent.document;
    ['[data-testid="stMain"]', '.stMain', 'section.main', '[data-testid="stAppViewContainer"]']
      .forEach(s => {{ const el = d.querySelector(s); if (el) el.scrollTo({{top: 0}}); }});
    window.parent.scrollTo({{top: 0}});
    </script>"""
    if hasattr(st, "iframe"):          # Streamlit 최신 버전
        st.iframe(script, height=1)
    else:                              # 예전 버전
        import streamlit.components.v1 as components
        components.html(script, height=0)


def axis_detail(first, second, score):
    """지표 점수 → (이긴 글자, 이긴 쪽 %, 강도 이름)"""
    first_pct = round(50 + score / MAX_SCORE * 50)
    win_first = score >= 0
    pct = first_pct if win_first else 100 - first_pct
    strength = "반반" if pct < 60 else ("보통" if pct < 75 else "뚜렷함")
    return (first if win_first else second), first_pct, pct, strength


# ═════════════════════════════════════════════
# 4. 디자인 (CSS)
# ═════════════════════════════════════════════
st.markdown("""<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
:root { --ink:#191f28; --sub:#6b7684; --line:#e5e8eb; --bg:#f7f8fa; --accent:#3d5afe; --accent-soft:#eef1ff; }
.stApp { background: var(--bg); color: var(--ink); }
html, body, .stApp, .stMarkdown, button, input, label, p { font-family: 'Pretendard', sans-serif !important; }
.block-container { max-width: 640px !important; padding-top: 3rem !important; padding-bottom: 4rem !important; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
div[data-testid="stElementContainer"]:has(iframe) { display: none; }

/* 공통 */
.eyebrow { font-size:13px; font-weight:700; color:var(--accent); margin-bottom:6px; }
.h1 { font-size:32px; font-weight:800; letter-spacing:-0.5px; line-height:1.3; margin:0 0 10px; }
.lead { color:var(--sub); font-size:15px; line-height:1.7; margin:0 0 20px; }
.chips { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:28px; }
.chip { border-radius:99px; padding:7px 14px; font-size:13px; font-weight:600; border:0; }
.chip b { font-weight:800; }
.chip:nth-child(1) { background:#eef1ff; color:#3d5afe; }   /* 24문항 - 연한 파랑 */
.chip:nth-child(2) { background:#e6f8f0; color:#12a26a; }   /* 3분 - 연한 초록 */
.chip:nth-child(3) { background:#fff4e5; color:#e67700; }   /* 5점 척도 - 연한 주황 */
.chip:nth-child(4) { background:#fdeef5; color:#d6336c; }   /* 결과 즉시 확인 - 연한 분홍 */
.section { font-size:18px; font-weight:800; margin:32px 0 12px; }
.box { background:#fff; border:1px solid var(--line); border-radius:16px; padding:20px 22px; }
.grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
@media (max-width:560px) { .grid { grid-template-columns:1fr; } }
.small { font-size:13px; color:var(--sub); line-height:1.6; }

/* 시작 화면 단계 */
.step { display:flex; gap:14px; align-items:flex-start; padding:12px 0; border-bottom:1px solid var(--line); }
.step:last-child { border-bottom:0; }
.step .num { flex:none; width:28px; height:28px; border-radius:99px; background:var(--accent-soft); color:var(--accent);
             font-weight:800; font-size:13px; display:flex; align-items:center; justify-content:center; }
.step .t { font-weight:700; font-size:15px; }
.axis-box .letters { font-size:20px; font-weight:800; color:var(--accent); letter-spacing:1px; }
.axis-box .name { font-weight:700; font-size:15px; margin:2px 0 6px; }

/* 진행률 */
.progress-row { display:flex; justify-content:space-between; font-size:14px; color:var(--sub); margin:0 0 6px; }
.progress-row b { color:var(--ink); }
.progress-track { height:8px; background:var(--line); border-radius:99px; overflow:hidden; display:flex; }
.progress-fill { height:100%; background:var(--accent); border-radius:99px; transition: width .3s ease; }

/* 문항 카드 + 넘기기 애니메이션 */
@keyframes slideNext { from { opacity:0; transform:translateX(48px); } to { opacity:1; transform:none; } }
@keyframes slidePrev { from { opacity:0; transform:translateX(-48px); } to { opacity:1; transform:none; } }
div[class*="st-key-qcard"] { background:#fff; border:1px solid var(--line); border-radius:20px; padding:28px 24px 22px; margin-top:16px; }
div[class*="st-key-qcard"][class*="_next"] { animation: slideNext .35s ease; }
div[class*="st-key-qcard"][class*="_prev"] { animation: slidePrev .35s ease; }
.q-tag { display:inline-block; background:var(--accent-soft); color:var(--accent); font-size:12px; font-weight:700; border-radius:99px; padding:4px 10px; }
.q-num { color:var(--sub); font-size:14px; font-weight:600; margin:14px 0 4px; }
.q-text { font-size:21px; font-weight:800; line-height:1.45; margin:0 0 18px; word-break:keep-all; }

/* 버튼 공통 */
.stButton button { border-radius:12px !important; min-height:50px; }
.stButton button p { font-weight:700 !important; font-size:15px !important; }
.stButton button[kind="primary"], button[data-testid="stBaseButton-primary"] { background:var(--accent) !important; border:0 !important; color:#fff !important; }
.stButton button[kind="primary"]:disabled, button[data-testid="stBaseButton-primary"]:disabled { background:#d1d6db !important; cursor:not-allowed; }
.stButton button[kind="secondary"], button[data-testid="stBaseButton-secondary"] { background:#fff !important; border:1px solid var(--line) !important; color:var(--ink) !important; }

/* 5점 척도 선택지 */
div[class*="st-key-opts"] { gap:8px !important; }
div[class*="st-key-opts"] .stButton button { min-height:48px; justify-content:flex-start; padding-left:18px; }
div[class*="st-key-opts"] .stButton button p { font-weight:600 !important; }
div[class*="st-key-opts"] button[kind="secondary"]:hover, div[class*="st-key-opts"] button[data-testid="stBaseButton-secondary"]:hover { border-color:#b8c2ff !important; background:#fafbff !important; }
div[class*="st-key-opts"] button[kind="primary"], div[class*="st-key-opts"] button[data-testid="stBaseButton-primary"] { background:var(--accent-soft) !important; color:var(--accent) !important; border:1.5px solid var(--accent) !important; }

/* 이름 입력 */
.stTextInput label p { font-size:15px !important; font-weight:700; }
.stTextInput input { border-radius:10px !important; padding:12px 14px !important; font-size:15px !important; background:#fff !important; }
.hint { text-align:center; color:var(--sub); font-size:13px; margin:8px 0 0; }

/* 결과 */
.hero-card { background:#fff; border:1px solid var(--line); border-radius:20px; padding:36px 28px; text-align:center; }
.hero-card .who { color:var(--sub); font-size:15px; }
.hero-card .type { font-size:68px; font-weight:800; letter-spacing:5px; color:var(--accent); line-height:1.2; margin:6px 0; }
.hero-card .nick { font-size:22px; font-weight:800; }
.hero-card .desc { color:var(--sub); font-size:15px; line-height:1.7; margin-top:8px; word-break:keep-all; }
.axis { padding:14px 0; border-bottom:1px solid var(--line); }
.axis:last-child { border-bottom:0; }
.axis-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
.axis-head .title { font-weight:700; font-size:14px; }
.badge { font-size:12px; font-weight:700; border-radius:99px; padding:3px 9px; }
.badge.strong { background:var(--accent-soft); color:var(--accent); }
.badge.mid { background:#f2f4f6; color:var(--sub); }
.badge.half { background:#fff4e5; color:#e67700; }
.axis-labels { display:flex; justify-content:space-between; font-size:13px; color:#adb5bd; margin-bottom:6px; }
.axis-labels .win { color:var(--ink); font-weight:700; }
.axis-labels .win em { color:var(--accent); font-style:normal; }
.alt { background:#fff8ee; border:1px solid #ffe2b8; border-radius:16px; padding:18px 20px; font-size:14px; line-height:1.7; }
.alt b { color:#e67700; }
.info-title { font-size:13px; font-weight:700; color:var(--sub); margin-bottom:8px; }
.tags { display:flex; gap:6px; flex-wrap:wrap; }
.tag { background:var(--accent-soft); color:var(--accent); font-weight:700; font-size:13px; border-radius:8px; padding:5px 10px; }
.foot { text-align:center; color:#adb5bd; font-size:12px; line-height:1.6; margin-top:28px; }
</style>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# 5-A. 시작 화면
# ═════════════════════════════════════════════
if ss.stage == "intro":
    st.markdown(f"""
    <div class="eyebrow">MBTI 성향 검사</div>
    <div class="h1">나의 진짜 성향을<br>찾아보세요</div>
    <p class="lead">24개의 문장에 얼마나 동의하는지 답하면, 4가지 지표의 강도를 분석해 나의 유형을 알려드려요.</p>
    <div class="chips">
      <span class="chip"><b>{N}</b>문항</span>
      <span class="chip">약 <b>3</b>분</span>
      <span class="chip"><b>5</b>점 척도</span>
      <span class="chip">결과 즉시 확인</span>
    </div>

    <div class="section">검사는 이렇게 진행돼요</div>
    <div class="box">
      <div class="step"><div class="num">1</div><div><div class="t">문장 응답</div>
        <div class="small">카드를 한 장씩 넘기며 '매우 그렇다'부터 '전혀 아니다'까지 골라 주세요.</div></div></div>
      <div class="step"><div class="num">2</div><div><div class="t">지표 강도 분석</div>
        <div class="small">4가지 지표마다 어느 쪽에 얼마나 가까운지 비율로 계산해요.</div></div></div>
      <div class="step"><div class="num">3</div><div><div class="t">유형과 반반 지표 안내</div>
        <div class="small">최종 유형과 함께, 차이가 작은 지표가 있으면 두 번째 후보 유형도 알려드려요.</div></div></div>
    </div>

    <div class="section">4가지 지표</div>
    <div class="grid">
      {''.join(f'<div class="box axis-box"><div class="letters">{f} · {s}</div><div class="name">{name}</div>'
               f'<div class="small">{desc}</div></div>' for f, s, name, _, _, desc in AXES)}
    </div>
    <div class="section">시작하기</div>
    """, unsafe_allow_html=True)

    name = st.text_input("이름", placeholder="이름을 입력하고 Enter", key=f"name_{ss.round}")
    st.button("검사 시작하기", type="primary", width="stretch", disabled=not name.strip(), on_click=start_test)
    if not name.strip():
        st.markdown('<p class="hint">이름을 입력하면 시작할 수 있어요</p>', unsafe_allow_html=True)


# ═════════════════════════════════════════════
# 5-B. 검사 화면 (카드 한 장씩 넘기기)
# ═════════════════════════════════════════════
elif ss.stage == "test":
    i = ss.idx
    q = QUESTIONS[i]
    done = len(ss.answers)

    st.markdown(f"""
    <div class="progress-row"><span>{html.escape(ss.name)}님의 성향 찾는 중</span><span><b>{done}</b> / {N}</span></div>
    <div class="progress-track"><div class="progress-fill" style="width:{done / N * 100}%"></div></div>
    """, unsafe_allow_html=True)

    # key에 문항 번호와 방향을 넣어서, 카드가 바뀔 때마다 새로 그려지며 슬라이드 애니메이션이 실행됨
    with st.container(key=f"qcard_{ss.round}_{i}_{ss.direction}"):
        st.markdown(f"""
        <span class="q-tag">{q['axis_name']}</span>
        <div class="q-num">Q{i + 1}</div>
        <div class="q-text">{q['text']}</div>
        """, unsafe_allow_html=True)

        with st.container(key=f"opts_{ss.round}_{i}"):
            for label, value in SCALE:
                selected = ss.answers.get(i) == value
                st.button(("✓  " if selected else "") + label, key=f"opt_{ss.round}_{i}_{value}",
                          type="primary" if selected else "secondary", width="stretch",
                          on_click=choose, args=(i, value))

    st.write("")
    col_prev, col_next = st.columns(2)
    with col_prev:
        st.button("← 이전", width="stretch", disabled=i == 0, on_click=move, args=(-1,))
    with col_next:
        if i < N - 1:
            st.button("다음 →", width="stretch", disabled=i not in ss.answers, on_click=move, args=(1,))
        else:
            st.button("결과 보기", type="primary", width="stretch", disabled=done < N, on_click=finish)

    st.markdown('<p class="hint">답을 고르면 다음 카드로 자동으로 넘어가요</p>', unsafe_allow_html=True)


# ═════════════════════════════════════════════
# 5-C. 결과 화면
# ═════════════════════════════════════════════
else:
    r = ss.result
    mbti = r["type"]
    nick, desc, strengths, caution, jobs = TYPES[mbti]

    # (1) 대표 결과 카드
    st.markdown(f"""
    <div class="hero-card">
      <div class="who">{html.escape(ss.name)}님의 성향은</div>
      <div class="type">{mbti}</div>
      <div class="nick">{nick}</div>
      <div class="desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

    # (2) 지표별 강도
    rows, closest = "", None
    for first, second, axis_name, first_kr, second_kr, _ in AXES:
        win, first_pct, pct, strength = axis_detail(first, second, r["scores"][first + second])
        if closest is None or pct < closest[1]:
            closest = (first + second, pct, win)
        first_win = win == first
        badge = {"뚜렷함": "strong", "보통": "mid", "반반": "half"}[strength]
        rows += f"""
        <div class="axis">
          <div class="axis-head"><span class="title">{axis_name}</span><span class="badge {badge}">{strength}</span></div>
          <div class="axis-labels">
            <span class="{'win' if first_win else ''}">{first_kr} {first} <em>{first_pct}%</em></span>
            <span class="{'' if first_win else 'win'}"><em>{100 - first_pct}%</em> {second_kr} {second}</span>
          </div>
          <div class="progress-track" style="justify-content:{'flex-start' if first_win else 'flex-end'}">
            <div class="progress-fill" style="width:{pct}%"></div>
          </div>
        </div>"""
    st.markdown(f'<div class="section">지표별 분석</div><div class="box">{rows}</div>', unsafe_allow_html=True)

    # (3) 반반 지표가 있으면 두 번째 후보 유형 안내
    axis, pct, win = closest
    if pct < 60:
        other = axis[1] if win == axis[0] else axis[0]
        alt_type = mbti.replace(win, other)
        st.markdown(f"""
        <div class="section">반반 지표</div>
        <div class="alt"><b>{axis[0]} / {axis[1]}</b> 지표가 거의 반반이에요. 상황에 따라
        <b>{alt_type}</b> ({TYPES[alt_type][0]})의 모습도 함께 나타날 수 있어요.</div>
        """, unsafe_allow_html=True)

    # (4) 강점 · 주의할 점 · 잘 맞는 일
    tags = "".join(f'<span class="tag">{s}</span>' for s in strengths)
    st.markdown(f"""
    <div class="section">나의 성격 이야기</div>
    <div class="grid">
      <div class="box"><div class="info-title">강점</div><div class="tags">{tags}</div></div>
      <div class="box"><div class="info-title">잘 맞는 일</div><div class="small" style="color:var(--ink)">{jobs}</div></div>
    </div>
    <div class="box" style="margin-top:10px"><div class="info-title">주의할 점</div>
      <div class="small" style="color:var(--ink)">{caution}</div></div>
    """, unsafe_allow_html=True)

    # (5) 내 응답 다시 보기
    st.write("")
    with st.expander("내 응답 다시 보기"):
        for n, item in enumerate(QUESTIONS):
            st.markdown(f"**Q{n + 1}.** {item['text']} → `{SCALE_LABEL[ss.answers[n]]}`")

    st.button("처음부터 다시 하기", type="primary", width="stretch", on_click=restart)

st.markdown('<div class="foot">MBTI 이론을 참고해 만든 간단한 실습용 검사이며,<br>공식 MBTI 검사가 아니에요.</div>',
            unsafe_allow_html=True)

# 화면이 바뀐 직후에만 한 번 맨 위로 이동
if ss.do_scroll:
    scroll_to_top()
    ss.do_scroll = False