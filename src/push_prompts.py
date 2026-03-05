"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt.

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ['description', 'system_prompt', 'version']
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = prompt_data.get('system_prompt', '').strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    if 'TODO' in str(prompt_data):
        errors.append("Prompt ainda contém TODOs")

    techniques = prompt_data.get('techniques_applied', [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    print(f"\n📤 Fazendo push do prompt para LangSmith Hub: {prompt_name}")

    try:
        # Validar estrutura
        is_valid, errors = validate_prompt(prompt_data)
        if not is_valid:
            print("   ❌ Validação falhou:")
            for error in errors:
                print(f"      - {error}")
            return False

        print("   ✓ Prompt validado com sucesso")

        # Extrair system e user prompts
        system_prompt = prompt_data.get('system_prompt', '')
        user_prompt = prompt_data.get('user_prompt', '')

        # Criar ChatPromptTemplate
        from langchain_core.prompts import ChatPromptTemplate

        chat_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        print(f"   ✓ ChatPromptTemplate criado")

        # Fazer push para o Hub
        pushed_prompt = hub.push(
            prompt_name,
            chat_template,
            new_repo_is_public=True
        )

        print(f"   ✓ Prompt publicado com sucesso!")
        print(f"   📍 URL: https://smith.langchain.com/hub/{prompt_name}")
        return True

    except Exception as e:
        print(f"   ❌ Erro ao fazer push do prompt: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "LANGSMITH_ENDPOINT", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")

    # Carregar prompt otimizado
    from utils import load_yaml

    yaml_path = "prompts/bug_to_user_story_v2.yml"

    if not os.path.exists(yaml_path):
        print(f"❌ Arquivo não encontrado: {yaml_path}")
        print("\nCertifique-se de que o arquivo existe antes de continuar.")
        return 1

    prompt_yaml = load_yaml(yaml_path)

    if not prompt_yaml:
        print(f"❌ Erro ao carregar YAML: {yaml_path}")
        return 1

    # Extrair dados do prompt (a chave no YAML)
    prompt_key = "bug_to_user_story_v2"
    if prompt_key not in prompt_yaml:
        print(f"❌ Chave '{prompt_key}' não encontrada no YAML")
        print(f"   Chaves disponíveis: {list(prompt_yaml.keys())}")
        return 1

    prompt_data = prompt_yaml[prompt_key]

    # Nome do prompt para publicar
    prompt_name = f"{username}/bug_to_user_story_v2"

    if push_prompt_to_langsmith(prompt_name, prompt_data):
        print("\n✅ Push realizado com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Verifique o prompt publicado em:")
        print(f"   https://smith.langchain.com/hub/{prompt_name}")
        print("\n2. Execute a avaliação:")
        print("   python src/evaluate.py")
        return 0
    else:
        print("\n❌ Falha ao fazer push do prompt")
        print("\nVerifique:")
        print("- LANGSMITH_API_KEY está corretamente configurada no .env")
        print("- USERNAME_LANGSMITH_HUB está corretamente configurada")
        print("- A estrutura do YAML está correta")
        return 1


if __name__ == "__main__":
    sys.exit(main())
