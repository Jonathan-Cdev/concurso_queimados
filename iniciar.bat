@echo off
REM ============================================================
REM  Iniciar Sistema de Estudos - Concurso Queimados
REM ============================================================
title Sistema de Estudos - Queimados

REM Muda para a pasta onde este .bat esta localizado
cd /d "%~dp0"

REM Ativa o ambiente virtual
call .venv\Scripts\activate.bat

REM Roda o Streamlit (o navegador abre automaticamente)
python -m streamlit run app.py

REM Se der erro, mantem a janela aberta para voce ver
pause