from __future__ import annotations

import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # volta até a raiz do projeto
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.application.use_cases import ChatAgentUC
from src.config import settings
from src.domain.models import ChatMessage
from src.infrastructure.openai_llm import OpenAILLMAdapter


st.set_page_config(
    page_title="Grupo Fácil IA",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.5rem; }
      .gf-title {
        font-size: 2.0rem; font-weight: 700; letter-spacing: 0.5px;
        margin-bottom: 0.25rem;
      }
      .gf-sub { opacity: 0.75; margin-top: -0.2rem; }
      .gf-badge {
        display:inline-block; padding: 0.25rem 0.6rem; border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.18); font-size: 0.85rem;
        opacity: 0.9;
      }
      .gf-panel {
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px; padding: 14px 14px; background: rgba(255,255,255,0.03);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="gf-title">Grupo Fácil IA <span class="gf-badge">Agente Motor</span></div>', unsafe_allow_html=True)
st.markdown('<div class="gf-sub">A IA oficial do Grupo Fácil — base para outros agentes e serviços.</div>', unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.header("Configurações")
    model = st.text_input("Modelo", value=settings.llm_model)
    st.caption("Troque o modelo aqui sem redeploy.")

    st.markdown("---")
    st.subheader("Status")
    if "history" not in st.session_state:
        st.session_state.history = []
    st.write(f"Mensagens na sessão: **{len(st.session_state.history)}**")

    if st.button("Limpar conversa"):
        st.session_state.history = []
        st.rerun()

try:
    llm = OpenAILLMAdapter(api_key=st.secrets.get("OPENAI_API_KEY", None))
except Exception:
    llm = OpenAILLMAdapter(api_key=settings.openai_api_key)

agent = ChatAgentUC(llm=llm)

colA, colB = st.columns([2, 1], gap="large")

with colA:
    st.markdown('<div class="gf-panel">', unsafe_allow_html=True)
    st.subheader("Chat")

    for m in st.session_state.history:
        with st.chat_message(m.role):
            st.markdown(m.content)

    user_text = st.chat_input("Digite sua mensagem…")
    st.markdown("</div>", unsafe_allow_html=True)

with colB:
    st.markdown('<div class="gf-panel">', unsafe_allow_html=True)
    st.subheader("Painel")
    st.write("Próximas evoluções:")
    st.write("- RAG (documentos internos)")
    st.write("- Agentes satélites por área")
    st.write("- Políticas e governança")
    st.markdown("</div>", unsafe_allow_html=True)

if user_text:
    st.session_state.history.append(ChatMessage(role="user", content=user_text))
    with st.chat_message("assistant"):
        with st.spinner("Pensando…"):
            resp = agent.run(model=model, history=st.session_state.history[:-1], user_text=user_text)
            st.markdown(resp.text)
            st.caption(f"Modelo: {resp.used_model} • Latência: {resp.latency_ms} ms")
    st.session_state.history.append(ChatMessage(role="assistant", content=resp.text))