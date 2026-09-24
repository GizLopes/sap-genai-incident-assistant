"""Streamlit interface for the SAP GenAI Incident Assistant."""

from __future__ import annotations

import html

import streamlit as st

from app.assistant import SAPIncidentAssistant
from app.config import settings


st.set_page_config(
    page_title=settings.app_name,
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1280px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            min-width: 280px;
            max-width: 280px;
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }

        .app-header {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 4px;
        }

        .app-icon {
            width: 46px;
            height: 46px;
            border-radius: 12px;
            background: #FF9900;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            flex-shrink: 0;
        }

        .app-title {
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.15;
            margin: 0;
        }

        .app-subtitle {
            margin: 5px 0 26px 60px;
            font-size: 0.92rem;
            color: #6B7280;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 650;
            margin-top: 26px;
            margin-bottom: 12px;
        }

        .analysis-card {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 16px 18px;
            min-height: 92px;
            background: #FFFFFF;
        }

        .card-label {
            color: #6B7280;
            font-size: 0.76rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 8px;
        }

        .card-value {
            color: #111827;
            font-size: 1.02rem;
            font-weight: 700;
            line-height: 1.3;
            overflow-wrap: anywhere;
        }

        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            line-height: 1.2;
        }

        .badge-success {
            background: #ECFDF3;
            color: #027A48;
        }

        .badge-warning {
            background: #FFF7E6;
            color: #B54708;
        }

        .badge-danger {
            background: #FEF3F2;
            color: #B42318;
        }

        .badge-neutral {
            background: #F2F4F7;
            color: #344054;
        }

        .summary-box {
            margin-top: 18px;
            padding: 15px 17px;
            border-left: 4px solid #FF9900;
            border-radius: 6px;
            background: #F8FAFC;
            font-size: 0.94rem;
            line-height: 1.55;
        }

        .content-item {
            padding: 10px 14px;
            margin-bottom: 8px;
            border: 1px solid #EAECF0;
            border-radius: 8px;
            background: #FFFFFF;
            font-size: 0.92rem;
            line-height: 1.45;
        }

        .source-card {
            padding: 12px 14px;
            margin-bottom: 8px;
            border: 1px solid #EAECF0;
            border-radius: 8px;
            background: #F9FAFB;
        }

        .source-title {
            font-size: 0.9rem;
            font-weight: 650;
        }

        .source-meta {
            color: #667085;
            font-size: 0.78rem;
            margin-top: 4px;
        }

        .sidebar-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 20px;
        }

        .sidebar-label {
            color: #667085;
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 2px;
        }

        .sidebar-value {
            font-size: 0.9rem;
            font-weight: 650;
            margin-bottom: 16px;
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 10px;
        }

        div[data-testid="stButton"] button {
            border-radius: 8px;
            font-weight: 650;
        }

        h1, h2, h3 {
            letter-spacing: -0.02em;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


assistant = SAPIncidentAssistant()


def escape(value: object) -> str:
    return html.escape(str(value))


def status_badge(status: str) -> str:
    status_upper = status.upper()

    if status_upper == "GROUNDED_RECOMMENDATION":
        css_class = "badge-success"
    elif status_upper in {
        "HUMAN_VALIDATION_REQUIRED",
        "REQUEST_MORE_CONTEXT_OR_ESCALATE",
    }:
        css_class = "badge-warning"
    elif status_upper in {"OUT_OF_SCOPE", "INSUFFICIENT_EVIDENCE"}:
        css_class = "badge-danger"
    else:
        css_class = "badge-neutral"

    status_labels = {
        "GROUNDED_RECOMMENDATION": "RECOMENDAÇÃO FUNDAMENTADA",
        "HUMAN_VALIDATION_REQUIRED": "VALIDAÇÃO HUMANA NECESSÁRIA",
        "REQUEST_MORE_CONTEXT_OR_ESCALATE": "SOLICITAR CONTEXTO OU ESCALAR",
        "OUT_OF_SCOPE": "FORA DO ESCOPO",
        "INSUFFICIENT_EVIDENCE": "EVIDÊNCIA INSUFICIENTE",
        "NEEDS_CLARIFICATION": "NECESSITA ESCLARECIMENTO",
    }

    display_status = status_labels.get(
        status_upper,
        status.replace("_", " "),
    )

    return (
        f'<span class="badge {css_class}">'
        f'{escape(display_status)}'
        "</span>"
    )


def confidence_badge(confidence: str) -> str:
    confidence_upper = confidence.upper()

    css_class = {
        "HIGH": "badge-success",
        "MEDIUM": "badge-warning",
        "LOW": "badge-danger",
    }.get(confidence_upper, "badge-neutral")

    confidence_labels = {
        "HIGH": "ALTA",
        "MEDIUM": "MÉDIA",
        "LOW": "BAIXA",
    }

    return (
        f'<span class="badge {css_class}">'
        f'{escape(confidence_labels.get(confidence_upper, confidence_upper))}'
        "</span>"
    )


def render_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="analysis-card">
            <div class="card-label">{escape(label)}</div>
            <div class="card-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div class="sidebar-title">Contexto da POC</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="sidebar-label">Módulo SAP</div>
        <div class="sidebar-value">{escape(settings.sap_module)}</div>

        <div class="sidebar-label">Região AWS</div>
        <div class="sidebar-value">{escape(settings.aws_region)}</div>

        <div class="sidebar-label">Ambiente</div>
        <div class="sidebar-value">{escape(settings.environment)}</div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.info(
        "A IA fornece apenas recomendações de diagnóstico. Alterações no SAP, "
        "lançamentos, liberações, mudanças de configuração e outras ações críticas "
        "exigem execução humana autorizada."
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="app-header">
        <div class="app-icon">🔎</div>
        <div class="app-title">{escape(settings.app_name)}</div>
    </div>
    <div class="app-subtitle">
        Análise de chamados SAP com recomendações fundamentadas em evidências
        e controles Human-in-the-Loop.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Ticket input
# ---------------------------------------------------------------------------

ticket = st.text_area(
    "Chamado de suporte SAP",
    height=150,
    placeholder=(
        "Exemplo: O pedido de compra 4500012345 está bloqueado e o comprador "
        "não consegue continuar. Verifique por que o pedido não pode prosseguir "
        "e se existe uma liberação pendente."
    ),
)

analyze = st.button(
    "Analisar chamado",
    type="primary",
    use_container_width=True,
)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

if analyze:
    with st.spinner("Analisando chamado..."):
        result = assistant.analyze_ticket(ticket)

    st.markdown(
        '<div class="section-title">Análise</div>',
        unsafe_allow_html=True,
    )

    status_col, confidence_col, module_col, process_col = st.columns(
        [1.5, 1, 0.8, 1.4]
    )

    with status_col:
        render_card("Status", status_badge(result.status))

    with confidence_col:
        render_card(
            "Confiança",
            confidence_badge(result.confidence),
        )

    with module_col:
        render_card(
            "Módulo SAP",
            f'<span class="badge badge-neutral">{escape(result.sap_module)}</span>',
        )

    with process_col:
        render_card(
            "Processo",
            f'<span class="badge badge-neutral">'
            f'{escape(result.process or "Não identificado")}'
            "</span>",
        )

    st.markdown(
        f"""
        <div class="summary-box">
            {escape(result.summary)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result.missing_information:
        st.markdown(
            '<div class="section-title">Informações adicionais necessárias</div>',
            unsafe_allow_html=True,
        )

        for item in result.missing_information:
            st.markdown(
                f'<div class="content-item">• {escape(item)}</div>',
                unsafe_allow_html=True,
            )

    if result.possible_causes:
        st.markdown(
            '<div class="section-title">Possíveis causas</div>',
            unsafe_allow_html=True,
        )

        for cause in result.possible_causes:
            st.markdown(
                f'<div class="content-item">• {escape(cause)}</div>',
                unsafe_allow_html=True,
            )

    if result.recommended_checks:
        st.markdown(
            '<div class="section-title">Verificações recomendadas</div>',
            unsafe_allow_html=True,
        )

        for check in result.recommended_checks:
            st.markdown(
                f'<div class="content-item">• {escape(check)}</div>',
                unsafe_allow_html=True,
            )

    if result.sources:
        st.markdown(
            '<div class="section-title">Fontes utilizadas</div>',
            unsafe_allow_html=True,
        )

        for source in result.sources:
            document_id = source.get("document_id", "N/A")
            title = source.get("title", "Fonte da base de conhecimento")
            score = source.get("score", 0.0)

            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-title">
                        {escape(document_id)} · {escape(title)}
                    </div>
                    <div class="source-meta">
                        Score de recuperação: {float(score):.2f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption(
            "Nenhuma fonte fundamentada foi retornada para esta análise."
        )

    if result.human_validation_required:
        st.warning(
            "Validação humana necessária. "
            + (result.human_validation_reason or "")
        )

    with st.expander("Resposta técnica"):
        st.json(result.to_dict())