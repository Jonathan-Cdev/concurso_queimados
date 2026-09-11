"""
=============================================================================
CONFIGURAÇÕES CENTRAIS DO SISTEMA DE ESTUDOS
=============================================================================
Baseado no ANEXO VII do Edital 01/2026 de Queimados/RJ
Cargo: Agente Administrativo (Nível Médio Completo)
=============================================================================
"""

# -----------------------------------------------------------------------------
# ESTRUTURA DE DISCIPLINAS E TÓPICOS (conforme ANEXO VII do Edital)
# -----------------------------------------------------------------------------
DISCIPLINAS: dict[str, list[str]] = {
    # -------------------------------------------------------------------------
    # LÍNGUA PORTUGUESA (11 tópicos do edital, com subdivisões didáticas)
    # -------------------------------------------------------------------------
    "Língua Portuguesa": [
        "Leitura, Compreensão e Interpretação de Texto",
        "Vocabulário (denotação, conotação, sinonímia, antonímia, homonímia, paronímia, polissemia)",
        "Ortografia e Acentuação Gráfica",
        "Pontuação (todos os sinais)",
        "Pronomes (classificação, emprego e colocação)",
        "Verbos (modos, tempos, flexões e vozes)",
        "Preposições (relações semânticas)",
        "Conjunções (classificação e relações)",
        "Substantivos (classificação e flexões)",
        "Adjetivos (classificação e flexões)",
        "Termos da Oração",
        "Coordenação e Subordinação",
        "Classificação de Períodos e Orações",
        "Concordância Nominal e Verbal",
        "Regência Nominal e Verbal",
        "Crase",
        "Simulado / Revisão Geral",
    ],

    # -------------------------------------------------------------------------
    # LEGISLAÇÃO MUNICIPAL (2 tópicos do edital, com subdivisões da Lei 1.060)
    # -------------------------------------------------------------------------
    "Legislação Municipal": [
        "Lei Orgânica do Município de Queimados/RJ",
        "Lei 1.060/2011 - Regime Jurídico dos Servidores",
        "Lei 1.060/2011 - Provimento e Vacância",
        "Lei 1.060/2011 - Direitos e Vantagens",
        "Lei 1.060/2011 - Deveres e Proibições",
        "Lei 1.060/2011 - Responsabilidades",
        "Lei 1.060/2011 - Processo Disciplinar",
        "Simulado / Revisão Geral",
    ],

    # -------------------------------------------------------------------------
    # CONHECIMENTOS ESPECÍFICOS (11 tópicos do edital, com subdivisões)
    # -------------------------------------------------------------------------
    "Conhecimentos Específicos": [
        "Administração Pública - Conceitos e Princípios",
        "Administração Pública - Organização (Direta e Indireta)",
        "Atos Administrativos",
        "Poderes Administrativos",
        "Administração Geral - Funções Administrativas",
        "Organização e Métodos (O&M)",
        "Fluxogramas, Organogramas e Rotinas Administrativas",
        "Gestão por Processos",
        "Recrutamento e Seleção",
        "Treinamento e Desenvolvimento",
        "Avaliação de Desempenho",
        "Rotinas de Pessoal (Frequência, Férias, Registros)",
        "Gestão de Materiais (Compras, Recebimento, Armazenamento, Distribuição)",
        "Controle de Estoque",
        "Inventário de Bens",
        "Controle Patrimonial",
        "Orçamento Público",
        "Receita e Despesa Pública",
        "Execução Orçamentária e Financeira",
        "Controle de Gastos Públicos",
        "Arquivologia - Conceitos",
        "Classificação, Organização e Conservação de Documentos",
        "Protocolo (Recebimento, Registro, Tramitação, Expedição)",
        "Arquivo Físico e Digital",
        "Redação Oficial (Ofício, Memorando, Relatório)",
        "Manual de Redação da Presidência da República",
        "Legislação e Normas Administrativas",
        "Planejamento e Controle Administrativo",
        "Análise de Dados e Relatórios",
        "Indicadores de Desempenho",
        "Ética e Conduta no Serviço Público",
        "Informática Básica",
        "Simulado / Revisão Geral",
    ],
}

# -----------------------------------------------------------------------------
# PESOS DA PROVA (para priorização de estudo)
# Total = 100 pontos
# LP: 10 questões x 2 pts | LM: 5 questões x 1 pt | CE: 15 questões x 5 pts
# -----------------------------------------------------------------------------
PESOS_PROVA: dict[str, int] = {
    "Língua Portuguesa": 20,
    "Legislação Municipal": 5,
    "Conhecimentos Específicos": 75,
}

# -----------------------------------------------------------------------------
# METAS PADRÃO (editáveis pela interface)
# -----------------------------------------------------------------------------
META_HORAS_SEMANAL_PADRAO = 15.0
META_QUESTOES_SEMANAL_PADRAO = 100

# -----------------------------------------------------------------------------
# LISTA DE DISCIPLINAS (atalho)
# -----------------------------------------------------------------------------
LISTA_DISCIPLINAS = list(DISCIPLINAS.keys())

# -----------------------------------------------------------------------------
# CORES DOS GRÁFICOS
# -----------------------------------------------------------------------------
CORES_DISCIPLINAS = {
    "Língua Portuguesa": "#2E86AB",
    "Legislação Municipal": "#A23B72",
    "Conhecimentos Específicos": "#F18F01",
}

# -----------------------------------------------------------------------------
# METADADOS DO CONCURSO
# -----------------------------------------------------------------------------
CONCURSO_INFO = {
    "nome": "Concurso Público 01/2026 - Prefeitura Municipal de Queimados/RJ",
    "cargo": "Agente Administrativo",
    "banca": "Instituto de Avaliação Nacional (IAN)",
    "vagas_imediatas": 54,
    "vagas_pcd": 3,
    "vagas_cotas": 11,
    "salario": "R$ 3.422,60",
    "carga_horaria": "40 horas semanais",
    "regime": "Estatutário",
    "data_prova": "22/11/2026 (domingo)",
    "horario_prova": "14h às 17h (Horário de Brasília)",
    "validade": "24 meses, prorrogável por mais 24",
    "site_banca": "www.ian.org.br",
}