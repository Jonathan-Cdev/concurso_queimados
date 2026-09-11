"""
=============================================================================
CONFIGURAÇÕES CENTRAIS DO SISTEMA DE ESTUDOS
=============================================================================
Este módulo contém apenas constantes. Não importa nada além do Python padrão.
Toda a lógica de negócio fica em database.py, e a UI fica em app.py.
=============================================================================
"""

# -----------------------------------------------------------------------------
# ESTRUTURA DE DISCIPLINAS E TÓPICOS
# Baseado no Anexo VII do Edital 01/2026 de Queimados/RJ
# -----------------------------------------------------------------------------
DISCIPLINAS: dict[str, list[str]] = {
    "Língua Portuguesa": [
        "Interpretação de Texto",
        "Vocabulário (sinonímia, antonímia, polissemia)",
        "Ortografia e Acentuação",
        "Pontuação",
        "Pronomes",
        "Verbos",
        "Preposições e Conjunções",
        "Substantivos e Adjetivos",
        "Termos da Oração",
        "Coordenação e Subordinação",
        "Concordância Nominal e Verbal",
        "Regência Nominal e Verbal",
        "Crase",
        "Simulado/Revisão Geral",
    ],
    "Legislação Municipal": [
        "Lei Orgânica do Município de Queimados",
        "Lei 1.060/2011 - Regime Jurídico",
        "Lei 1.060/2011 - Provimento e Vacância",
        "Lei 1.060/2011 - Direitos e Vantagens",
        "Lei 1.060/2011 - Deveres e Proibições",
        "Lei 1.060/2011 - Responsabilidades",
        "Lei 1.060/2011 - Processo Disciplinar",
        "Simulado/Revisão Geral",
    ],
    "Conhecimentos Específicos": [
        "Administração Pública - Princípios",
        "Administração Pública - Organização",
        "Atos Administrativos",
        "Poderes Administrativos",
        "Administração Geral - Funções",
        "O&M e Fluxogramas",
        "Gestão por Processos",
        "Administração de RH",
        "Rotinas de Pessoal",
        "Administração de Materiais",
        "Controle de Estoque",
        "Patrimônio e Inventário",
        "Orçamento Público",
        "Execução Orçamentária",
        "Arquivologia",
        "Protocolo e Gestão Documental",
        "Redação Oficial",
        "Legislação Administrativa",
        "Planejamento e Controle",
        "Indicadores de Desempenho",
        "Ética no Serviço Público",
        "Informática Básica",
        "Simulado/Revisão Geral",
    ],
}

# -----------------------------------------------------------------------------
# PESOS DA PROVA (para priorização de estudo)
# Total = 100 pontos (10 questões LP x 2 + 5 questões LM x 1 + 15 questões CE x 5)
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
# LISTA DE DISCIPLINAS (atalho útil)
# -----------------------------------------------------------------------------
LISTA_DISCIPLINAS = list(DISCIPLINAS.keys())

# -----------------------------------------------------------------------------
# CORES DOS GRÁFICOS (paleta fixa por disciplina)
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