@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
C:\Users\kl\miniconda3\python.exe -X utf8 "%~dp0main.py" %*
