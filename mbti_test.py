import html
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MBTI 성향 테스트", page_icon="🧭", layout="centered")

# ─────────────────────────────────────────────
# 1. 데이터
#    (첫 글자, 둘째 글자, 질문, 첫 글자 선택지, 둘째 글자 선택지)
# ─────────────────────────────────────────────
QUESTIONS = [
    ("E", "I", "주말에는 보통?", "밖으로 나가 사람들을 만난다", "집에서 쉬면서 충전한다"),
    ("E", "I", "새로운 사람을 만나는 것이", "편하고 즐겁다", "조금 부담된다"),
    ("E", "I", "공부할 때 더 편한 것은?", "친구들과 같이", "혼자 조용히"),
    ("S", "N", "새로운 정보를 접할 때", "구체적인 사실부터 본다", "가능성과 의미를 상상한다"),
    ("S", "N", "여행 계획을 세울 때", "세부 일정을 꼼꼼히 짠다", "큰 방향만 정하고 떠난다"),
    ("S", "N", "설명을 들을 때 더 좋은 것은?", "실제 사례와 경험", "아이디어와 큰 그림"),
    ("T", "F", "친구가 고민을 털어놓으면", "해결 방법을 함께 찾는다", "먼저 마음을 공감해 준다"),
    ("T", "F", "중요한 결정을 할 때", "논리와 근거를 우선한다", "사람들의 마음을 고려한다"),
    ("T", "F", "갈등 상황에서는", "사실을 분명히 정리한다", "관계가 상하지 않게 배려한다"),
    ("J", "P", "하루 일과를 보낼 때", "계획대로 움직이는 편이다", "상황에 따라 유연하게 움직인다"),
    ("J", "P", "마감이 다가오면", "미리 끝내 두는 편이다", "막판 집중력이 올라간다"),
    ("J", "P", "약속이 갑자기 바뀌면", "계획이 틀어져 불편하다", "새로운 상황도 괜찮다"),
]
GROUPS = ["에너지 방향", "정보 인식", "판단 기준", "생활 방식"]
AXES = [("E", "I", "외향", "내향"), ("S", "N", "감각", "직관"),
        ("T", "F", "사고", "감정"), ("J", "P", "판단", "인식")]

TYPES = {
    "ISTJ": ("믿음직한 원칙주의자", "맡은 일은 끝까지 책임지는 성실한 타입이에요."),
    "ISFJ": ("따뜻한 수호자", "조용히 주변 사람을 챙기는 다정한 타입이에요."),
    "INFJ": ("통찰력 있는 조언자", "사람의 마음을 잘 읽고 깊은 의미를 찾는 타입이에요."),
    "INTJ": ("치밀한 전략가", "큰 그림을 그리고 계획대로 실행하는 타입이에요."),
    "ISTP": ("만능 해결사", "문제가 생기면 직접 뜯어보고 고치는 타입이에요."),
    "ISFP": ("감성 예술가", "자신만의 감성과 취향이 뚜렷한 타입이에요."),
    "INFP": ("꿈꾸는 이상주의자", "따뜻한 가치와 상상력이 가득한 타입이에요."),
    "INTP": ("호기심 많은 탐구자", "'왜?'라는 질문을 멈추지 않는 논리적인 타입이에요."),
    "ESTP": ("행동파 모험가", "생각보다 몸이 먼저 움직이는 에너지 넘치는 타입이에요."),
    "ESFP": ("분위기 메이커", "어디서든 사람들을 즐겁게 만드는 타입이에요."),
    "ENFP": ("열정적인 아이디어 뱅크", "새로운 가능성에 늘 설레는 자유로운 타입이에요."),
    "ENTP": ("재치 있는 발명가", "토론과 새로운 시도를 즐기는 아이디어형 타입이에요."),
    "ESTJ": ("든든한 관리자", "체계를 세우고 팀을 이끄는 리더 타입이에요."),
    "ESFJ": ("다정한 사교가", "모두가 함께 잘 지내도록 챙기는 타입이에요."),
    "ENFJ": ("따뜻한 리더", "사람들의 성장을 돕고 이끄는 타입이에요."),
    "ENTJ": ("대담한 지휘관", "목표를 정하면 거침없이 밀고 나가는 타입이에요."),
}

# ─────────────────────────────────────────────
# 2. 상태(session_state) 준비
#    round     : '다시 하기'를 누를 때마다 1씩 증가 → 위젯 key가 바뀌어 새 질문지가 됨
#    do_scroll : 버튼을 눌렀을 때만 True → 딱 한 번만 맨 위로 이동
# ─────────────────────────────────────────────
ss = st.session_state
ss.setdefault("round", 0)
ss.setdefault("result", None)
ss.setdefault("scroll_id", 0)
ss.setdefault("do_scroll", False)

NAME_KEY = f"r{ss.round}_name"


def q_key(i):
    return f"r{ss.round}_q{i}"


def submit():
    """결과 계산 (버튼 클릭 시 실행되는 콜백)"""
    scores = {}
    for first, second, *_ in AXES:
        idx = [i for i, q in enumerate(QUESTIONS) if q[0] == first]
        scores[first] = sum(ss[q_key(i)] == QUESTIONS[i][3] for i in idx)
        scores[second] = len(idx) - scores[first]
    mbti = "".join(f if scores[f] > scores[s] else s for f, s, *_ in AXES)
    ss.result = {"name": ss[NAME_KEY].strip(), "type": mbti, "scores": scores}
    ss.do_scroll = True


def restart():
    """처음부터 다시 하기 (버튼 클릭 시 실행되는 콜백)"""
    ss.round += 1
    ss.result = None
    ss.do_scroll = True


def scroll_to_top():
    """화면을 맨 위로 올리는 스크립트 (버튼을 누른 직후 한 번만 실행)"""
    ss.scroll_id += 1
    components.html(f"""<script>
    // {ss.scroll_id}
    const d = window.parent.document;
    ['[data-testid="stMain"]', '.stMain', 'section.main', '[data-testid="stAppViewContainer"]']
      .forEach(s => {{ const el = d.querySelector(s); if (el) el.scrollTo({{top: 0}}); }});
    window.parent.scrollTo({{top: 0}});
    </script>""", height=0)


# ─────────────────────────────────────────────
# 3. 디자인 (CSS)
# ─────────────────────────────────────────────
st.markdown("""<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
:root { --ink:#191f28; --sub:#6b7684; --line:#e5e8eb; --bg:#f7f8fa; --accent:#3d5afe; --accent-soft:#eef1ff; }
.stApp { background: var(--bg); color: var(--ink); }
html, body, .stApp, .stMarkdown, button, input, label, p { font-family: 'Pretendard', sans-serif !important; }
.block-container { max-width: 680px !important; padding-top: 3rem !important; padding-bottom: 4rem !important; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
div[data-testid="stElementContainer"]:has(iframe[height="0"]) { display: none; }

/* 상단 제목 */
.hero h1 { font-size: 32px; font-weight: 800; letter-spacing: -0.5px; margin: 0 0 8px; color: var(--ink); }
.hero p { color: var(--sub); font-size: 15px; margin: 0 0 28px; }
.hello { color: var(--accent); font-weight: 600; font-size: 15px; margin: -4px 0 8px; }

/* 진행률 */
.progress-row { display:flex; justify-content:space-between; font-size:14px; color:var(--sub); margin:24px 0 6px; }
.progress-track { height:8px; background:var(--line); border-radius:99px; overflow:hidden; display:flex; }
.progress-fill { height:100%; background:var(--accent); border-radius:99px; transition: width .3s ease; }

/* 구역 제목 (1. 에너지 방향 ...) */
.group { font-size:20px; font-weight:800; color:var(--accent); margin:40px 0 12px; }

/* 질문 카드 - 모든 카드가 같은 폭이 되도록 */
div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) { width:100% !important; }
div[data-testid="stRadio"] { width:100% !important; box-sizing:border-box;
    background:#fff; border:1px solid var(--line); border-radius:16px; padding:20px 22px 16px; margin-bottom:12px; }
div[data-testid="stRadio"] > div { width:100%; }
div[data-testid="stRadio"] [data-testid="stWidgetLabel"] p { font-size:17px; font-weight:700; color:var(--ink); margin-bottom:6px; }
div[data-testid="stRadio"] div[role="radiogroup"] { gap:8px; width:100%; }
div[data-testid="stRadio"] label[data-baseweb="radio"] { width:100%; box-sizing:border-box; border:1px solid var(--line); border-radius:10px; padding:12px 14px; margin:0; transition:.15s; }
div[data-testid="stRadio"] label[data-baseweb="radio"] p { font-size:15px; }
div[data-testid="stRadio"] label[data-baseweb="radio"]:hover { border-color:#b8c2ff; }
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) { background:var(--accent-soft); border-color:var(--accent); }

/* 이름 입력 */
.stTextInput label p { font-size:15px !important; font-weight:700; }
.stTextInput input { border-radius:10px !important; padding:12px 14px !important; font-size:15px !important; background:#fff !important; }

/* 버튼 */
.stButton button { border-radius:12px !important; min-height:52px; }
.stButton button p { font-weight:700 !important; font-size:16px !important; }
.stButton button[kind="primary"] { background:var(--accent) !important; border:0 !important; color:#fff !important; }
.stButton button[kind="primary"]:disabled { background:#d1d6db !important; color:#fff !important; cursor:not-allowed; }
.hint { text-align:center; color:var(--sub); font-size:14px; margin:8px 0 0; }

/* 결과 카드 */
.card { background:#fff; border:1px solid var(--line); border-radius:20px; padding:40px 32px; margin:8px 0 16px; }
.card .who { color:var(--sub); font-size:16px; text-align:center; }
.card .type { font-size:72px; font-weight:800; letter-spacing:5px; color:var(--accent); text-align:center; line-height:1.2; margin:8px 0; }
.card .nick { font-size:22px; font-weight:700; text-align:center; }
.card .desc { color:var(--sub); font-size:16px; text-align:center; margin:8px 0 32px; }
.axis { margin-top:18px; }
.axis-labels { display:flex; justify-content:space-between; font-size:14px; color:#adb5bd; margin-bottom:6px; }
.axis-labels .win { color:var(--ink); font-weight:700; }
.axis-labels .win em { color:var(--accent); font-style:normal; }
.foot { text-align:center; color:#adb5bd; font-size:13px; margin-top:28px; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>MBTI 성향 테스트</h1>'
            '<p>12개의 질문으로 알아보는 나의 성향. 정답은 없어요.</p></div>',
            unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4-A. 질문 화면
# ─────────────────────────────────────────────
if ss.result is None:
    name = st.text_input("이름", placeholder="이름을 입력하고 Enter", key=NAME_KEY)
    if name.strip():
        st.markdown(f'<div class="hello">{html.escape(name.strip())}님, 반가워요! 아래 질문에 답해 주세요.</div>',
                    unsafe_allow_html=True)

    answered = sum(ss.get(q_key(i)) is not None for i in range(len(QUESTIONS)))
    pct = answered / len(QUESTIONS) * 100
    st.markdown(f'<div class="progress-row"><span>진행률</span><span>{answered} / {len(QUESTIONS)}</span></div>'
                f'<div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>',
                unsafe_allow_html=True)

    for i, (_, _, question, a, b) in enumerate(QUESTIONS):
        if i % 3 == 0:
            st.markdown(f'<div class="group">{i // 3 + 1}. {GROUPS[i // 3]}</div>', unsafe_allow_html=True)
        st.radio(f"Q{i + 1}. {question}", [a, b], index=None, key=q_key(i), width="stretch")

    st.write("")
    remaining = len(QUESTIONS) - answered
    ready = remaining == 0 and bool(name.strip())

    # 모든 조건을 채우기 전에는 버튼이 비활성화(disabled)됨
    st.button("결과 보기", type="primary", width="stretch", disabled=not ready, on_click=submit)
    if remaining > 0:
        st.markdown(f'<p class="hint">질문 {remaining}개가 남았어요</p>', unsafe_allow_html=True)
    elif not name.strip():
        st.markdown('<p class="hint">이름을 입력하면 결과를 볼 수 있어요</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4-B. 결과 화면
# ─────────────────────────────────────────────
else:
    r = ss.result
    nick, desc = TYPES[r["type"]]

    bars = ""
    for first, second, first_kr, second_kr in AXES:
        f_score, s_score = r["scores"][first], r["scores"][second]
        f_pct = round(f_score / (f_score + s_score) * 100)
        s_pct = 100 - f_pct
        first_win = f_pct > s_pct

        # 더 높은 쪽에서부터 막대가 채워지도록 (왼쪽 또는 오른쪽 정렬)
        align = "flex-start" if first_win else "flex-end"
        fill = f_pct if first_win else s_pct
        left_cls = "win" if first_win else ""
        right_cls = "" if first_win else "win"

        bars += (f'<div class="axis"><div class="axis-labels">'
                 f'<span class="{left_cls}">{first_kr} {first} <em>{f_pct}%</em></span>'
                 f'<span class="{right_cls}"><em>{s_pct}%</em> {second_kr} {second}</span></div>'
                 f'<div class="progress-track" style="justify-content:{align}">'
                 f'<div class="progress-fill" style="width:{fill}%"></div></div></div>')

    st.markdown(f'''<div class="card">
        <div class="who">{html.escape(r["name"])}님의 성향은</div>
        <div class="type">{r["type"]}</div>
        <div class="nick">{nick}</div>
        <div class="desc">{desc}</div>
        {bars}
    </div>''', unsafe_allow_html=True)

    st.button("처음부터 다시 하기", type="primary", width="stretch", on_click=restart)

st.markdown('<div class="foot">재미로 보는 간단한 성향 테스트예요</div>', unsafe_allow_html=True)

# 버튼을 누른 직후에만 한 번 맨 위로 이동하고, 바로 꺼 둠
if ss.do_scroll:
    scroll_to_top()
    ss.do_scroll = False