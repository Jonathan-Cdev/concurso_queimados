"""
=============================================================================
INTERFACE STREAMLIT - SISTEMA DE ESTUDOS
=============================================================================
Este arquivo contém APENAS a camada de apresentação.
Toda a persistência é delegada a database.py.

Para rodar:
    streamlit run app.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from io import BytesIO

import database as db
from config import (
    DISCIPLINAS, LISTA_DISCIPLINAS, CORES_DISCIPLINAS,
    PESOS_PROVA, META_HORAS_SEMANAL_PADRAO, META_QUESTOES_SEMANAL_PADRAO,
    CONCURSO_INFO,
)

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Estudos Queimados 2026",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializa banco de dados (idempotente)
db.init_database()

# -----------------------------------------------------------------------------
# CSS CUSTOMIZADO
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1F4E78;
        margin-bottom: 0;
    }
    .sub-header {
        color: #666;
        font-size: 1rem;
        margin-top: 0;
    }
    .kpi-card {
        background: linear-gradient(135deg, #D9E1F2 0%, #F2F6FC 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #1F4E78;
        text-align: center;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1F4E78;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<p class="main-header">🎓 Sistema de Estudos</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="sub-header">{CONCURSO_INFO["nome"]} • <b>{CONCURSO_INFO["cargo"]}</b></p>',
        unsafe_allow_html=True
    )
with col_h2:
    st.metric("Prova", CONCURSO_INFO["data_prova"].split(" ")[0])

# -----------------------------------------------------------------------------
# CRIA AS ABAS
# -----------------------------------------------------------------------------
tab_reg, tab_dash, tab_cons, tab_edit, tab_metas, tab_sobre = st.tabs([
    "📝 Registrar",
    "📊 Dashboard",
    "🔍 Consultar",
    "✏️ Editar/Excluir",
    "🎯 Metas",
    "ℹ️ Sobre",
])


# =============================================================================
# ABA 1: REGISTRAR
# =============================================================================
with tab_reg:
    st.subheader("📝 Nova sessão de estudo")

    with st.form("form_registro", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            data_input = st.date_input(
                "Data do estudo",
                value=date.today(),
                max_value=date.today(),
                help="Você pode registrar retroativamente",
            )

        with col2:
            disciplina_input = st.selectbox(
                "Disciplina",
                options=LISTA_DISCIPLINAS,
                index=0,
            )

        with col3:
            # Dropdown dependente: tópicos da disciplina escolhida
            topico_input = st.selectbox(
                "Tópico/Assunto",
                options=DISCIPLINAS[disciplina_input],
                index=0,
            )

        col4, col5, col6 = st.columns(3)

        with col4:
            horas_input = st.number_input(
                "Horas estudadas",
                min_value=0.0, max_value=24.0, step=0.25, value=1.0, format="%.2f",
                help="Use 0.5 = 30min, 0.25 = 15min, 1.5 = 1h30",
            )

        with col5:
            questoes_input = st.number_input(
                "Questões feitas",
                min_value=0, max_value=1000, step=1, value=0,
            )

        with col6:
            acertos_input = st.number_input(
                "Acertos",
                min_value=0, max_value=1000, step=1, value=0,
            )

        observacoes_input = st.text_area(
            "Observações (opcional)",
            placeholder="Ex: revisar fórmula de Bhaskara, dúvida no tópico X...",
            height=80,
        )

        # Validação em tempo real
        erros_calc = max(questoes_input - acertos_input, 0)
        if questoes_input > 0:
            perc = acertos_input / questoes_input * 100
            st.caption(f"📊 Erros: **{erros_calc}** • Aproveitamento: **{perc:.1f}%**")

        # Validação: acertos não pode passar de questões
        submit = st.form_submit_button("💾 Salvar sessão", type="primary", width="stretch")

        if submit:
            if acertos_input > questoes_input:
                st.error("❌ Acertos não pode ser maior que o total de questões.")
            elif horas_input <= 0 and questoes_input <= 0:
                st.warning("⚠️ Preencha pelo menos horas OU questões.")
            else:
                novo_id = db.inserir_sessao(
                    data=data_input.strftime("%Y-%m-%d"),
                    disciplina=disciplina_input,
                    topico=topico_input,
                    horas=horas_input,
                    questoes=questoes_input,
                    acertos=acertos_input,
                    erros=erros_calc,
                    observacoes=observacoes_input,
                )
                if novo_id:
                    st.success(f"✅ Sessão salva com sucesso! (ID: {novo_id})")
                    st.balloons()
                else:
                    st.error("❌ Erro ao salvar. Verifique o console para detalhes.")

    # Mostra as últimas 5 sessões registradas
    st.divider()
    st.subheader("🕐 Últimas 5 sessões registradas")
    ultimas = db.listar_sessoes({"limite": 5})
    if ultimas:
        df_ult = pd.DataFrame(ultimas)[
            ["id", "data", "disciplina", "topico", "horas", "questoes", "acertos", "erros"]
        ]
        st.dataframe(df_ult, width="stretch", hide_index=True)
    else:
        st.info("Nenhuma sessão registrada ainda. Comece pela primeira!")


# =============================================================================
# ABA 2: DASHBOARD
# =============================================================================
with tab_dash:
    st.subheader("📊 Dashboard de desempenho")

    # KPIs principais
    stats = db.obter_estatisticas_gerais()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total de Horas</div>
            <div class="kpi-value">{stats['total_horas']:.1f}h</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Questões Feitas</div>
            <div class="kpi-value">{stats['total_questoes']}</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Aproveitamento</div>
            <div class="kpi-value">{stats['percentual_acerto']*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Dias Estudados</div>
            <div class="kpi-value">{stats['dias_estudados']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Linha 1: barras de horas + pizza de questões
    stats_disc = db.obter_estatisticas_por_disciplina()

    if stats_disc:
        df_disc = pd.DataFrame(stats_disc)

        c1, c2 = st.columns(2)

        with c1:
            fig_horas = px.bar(
                df_disc, x="disciplina", y="horas",
                color="disciplina",
                color_discrete_map=CORES_DISCIPLINAS,
                title="⏱️ Horas por disciplina",
                text_auto=".1f",
            )
            fig_horas.update_layout(showlegend=False, height=380)
            st.plotly_chart(fig_horas, width="stretch")

        with c2:
            fig_pizza = px.pie(
                df_disc, names="disciplina", values="questoes",
                color="disciplina",
                color_discrete_map=CORES_DISCIPLINAS,
                title="🥧 Distribuição de questões",
                hole=0.4,
            )
            fig_pizza.update_layout(height=380)
            st.plotly_chart(fig_pizza, width="stretch")

        # Linha 2: aproveitamento por disciplina
        df_disc["perc"] = df_disc["percentual_acerto"] * 100
        fig_perc = px.bar(
            df_disc, x="disciplina", y="perc",
            color="disciplina",
            color_discrete_map=CORES_DISCIPLINAS,
            title="🎯 Aproveitamento (%) por disciplina",
            text_auto=".1f",
        )
        fig_perc.update_layout(showlegend=False, height=380)
        fig_perc.update_yaxes(range=[0, 100])
        st.plotly_chart(fig_perc, width="stretch")

    st.divider()

    # Evolução diária
    st.subheader("📈 Evolução diária (últimos 60 dias)")
    stats_dia = db.obter_estatisticas_diarias(dias=60)

    if stats_dia:
        df_dia = pd.DataFrame(stats_dia)
        df_dia["data"] = pd.to_datetime(df_dia["data"])

        fig_linha = go.Figure()
        fig_linha.add_trace(go.Scatter(
            x=df_dia["data"], y=df_dia["horas"],
            name="Horas", mode="lines+markers",
            line=dict(color="#1F4E78", width=3),
        ))
        fig_linha.add_trace(go.Bar(
            x=df_dia["data"], y=df_dia["questoes"],
            name="Questões", yaxis="y2",
            marker_color="rgba(241,143,1,0.6)",
        ))
        fig_linha.update_layout(
            height=400,
            yaxis=dict(title="Horas"),
            yaxis2=dict(title="Questões", overlaying="y", side="right"),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_linha, width="stretch")
    else:
        st.info("Sem dados para exibir. Registre suas primeiras sessões!")

    # Heatmap disciplina x semana
    st.subheader("🗓️ Heatmap: disciplina × semana (últimas 12 semanas)")
    stats_sem = db.obter_estatisticas_semanais(semanas=12)
    if stats_sem and len(stats_sem) > 1:
        sessoes = db.listar_sessoes({"limite": 2000})
        df_h = pd.DataFrame(sessoes)
        if not df_h.empty:
            df_h["data"] = pd.to_datetime(df_h["data"])
            df_h["semana"] = df_h["data"].dt.strftime("%Y-%W")
            pivot = df_h.pivot_table(
                index="disciplina", columns="semana",
                values="horas", aggfunc="sum", fill_value=0,
            )
            fig_heat = px.imshow(
                pivot, aspect="auto", color_continuous_scale="Blues",
                labels=dict(x="Semana", y="Disciplina", color="Horas"),
            )
            fig_heat.update_layout(height=300)
            st.plotly_chart(fig_heat, width="stretch")
    else:
        st.info("Dados insuficientes para o heatmap (mínimo 2 semanas).")


# =============================================================================
# ABA 3: CONSULTAR
# =============================================================================
with tab_cons:
    st.subheader("🔍 Consultar histórico")

    # Filtros
    colf1, colf2, colf3, colf4 = st.columns(4)
    with colf1:
        data_ini = st.date_input("De:", value=date.today() - timedelta(days=90), key="f_ini")
    with colf2:
        data_fim = st.date_input("Até:", value=date.today(), key="f_fim")
    with colf3:
        disc_filtro = st.selectbox(
            "Disciplina:", ["Todas"] + LISTA_DISCIPLINAS, key="f_disc"
        )
    with colf4:
        lim = st.number_input("Máx. registros:", 10, 5000, 500, step=50, key="f_lim")

    filtros = {
        "data_inicio": data_ini.strftime("%Y-%m-%d"),
        "data_fim": data_fim.strftime("%Y-%m-%d"),
        "limite": int(lim),
    }
    if disc_filtro != "Todas":
        filtros["disciplina"] = disc_filtro

    sessoes = db.listar_sessoes(filtros)

    if sessoes:
        df = pd.DataFrame(sessoes)
        df["perc"] = df.apply(
            lambda r: (r["acertos"] / (r["acertos"] + r["erros"])) if (r["acertos"] + r["erros"]) > 0 else 0,
            axis=1,
        )
        df_view = df[[
            "id", "data", "disciplina", "topico",
            "horas", "questoes", "acertos", "erros", "perc", "observacoes"
        ]].rename(columns={
            "id": "ID", "data": "Data", "disciplina": "Disciplina",
            "topico": "Tópico", "horas": "Horas", "questoes": "Questões",
            "acertos": "Acertos", "erros": "Erros", "perc": "% Acerto",
            "observacoes": "Observações",
        })
        df_view["% Acerto"] = (df_view["% Acerto"] * 100).round(1).astype(str) + "%"

        st.caption(f"📋 {len(df_view)} registros encontrados")
        st.dataframe(df_view, width="stretch", hide_index=True, height=450)

        # Exportar CSV
        csv = df_view.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Baixar CSV",
            data=csv,
            file_name=f"estudos_{date.today().isoformat()}.csv",
            mime="text/csv",
        )

        # Exportar Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_view.to_excel(writer, index=False, sheet_name="Estudos")
        st.download_button(
            "⬇️ Baixar Excel",
            data=buffer.getvalue(),
            file_name=f"estudos_{date.today().isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.info("Nenhum registro encontrado com esses filtros.")


# =============================================================================
# ABA 4: EDITAR / EXCLUIR
# =============================================================================
with tab_edit:
    st.subheader("✏️ Editar ou excluir uma sessão")

    sessoes_todas = db.listar_sessoes({"limite": 500})

    if not sessoes_todas:
        st.info("Nenhuma sessão para editar.")
    else:
        opcoes = {
            f"#{s['id']} - {s['data']} - {s['disciplina'][:25]} - {s['topico'][:30]}": s["id"]
            for s in sessoes_todas
        }
        escolha_label = st.selectbox("Selecione a sessão:", list(opcoes.keys()))
        id_sel = opcoes[escolha_label]
        s = db.obter_sessao(id_sel)

        if s:
            with st.form("form_edicao"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    nova_data = st.date_input(
                        "Data",
                        value=datetime.strptime(str(s["data"]), "%Y-%m-%d").date(),
                    )
                with c2:
                    idx_disc = LISTA_DISCIPLINAS.index(s["disciplina"]) if s["disciplina"] in LISTA_DISCIPLINAS else 0
                    nova_disc = st.selectbox("Disciplina", LISTA_DISCIPLINAS, index=idx_disc)
                with c3:
                    topicos_disp = DISCIPLINAS[nova_disc]
                    idx_top = topicos_disp.index(s["topico"]) if s["topico"] in topicos_disp else 0
                    novo_top = st.selectbox("Tópico", topicos_disp, index=idx_top)

                c4, c5, c6 = st.columns(3)
                with c4:
                    novas_horas = st.number_input("Horas", value=float(s["horas"]), step=0.25, min_value=0.0)
                with c5:
                    novas_questoes = st.number_input("Questões", value=int(s["questoes"]), step=1, min_value=0)
                with c6:
                    novos_acertos = st.number_input("Acertos", value=int(s["acertos"]), step=1, min_value=0)

                novas_obs = st.text_area("Observações", value=s.get("observacoes") or "", height=80)

                col_a, col_b = st.columns(2)
                with col_a:
                    salvar = st.form_submit_button("💾 Salvar alterações", type="primary", width="stretch")
                with col_b:
                    excluir = st.form_submit_button("🗑️ Excluir sessão", width="stretch")

                if salvar:
                    if novos_acertos > novas_questoes:
                        st.error("❌ Acertos não pode ser maior que questões.")
                    else:
                        ok = db.atualizar_sessao(id_sel, {
                            "data": nova_data.strftime("%Y-%m-%d"),
                            "disciplina": nova_disc,
                            "topico": novo_top,
                            "horas": novas_horas,
                            "questoes": novas_questoes,
                            "acertos": novos_acertos,
                            "erros": max(novas_questoes - novos_acertos, 0),
                            "observacoes": novas_obs,
                        })
                        if ok:
                            st.success("✅ Sessão atualizada!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao atualizar.")

                if excluir:
                    if db.deletar_sessao(id_sel):
                        st.success("🗑️ Sessão excluída!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir.")


# =============================================================================
# ABA 5: METAS
# =============================================================================
with tab_metas:
    st.subheader("🎯 Metas de estudo")

    # Metas configuráveis
    c1, c2 = st.columns(2)
    with c1:
        meta_horas = st.number_input(
            "Meta semanal de horas",
            min_value=1.0, max_value=100.0,
            value=float(META_HORAS_SEMANAL_PADRAO), step=1.0,
        )
    with c2:
        meta_questoes = st.number_input(
            "Meta semanal de questões",
            min_value=10, max_value=2000,
            value=META_QUESTOES_SEMANAL_PADRAO, step=10,
        )

    # Calcula progresso da semana atual (segunda a domingo)
    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())   # segunda
    fim_semana = inicio_semana + timedelta(days=6)

    stats_sem_atual = db.listar_sessoes({
        "data_inicio": inicio_semana.strftime("%Y-%m-%d"),
        "data_fim": fim_semana.strftime("%Y-%m-%d"),
    })

    df_sem = pd.DataFrame(stats_sem_atual) if stats_sem_atual else pd.DataFrame()
    horas_sem = df_sem["horas"].sum() if not df_sem.empty else 0
    q_sem = df_sem["questoes"].sum() if not df_sem.empty else 0

    prog_horas = min(horas_sem / meta_horas, 1.0) if meta_horas else 0
    prog_q = min(q_sem / meta_questoes, 1.0) if meta_questoes else 0

    st.markdown(f"### Semana atual: {inicio_semana.strftime('%d/%m')} a {fim_semana.strftime('%d/%m')}")

    p1, p2 = st.columns(2)
    with p1:
        st.metric("⏱️ Horas", f"{horas_sem:.1f}h / {meta_horas:.0f}h")
        st.progress(prog_horas)
    with p2:
        st.metric("📝 Questões", f"{q_sem} / {meta_questoes}")
        st.progress(prog_q)

    if prog_horas >= 1 and prog_q >= 1:
        st.success("🎉 Parabéns! Você bateu TODAS as metas da semana!")
    elif prog_horas >= 1 or prog_q >= 1:
        st.info("💪 Uma meta batida! Continue firme na outra!")

    st.divider()

    # Histórico semanal
    st.subheader("📅 Histórico das últimas 12 semanas")
    stats_hist = db.obter_estatisticas_semanais(semanas=12)
    if stats_hist:
        df_hist = pd.DataFrame(stats_hist)
        df_hist["perc"] = (df_hist["percentual_acerto"] * 100).round(1)
        df_view = df_hist[[
            "data_inicio", "data_fim", "horas", "questoes", "acertos", "erros", "perc"
        ]].rename(columns={
            "data_inicio": "Início", "data_fim": "Fim",
            "horas": "Horas", "questoes": "Questões",
            "acertos": "Acertos", "erros": "Erros", "perc": "% Acerto",
        })
        st.dataframe(df_view, width="stretch", hide_index=True)


# =============================================================================
# ABA 6: SOBRE
# =============================================================================
with tab_sobre:
    st.subheader("ℹ️ Sobre este sistema")

    st.markdown(f"""
    ### 🎓 {CONCURSO_INFO['nome']}
    **Cargo:** {CONCURSO_INFO['cargo']}  
    **Banca:** {CONCURSO_INFO['banca']}  
    **Regime:** {CONCURSO_INFO['regime']}  
    **Salário:** {CONCURSO_INFO['salario']}  
    **Carga horária:** {CONCURSO_INFO['carga_horaria']}  
    **Vagas imediatas:** {CONCURSO_INFO['vagas_imediatas']} + {CONCURSO_INFO['vagas_pcd']} PcD + {CONCURSO_INFO['vagas_cotas']} cotas  
    **Data da prova:** {CONCURSO_INFO['data_prova']} ({CONCURSO_INFO['horario_prova']})  
    **Validade:** {CONCURSO_INFO['validade']}  

    ### 📐 Estrutura da prova
    - **Língua Portuguesa:** 10 questões × 2,0 pts = 20 pts
    - **Legislação Municipal:** 5 questões × 1,0 pt = 5 pts
    - **Conhecimentos Específicos:** 15 questões × 5,0 pts = 75 pts
    - **Total:** 100 pontos | **Mínimo para aprovação:** 50 pts (sem zerar disciplina)

    ### 🎯 Estratégia sugerida
    Como **Conhecimentos Específicos** representa **75% da nota**, o ideal é:
    - 60% do tempo de estudo → Conhecimentos Específicos
    - 25% → Língua Portuguesa
    - 15% → Legislação Municipal

    ### 🛠️ Stack técnica
    - Python 3.9+ / PostgreSQL (Supabase) / Streamlit / Pandas / Plotly

    ### 📂 Estrutura
    - `config.py` → constantes
    - `database.py` → persistência (PostgreSQL)
    - `app.py` → interface (Streamlit)
    """)

    st.divider()
    st.caption("Feito com 💙 para a sua aprovação. Bons estudos!")
