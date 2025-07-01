#!/usr/bin/env python3

import os
import subprocess
import sys
import venv
from pathlib import Path

def run_command(command, shell=True):
    try:
        subprocess.run(command, shell=shell, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🚀 Iniciando Lux...")
    
    # Verificar se o ambiente virtual existe
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 Criando ambiente virtual...")
        venv.create("venv", with_pip=True)
    
    # Ativar o ambiente virtual
    print("🔧 Ativando ambiente virtual...")
    if sys.platform == "win32":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "source venv/bin/activate"
    
    # Verificar autenticação do Google Cloud
    print("🔐 Verificando autenticação do Google Cloud...")
    if not run_command("gcloud auth application-default print-access-token", shell=True):
        print("🔑 Realizando autenticação do Google Cloud...")
        run_command("gcloud auth application-default login", shell=True)
    else:
        print("✅ Autenticação do Google Cloud já está configurada.")
    
    # Instalar dependências se necessário
    if not Path("venv/lib/python3.*/site-packages/streamlit").exists():
        print("📥 Instalando dependências...")
        run_command(f"{activate_script} && pip install -r requirements.txt", shell=True)
    
    # Iniciar o Streamlit
    print("🌐 Iniciando o Streamlit...")
    run_command(f"{activate_script} && streamlit run app.py", shell=True)

if __name__ == "__main__":
    main() 