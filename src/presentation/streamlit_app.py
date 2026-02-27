# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.application.document_use_cases import ExplainPdfUC
from src.application.use_cases import ChatAgentUC
from src.config import settings
from src.domain.models import ChatMessage
from src.infrastructure.gemini_llm import GeminiLLMAdapter
from src.infrastructure.pdf_extractor import PdfTextExtractor

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Grupo Fácil IA",
    page_icon="💡",
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
        display: inline-block; padding: 0.25rem 0.6rem; border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.18); font-size: 0.85rem;
        opacity: 0.9;
      }
      .gf-panel {
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px; padding: 14px; background: rgba(255,255,255,0.03);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="gf-title">Grupo Fácil IA <span class="gf-badge">Agente Motor</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="gf-sub">A IA oficial do Grupo Fácil — base para outros agentes e serviços.</div>',
    unsafe_allow_html=True,
)
st.divider()

# ---------------------------------------------------------------------------
# Estado da sessão
# ---------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history: list[ChatMessage] = []

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Configurações")
    model = st.text_input("Modelo", value=settings.gemini_model)
    st.caption("Troque o modelo aqui sem redeploy.")

    st.markdown("---")
    st.subheader("Leitor de PDF")

    uploaded_pdf = st.file_uploader("Enviar PDF", type=["pdf"])
    pdf_goal = st.text_area(
        "O que você quer entender deste PDF?",
        value="Explique o conteúdo em linguagem simples e destaque os pontos importantes.",
        height=100,
    )
    max_pages = st.number_input(
        "Limite de páginas para leitura",
        min_value=1,
        max_value=200,
        value=15,
    )
    run_pdf = st.button("Explicar PDF", use_container_width=True)

    st.markdown("---")
    st.subheader("Status da sessão")
    st.write(f"Mensagens: **{len(st.session_state.history)}**")

    if st.button("Limpar conversa", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ---------------------------------------------------------------------------
# Instâncias de serviço
# ---------------------------------------------------------------------------
@st.cache_resource
def get_llm() -> GeminiLLMAdapter:
    api_key = (
        st.secrets.get("GEMINI_API_KEY")
        if hasattr(st, "secrets")
        else None
    ) or settings.gemini_api_key
    return GeminiLLMAdapter(api_key=api_key)


llm = get_llm()
agent = ChatAgentUC(llm=llm)
pdf_uc = ExplainPdfUC(llm=llm)
pdf_extractor = PdfTextExtractor()

# ---------------------------------------------------------------------------
# Layout principal
# ---------------------------------------------------------------------------
col_chat, col_panel = st.columns([2, 1], gap="large")

with col_chat:
    st.markdown('<div class="gf-panel">', unsafe_allow_html=True)
    st.subheader("Chat")

    for msg in st.session_state.history:
        with st.chat_message(msg.role):
            st.markdown(msg.content)

    user_text = st.chat_input("Digite sua mensagem...")
    st.markdown("</div>", unsafe_allow_html=True)

with col_panel:
    st.markdown('<div class="gf-panel">', unsafe_allow_html=True)
    st.subheader("Próximas evoluções")
    st.write("- RAG com documentos internos")
    st.write("- Agentes satélites por área")
    st.write("- Políticas e governança")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Fluxo PDF
# ---------------------------------------------------------------------------
if run_pdf:
    if not uploaded_pdf:
        st.warning("Envie um PDF antes de continuar.")
    else:
        file_bytes = uploaded_pdf.read()

        with st.spinner("Extraindo texto do PDF..."):
            extracted = pdf_extractor.extract(file_bytes, max_pages=int(max_pages))

        if not extracted.text.strip():
            st.error("Não foi possível extrair texto desse PDF.")
        else:
            method_label = {
                "text": "texto selecionável",
                "ocr": "OCR",
                "vision": "Claude Vision",
            }.get(extracted.method, extracted.method)

            with st.spinner("Gerando explicação..."):
                resp = pdf_uc.run(
                    model=model,
                    history=st.session_state.history,
                    pdf_text=extracted.text,
                    user_goal=pdf_goal,
                )

            st.session_state.history.append(
                ChatMessage(role="user", content=f"[PDF] {uploaded_pdf.name} — {pdf_goal}")
            )
            st.session_state.history.append(
                ChatMessage(role="assistant", content=resp.text)
            )

            st.success(
                f"**{uploaded_pdf.name}** | "
                f"Páginas no arquivo: {extracted.pages} | "
                f"Processadas: {int(max_pages)} | "
                f"Método: {method_label}"
            )
            st.write(resp.text)
            st.caption(f"Modelo: {resp.used_model} · Latência: {resp.latency_ms} ms")

# ---------------------------------------------------------------------------
# Fluxo chat
# ---------------------------------------------------------------------------
if user_text:
    st.session_state.history.append(ChatMessage(role="user", content=user_text))

    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            resp = agent.run(
                model=model,
                history=st.session_state.history[:-1],
                user_text=user_text,
            )
            st.markdown(resp.text)
            st.caption(f"Modelo: {resp.used_model} · Latência: {resp.latency_ms} ms")

    st.session_state.history.append(ChatMessage(role="assistant", content=resp.text))