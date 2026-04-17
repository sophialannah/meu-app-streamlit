import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import json
from datetime import datetime, date, time
import warnings
warnings.filterwarnings("ignore")

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Relatório de Atividades GEIMP",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "dados_relatorio.csv"

RESPONSAVEIS = [
    "Em definição", "Abel Silva", "Andrea Almeida", "Christopher Rezende",
    "Daisa haissy", "Elvis Oliveira", "Fernanda Marques", "Gerson Rodrigues",
    "Lucas Mota", "Matheus Alves", "Nilton Coelho", "Rafael Almeida",
    "Rafael Aires", "Rafael Lacerda", "Rosa Augusta", "Rosane Castro",
    "Rosangela Pereira", "Saulo de Castro", "Sophia Lannah",
]

PALAVRAS_CHAVE = [
    "Anteprojeto de Lei", "Base Folha", "Concurso Público", "Ofício Circular",
    "Orientação PGE", "Painel Remuneratório", "Evolução Funcional",
    "Processo Seletivo", "Promoção", "Promoção Ato de bravura", "Promoção CHOA",
    "Reajuste", "Alteração de Estrutura Administrativa", "Relatório de Atividades",
    "Relatório de Frequência", "Processo Interno", "Estudo da Carreira",
]

TIPOS_ATIVIDADE = [
    "Atividade Complementar", "Despacho", "Estudo",
    "Impacto", "Levantamento", "Aperfeiçoamento",
]

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f1923;
    border-right: 1px solid #1e3a4a;
}
section[data-testid="stSidebar"] * { color: #cdd9e5 !important; }
section[data-testid="stSidebar"] .stRadio label { font-size: 15px; padding: 6px 0; }

/* Main bg */
.stApp { background: #f0f4f8; }

/* Page header */
.page-header {
    background: linear-gradient(135deg, #0f1923 0%, #1a3a52 60%, #0d5c8a 100%);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 28px;
    color: white;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute; top: -40px; right: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.page-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 28px; font-weight: 800;
    margin: 0 0 6px 0; letter-spacing: -0.5px;
}
.page-header p { margin: 0; opacity: 0.7; font-size: 14px; }

/* Form card */
.form-card {
    background: white;
    border-radius: 14px;
    padding: 28px 32px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-bottom: 20px;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 13px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.5px;
    color: #0d5c8a; margin-bottom: 18px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e8f4fd;
}

/* KPI cards */
.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    border-left: 4px solid #0d5c8a;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 36px; font-weight: 800;
    color: #0f1923; line-height: 1;
}
.kpi-label { font-size: 13px; color: #6b7c93; margin-top: 6px; }

/* Success banner */
.success-banner {
    background: linear-gradient(135deg, #0a7c42, #14a85a);
    color: white; border-radius: 12px;
    padding: 18px 24px; margin: 16px 0;
    font-weight: 500;
}

/* Chart card */
.chart-card {
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}
.chart-title {
    font-family: 'Syne', sans-serif;
    font-size: 14px; font-weight: 700;
    color: #0f1923; margin-bottom: 16px;
    text-transform: uppercase; letter-spacing: 0.5px;
}

/* Streamlit overrides */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    border-radius: 8px !important;
    border-color: #dde3ea !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button {
    background: linear-gradient(135deg, #0d5c8a, #0a7cc2) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; padding: 12px 32px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 15px !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 14px rgba(13,92,138,0.35) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(13,92,138,0.45) !important;
}
div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Data helpers ─────────────────────────────────────────────────────────────
COLUMNS = [
    "Nº Processo", "Responsável", "Palavra-chave", "Assunto da Atividade",
    "Detalhamento da Atividade", "Tipo de Atividade", "Interessado",
    "Valor do Impacto", "Tipo de Documento", "Data Chegada Processo",
    "Prazo Pactuado", "Data Início", "Hora Início", "Data Término",
    "Hora Término", "Data Conclusão do Processo", "Encaminhamento",
    "Timestamp",
]

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype=str)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df
    return pd.DataFrame(columns=COLUMNS)

def save_record(record: dict):
    df = load_data()
    new_row = pd.DataFrame([record])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)


# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 10px;'>
        <div style='font-family:Syne,sans-serif;font-size:22px;font-weight:800;
                    color:white;letter-spacing:-0.5px;'>📋 SIGAP</div>
        <div style='font-size:12px;opacity:0.5;margin-top:4px;'>Sistema de Gestão de Atividades</div>
    </div>
    <hr style='border-color:#1e3a4a;margin:12px 0 20px;'/>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navegação",
        ["📝  Registrar Atividade", "📊  Dashboard", "📁  Dados Completos"],
        label_visibility="collapsed",
    )

    df_all = load_data()
    total = len(df_all)
    st.markdown(f"""
    <div style='margin-top:30px;padding:14px 16px;background:#1e3a4a;border-radius:10px;'>
        <div style='font-size:11px;opacity:0.5;text-transform:uppercase;letter-spacing:1px;'>Total de registros</div>
        <div style='font-family:Syne,sans-serif;font-size:28px;font-weight:800;
                    color:#4fc3f7;margin-top:4px;'>{total}</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — FORM
# ══════════════════════════════════════════════════════════════════════════════
if page == "📝  Registrar Atividade":
    st.markdown("""
    <div class="page-header">
        <h1>📋 Relatório de Atividades</h1>
        <p>Preencha todos os campos obrigatórios para registrar sua atividade</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("relatorio_form", clear_on_submit=True):

        # ── Bloco 1: Identificação ────────────────────────────────────────
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔖 Identificação do Processo</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            n_processo = st.text_input("1. Nº Processo *", placeholder="Ex: 00001/2024")
        with col2:
            responsavel = st.selectbox("2. Responsável *", RESPONSAVEIS)

        col3, col4 = st.columns(2)
        with col3:
            palavra_chave = st.selectbox("3. Palavra-chave *", PALAVRAS_CHAVE)
        with col4:
            tipo_atividade = st.selectbox("6. Tipo de Atividade *", TIPOS_ATIVIDADE)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Bloco 2: Atividade ────────────────────────────────────────────
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📝 Detalhes da Atividade</div>', unsafe_allow_html=True)

        assunto = st.text_input("4. Assunto da Atividade *", placeholder="Descreva o assunto principal")
        detalhamento = st.text_area("5. Detalhamento da Atividade *",
                                    placeholder="Descreva com detalhes as atividades realizadas...",
                                    height=120)

        col5, col6 = st.columns(2)
        with col5:
            interessado = st.text_input("7. Interessado", placeholder="Nome do interessado")
        with col6:
            valor_impacto = st.text_input("8. Valor do Impacto", placeholder="Ex: R$ 1.500.000,00")

        col7, _ = st.columns(2)
        with col7:
            tipo_documento = st.text_input("9. Tipo de Documento", placeholder="Ex: Ofício, Memorando...")

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Bloco 3: Datas ────────────────────────────────────────────────
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📅 Datas e Prazos</div>', unsafe_allow_html=True)

        col8, col9 = st.columns(2)
        with col8:
            data_chegada = st.date_input("10. Data Chegada do Processo", value=None)
        with col9:
            prazo_pactuado_data = st.date_input("11. Prazo Pactuado — Data", value=None)

        prazo_pactuado_hora = st.selectbox(
            "11. Prazo Pactuado — Hora (HH:00)",
            options=[""] + [f"{h:02d}:00" for h in range(0, 24)],
        )

        col10, col11 = st.columns(2)
        with col10:
            data_inicio = st.date_input("12. Data Início", value=None)
        with col11:
            hora_inicio = st.text_input("13. Hora Início (HH:MM)", placeholder="Ex: 08:30")

        col12, col13 = st.columns(2)
        with col12:
            data_termino = st.date_input("14. Data Término", value=None)
        with col13:
            hora_termino = st.text_input("15. Hora Término (HH:MM)", placeholder="Ex: 17:00")

        col14, _ = st.columns(2)
        with col14:
            data_conclusao = st.date_input("16. Data Conclusão do Processo", value=None)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Bloco 4: Encaminhamento ───────────────────────────────────────
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📤 Encaminhamento</div>', unsafe_allow_html=True)
        encaminhamento = st.text_area("17. Encaminhamento *",
                                       placeholder="Informe o encaminhamento do processo...",
                                       height=100)
        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("✅  Enviar Relatório", use_container_width=True)

    # ── Process submission ────────────────────────────────────────────────
    if submitted:
        errors = []
        if not n_processo.strip():
            errors.append("Nº Processo é obrigatório.")
        if responsavel == "Em definição":
            errors.append("Selecione um Responsável.")
        if not assunto.strip():
            errors.append("Assunto da Atividade é obrigatório.")
        if not detalhamento.strip():
            errors.append("Detalhamento da Atividade é obrigatório.")
        if not encaminhamento.strip():
            errors.append("Encaminhamento é obrigatório.")

        if errors:
            for e in errors:
                st.error(f"⚠️ {e}")
        else:
            fmt_date = lambda d: d.strftime("%d/%m/%Y") if d else ""
            prazo_str = ""
            if prazo_pactuado_data:
                prazo_str = prazo_pactuado_data.strftime("%d/%m/%Y")
                if prazo_pactuado_hora:
                    prazo_str += f" {prazo_pactuado_hora}"

            record = {
                "Nº Processo": n_processo.strip(),
                "Responsável": responsavel,
                "Palavra-chave": palavra_chave,
                "Assunto da Atividade": assunto.strip(),
                "Detalhamento da Atividade": detalhamento.strip(),
                "Tipo de Atividade": tipo_atividade,
                "Interessado": interessado.strip(),
                "Valor do Impacto": valor_impacto.strip(),
                "Tipo de Documento": tipo_documento.strip(),
                "Data Chegada Processo": fmt_date(data_chegada),
                "Prazo Pactuado": prazo_str,
                "Data Início": fmt_date(data_inicio),
                "Hora Início": hora_inicio.strip(),
                "Data Término": fmt_date(data_termino),
                "Hora Término": hora_termino.strip(),
                "Data Conclusão do Processo": fmt_date(data_conclusao),
                "Encaminhamento": encaminhamento.strip(),
                "Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
            save_record(record)
            st.markdown("""
            <div class="success-banner">
                ✅ Relatório enviado com sucesso! Os dados foram salvos e já estão disponíveis no Dashboard.
            </div>
            """, unsafe_allow_html=True)
            st.balloons()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊  Dashboard":
    df = load_data()

    st.markdown("""
    <div class="page-header">
        <h1>📊 Dashboard de Atividades</h1>
        <p>Visão analítica consolidada de todos os registros da equipe</p>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("ℹ️ Nenhum registro encontrado. Use o formulário para adicionar atividades.")
        st.stop()

    # ── Filters ──────────────────────────────────────────────────────────
    with st.expander("🔍 Filtros", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            f_resp = st.multiselect("Responsável", sorted(df["Responsável"].dropna().unique()))
        with fc2:
            f_tipo = st.multiselect("Tipo de Atividade", sorted(df["Tipo de Atividade"].dropna().unique()))
        with fc3:
            f_pkw = st.multiselect("Palavra-chave", sorted(df["Palavra-chave"].dropna().unique()))

    dff = df.copy()
    if f_resp: dff = dff[dff["Responsável"].isin(f_resp)]
    if f_tipo: dff = dff[dff["Tipo de Atividade"].isin(f_tipo)]
    if f_pkw:  dff = dff[dff["Palavra-chave"].isin(f_pkw)]

    # ── KPIs ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-value">{len(dff)}</div>
            <div class="kpi-label">Total de Registros</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        n_resp = dff["Responsável"].nunique()
        st.markdown(f"""<div class="kpi-card" style="border-left-color:#e67e22;">
            <div class="kpi-value">{n_resp}</div>
            <div class="kpi-label">Responsáveis Ativos</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        n_proc = dff["Nº Processo"].nunique()
        st.markdown(f"""<div class="kpi-card" style="border-left-color:#27ae60;">
            <div class="kpi-value">{n_proc}</div>
            <div class="kpi-label">Processos Únicos</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        n_tipos = dff["Tipo de Atividade"].nunique()
        st.markdown(f"""<div class="kpi-card" style="border-left-color:#8e44ad;">
            <div class="kpi-value">{n_tipos}</div>
            <div class="kpi-label">Tipos de Atividade</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    COLORS = ["#0d5c8a", "#1a8fc1", "#e67e22", "#27ae60", "#8e44ad", "#c0392b", "#16a085", "#2c3e50"]

    # ── Row 1: Responsável + Tipo de Atividade ────────────────────────────
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Atividades por Responsável</div>', unsafe_allow_html=True)
        resp_count = dff["Responsável"].value_counts().reset_index()
        resp_count.columns = ["Responsável", "Qtd"]
        fig = px.bar(resp_count, x="Qtd", y="Responsável", orientation="h",
                     color="Qtd", color_continuous_scale=["#b3d9f2", "#0d5c8a"],
                     template="plotly_white")
        fig.update_layout(showlegend=False, coloraxis_showscale=False,
                          margin=dict(l=0,r=0,t=0,b=0), height=320,
                          yaxis=dict(categoryorder="total ascending"))
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r1c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Distribuição por Tipo de Atividade</div>', unsafe_allow_html=True)
        tipo_count = dff["Tipo de Atividade"].value_counts().reset_index()
        tipo_count.columns = ["Tipo", "Qtd"]
        fig2 = px.pie(tipo_count, names="Tipo", values="Qtd",
                      color_discrete_sequence=COLORS, template="plotly_white",
                      hole=0.45)
        fig2.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=320,
                           legend=dict(orientation="v", x=1.01))
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 2: Palavra-chave + Evolução temporal ──────────────────────────
    r2c1, r2c2 = st.columns([1, 1])
    with r2c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Top Palavras-chave</div>', unsafe_allow_html=True)
        pkw_count = dff["Palavra-chave"].value_counts().head(10).reset_index()
        pkw_count.columns = ["Palavra-chave", "Qtd"]
        fig3 = px.bar(pkw_count, x="Qtd", y="Palavra-chave", orientation="h",
                      color_discrete_sequence=["#0d5c8a"], template="plotly_white")
        fig3.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=340,
                           showlegend=False,
                           yaxis=dict(categoryorder="total ascending"))
        fig3.update_traces(marker_line_width=0)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r2c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Registros ao Longo do Tempo</div>', unsafe_allow_html=True)
        dff2 = dff.copy()
        dff2["Data"] = pd.to_datetime(dff2["Timestamp"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
        dff2 = dff2.dropna(subset=["Data"])
        if not dff2.empty:
            dff2["Mês"] = dff2["Data"].dt.to_period("M").astype(str)
            time_count = dff2.groupby("Mês").size().reset_index(name="Qtd")
            fig4 = px.area(time_count, x="Mês", y="Qtd",
                           color_discrete_sequence=["#0d5c8a"],
                           template="plotly_white")
            fig4.update_traces(fill="tozeroy", line_color="#0d5c8a",
                               fillcolor="rgba(13,92,138,0.15)")
            fig4.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=340)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Dados temporais insuficientes.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 3: Heatmap Responsável × Tipo ────────────────────────────────
    st.markdown('<div class="chart-card"><div class="chart-title">Heatmap — Responsável × Tipo de Atividade</div>', unsafe_allow_html=True)
    pivot = dff.pivot_table(index="Responsável", columns="Tipo de Atividade",
                            aggfunc="size", fill_value=0)
    fig5 = px.imshow(pivot, color_continuous_scale=["#e8f4fd", "#0d5c8a"],
                     template="plotly_white", text_auto=True, aspect="auto")
    fig5.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=350,
                       coloraxis_showscale=False)
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 4: Processos por status de conclusão ──────────────────────────
    st.markdown('<div class="chart-card"><div class="chart-title">Processos: Concluídos vs Pendentes</div>', unsafe_allow_html=True)
    dff["Concluído"] = dff["Data Conclusão do Processo"].apply(
        lambda x: "✅ Concluído" if (isinstance(x, str) and x.strip()) else "⏳ Pendente"
    )
    status_count = dff["Concluído"].value_counts().reset_index()
    status_count.columns = ["Status", "Qtd"]
    fig6 = px.bar(status_count, x="Status", y="Qtd",
                  color="Status",
                  color_discrete_map={"✅ Concluído": "#27ae60", "⏳ Pendente": "#e67e22"},
                  template="plotly_white", text_auto=True)
    fig6.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=280, showlegend=False)
    fig6.update_traces(marker_line_width=0)
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — DATA TABLE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📁  Dados Completos":
    df = load_data()

    st.markdown("""
    <div class="page-header">
        <h1>📁 Base de Dados Completa</h1>
        <p>Visualize, filtre e exporte todos os registros</p>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("ℹ️ Nenhum registro encontrado.")
        st.stop()

    # Search
    search = st.text_input("🔍 Buscar em todos os campos", placeholder="Digite para filtrar...")
    if search:
        mask = df.apply(lambda col: col.astype(str).str.contains(search, case=False, na=False))
        df = df[mask.any(axis=1)]

    st.markdown(f"**{len(df)} registro(s) encontrado(s)**")
    st.dataframe(df, use_container_width=True, height=500)

    # Export
    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇️  Exportar CSV",
        data=csv_bytes,
        file_name=f"relatorio_atividades_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )