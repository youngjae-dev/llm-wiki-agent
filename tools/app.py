"""
tools/app.py — ArchWiki Streamlit GUI
3-패널 레이아웃: 좌측(검색+네비), 중앙(위키 콘텐츠), 우측(AI 에이전트 채팅)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import streamlit as st

# ── wiki_core를 sys.path에 추가 (repo root) ───────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))
import wiki_core as wc

# ────────────────────────────────────────────────────────────────────────────
# 페이지 설정
# ────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ArchWiki — 시스템 아키텍처 설계 위키",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* 전체 배경 */
[data-testid="stAppViewContainer"] {
    background-color: #0f1117;
}
/* 사이드바 */
[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}
/* 카드 공통 */
.wiki-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: border-color 0.2s;
}
.wiki-card:hover { border-color: #58a6ff; }
.wiki-card.active { border-color: #58a6ff; background: #1f2a3a; }
/* 태그 뱃지 */
.tag-badge {
    display: inline-block;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 2px 10px;
    margin: 2px;
    font-size: 12px;
    color: #8b949e;
}
/* 메타데이터 바 */
.meta-bar {
    display: flex;
    gap: 20px;
    padding: 10px 0;
    border-bottom: 1px solid #30363d;
    margin-bottom: 20px;
    font-size: 13px;
    color: #8b949e;
}
/* 채팅 말풍선 */
.chat-user {
    background: #1f6feb;
    color: white;
    border-radius: 12px 12px 4px 12px;
    padding: 10px 14px;
    margin: 6px 0 6px 40px;
    font-size: 14px;
}
.chat-agent {
    background: #21262d;
    border: 1px solid #30363d;
    color: #e6edf3;
    border-radius: 12px 12px 12px 4px;
    padding: 10px 14px;
    margin: 6px 40px 6px 0;
    font-size: 14px;
}
/* 섹션 헤더 */
.section-header {
    color: #8b949e;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 8px 0 4px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# 상태 초기화
# ────────────────────────────────────────────────────────────────────────────

if "selected_slug" not in st.session_state:
    st.session_state.selected_slug = "10-project-classification"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# ────────────────────────────────────────────────────────────────────────────
# 헬퍼 함수
# ────────────────────────────────────────────────────────────────────────────

TAG_COLORS = {
    "architecture-patterns": "#1f6feb",
    "agent-design": "#388bfd",
    "sdlc": "#2da44e",
    "mcp": "#d29922",
    "llm": "#8b949e",
    "sequential": "#388bfd",
    "parallel": "#58a6ff",
    "plan-mode": "#d29922",
    "claude-code": "#bc8cff",
    "execution-environment": "#2da44e",
    "documentation": "#58a6ff",
}


def tag_badge(tag: str) -> str:
    color = TAG_COLORS.get(tag, "#30363d")
    return (
        f'<span style="display:inline-block;background:{color}22;border:1px solid {color}66;'
        f'border-radius:12px;padding:2px 10px;margin:2px;font-size:12px;color:{color};">'
        f"{tag}</span>"
    )


def call_agent(user_msg: str, wiki_context: str) -> str:
    """Claude CLI subprocess를 호출하여 에이전트 응답을 얻는다."""
    system_prompt = (
        "You are ArchWiki Agent, an expert in system architecture design for personal projects. "
        "You have access to the following wiki context. Answer in Korean when the user writes in Korean. "
        "Be concise and reference relevant wiki pages.\n\n"
        f"=== Current Wiki Context ===\n{wiki_context[:3000]}\n=== End Context ==="
    )

    full_prompt = f"{system_prompt}\n\nUser: {user_msg}"

    try:
        result = subprocess.run(
            ["claude", "-p", "--output-format", "json", "--no-session-persistence"],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return data.get("result", data.get("content", str(data)))
            except json.JSONDecodeError:
                return result.stdout.strip()
        else:
            return f"[에이전트 오류] {result.stderr.strip()[:300]}"
    except FileNotFoundError:
        return "[오류] Claude CLI를 찾을 수 없습니다. `claude` 명령이 PATH에 있는지 확인하세요."
    except subprocess.TimeoutExpired:
        return "[오류] 에이전트 응답 시간 초과 (60초)"


# ────────────────────────────────────────────────────────────────────────────
# 레이아웃
# ────────────────────────────────────────────────────────────────────────────

col_sidebar, col_main, col_chat = st.columns([1, 2.2, 1.3])

# ──────────────────────────────────────────────
# 좌측 사이드바: 검색 + 페이지 네비게이션
# ──────────────────────────────────────────────

with col_sidebar:
    st.markdown("## 🏗️ ArchWiki")
    st.markdown('<p style="color:#8b949e;font-size:13px;margin-top:-10px;">시스템 아키텍처 설계 지식 베이스</p>', unsafe_allow_html=True)

    st.divider()

    # 검색
    query = st.text_input("🔍 검색", value=st.session_state.search_query, placeholder="패턴, 캐싱, microservices...", label_visibility="collapsed")

    if query:
        st.session_state.search_query = query
        results = wc.search(query)
        st.markdown('<div class="section-header">검색 결과</div>', unsafe_allow_html=True)
        if results:
            for r in results:
                is_active = r["slug"] == st.session_state.selected_slug
                border = "#58a6ff" if is_active else "#30363d"
                bg = "#1f2a3a" if is_active else "#161b22"
                label = f"**{r['title'][:28]}**" + (" ✓" if is_active else "")
                if st.button(
                    f"{r['title'][:34]}",
                    key=f"search_{r['slug']}",
                    help=r.get("snippet", ""),
                    use_container_width=True,
                ):
                    st.session_state.selected_slug = r["slug"]
                    st.rerun()
        else:
            st.caption("검색 결과가 없습니다.")
    else:
        # 전체 페이지 목록
        pages = wc.get_all_pages()

        domain_10_16 = [p for p in pages if p["slug"].startswith(("10", "11", "12", "13", "14", "15", "16"))]
        domain_01_09 = [p for p in pages if not p["slug"].startswith(("10", "11", "12", "13", "14", "15", "16"))]

        if domain_10_16:
            st.markdown('<div class="section-header">🏛️ 아키텍처 설계 도메인</div>', unsafe_allow_html=True)
            for p in domain_10_16:
                is_active = p["slug"] == st.session_state.selected_slug
                label = ("▶ " if is_active else "  ") + p["title"][:30]
                if st.button(label, key=f"nav_{p['slug']}", use_container_width=True):
                    st.session_state.selected_slug = p["slug"]
                    st.rerun()

        if domain_01_09:
            st.markdown('<div class="section-header">🤖 Agentic Coding</div>', unsafe_allow_html=True)
            for p in domain_01_09:
                is_active = p["slug"] == st.session_state.selected_slug
                label = ("▶ " if is_active else "  ") + p["title"][:30]
                if st.button(label, key=f"nav_{p['slug']}", use_container_width=True):
                    st.session_state.selected_slug = p["slug"]
                    st.rerun()

# ──────────────────────────────────────────────
# 중앙: 위키 콘텐츠 뷰어
# ──────────────────────────────────────────────

with col_main:
    page = wc.get_page(st.session_state.selected_slug)

    if page is None:
        st.warning("페이지를 찾을 수 없습니다.")
    else:
        # 메타데이터 바
        tag_html = "".join(tag_badge(t) for t in page["tags"])
        st.markdown(
            f'<div class="meta-bar">'
            f'<span>📄 {page["slug"]}.md</span>'
            f'<span>v{page["version"]}</span>'
            f'<span>📅 {page["date"]}</span>'
            f'<span>📁 {page["source"][:30]}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

        # 제목
        st.markdown(f"# {page['title']}")

        # 태그 뱃지
        if page["tags"]:
            st.markdown(tag_html, unsafe_allow_html=True)
            st.markdown("")

        # 관련 페이지
        related_slugs = wc.get_related_slugs(page["slug"])
        if related_slugs:
            related_pages = [wc.get_page(s.strip()) for s in related_slugs if wc.get_page(s.strip())]
            if related_pages:
                cols = st.columns(len(related_pages[:3]))
                for i, rp in enumerate(related_pages[:3]):
                    with cols[i]:
                        if st.button(f"→ {rp['title'][:28]}", key=f"rel_{rp['slug']}_{page['slug']}", use_container_width=True):
                            st.session_state.selected_slug = rp["slug"]
                            st.rerun()

        st.divider()

        # 본문
        st.markdown(page["body"])

# ──────────────────────────────────────────────
# 우측: 위키 에이전트 채팅
# ──────────────────────────────────────────────

with col_chat:
    st.markdown("### 💬 위키 에이전트")
    st.markdown('<p style="color:#8b949e;font-size:12px;margin-top:-8px;">현재 페이지 기반으로 아키텍처를 설명합니다</p>', unsafe_allow_html=True)

    # 채팅 히스토리 표시
    chat_container = st.container(height=480)
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown(
                '<div class="chat-agent">'
                '안녕하세요! 저는 <b>ArchWiki Agent</b>입니다.<br>'
                '현재 위키 페이지를 기반으로 아키텍처 설계를 도와드립니다.<br><br>'
                '예시 질문:<br>'
                '• "이 프로젝트에 적합한 패턴은?"<br>'
                '• "마이크로서비스 vs 모듈형 모놀리식 차이?"<br>'
                '• "캐싱 전략을 설명해줘"</div>',
                unsafe_allow_html=True,
            )
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-agent">{msg["content"]}</div>', unsafe_allow_html=True)

    # 입력
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "메시지",
            placeholder="아키텍처 질문을 입력하세요...",
            height=80,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("전송 ↵", use_container_width=True)

    if submitted and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})

        # 현재 페이지 컨텍스트 + 검색 컨텍스트 구성
        ctx_page = wc.get_page(st.session_state.selected_slug) or {}
        search_results = wc.search(user_input, top_k=3)
        search_ctx = "\n".join(
            f"[{r['slug']}] {r['title']}: {r['snippet']}" for r in search_results
        )
        wiki_context = (
            f"=== 현재 보고 있는 페이지: {ctx_page.get('title', '')} ===\n"
            f"{ctx_page.get('body', '')[:1500]}\n\n"
            f"=== 관련 검색 결과 ===\n{search_ctx}"
        )

        with st.spinner("에이전트 응답 중..."):
            response = call_agent(user_input.strip(), wiki_context)

        st.session_state.chat_history.append({"role": "agent", "content": response})
        st.rerun()

    # 채팅 초기화
    if st.session_state.chat_history:
        if st.button("대화 초기화", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    st.divider()

    # 현재 페이지 정보 요약
    st.markdown('<div class="section-header">현재 페이지</div>', unsafe_allow_html=True)
    if page:
        st.markdown(f"**{page['title']}**")
        st.markdown(f"`{page['slug']}`  v{page['version']}")
        if page["tags"]:
            st.markdown("".join(tag_badge(t) for t in page["tags"]), unsafe_allow_html=True)
