"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith(prompt_name: str = "leonanluppi/bug_to_user_story_v1") -> bool:
    """
    Faz pull de um prompt do LangSmith Hub e salva em arquivo YAML local.

    Args:
        prompt_name: Nome do prompt no formato {username}/{prompt_name}

    Returns:
        True se sucesso, False caso contrário
    """
    print(f"\n📥 Puxando prompt do LangSmith Hub: {prompt_name}")

    try:
        # Puxar prompt do hub
        prompt_template = hub.pull(prompt_name)
        print(f"   ✓ Prompt carregado com sucesso")

        # Extrair mensagens do prompt
        messages = prompt_template.messages

        system_prompt = ""
        user_prompt = ""

        # Processar mensagens
        for msg in messages:
            if hasattr(msg, "prompt"):
                template = msg.prompt
                if hasattr(template, "template"):
                    content = template.template
                else:
                    content = str(template)

                # Determinar se é system ou user
                msg_type = msg.__class__.__name__
                if "System" in msg_type:
                    system_prompt = content
                elif "Human" in msg_type or "User" in msg_type:
                    user_prompt = content

        # Criar estrutura de dados
        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"]
            }
        }

        # Salvar em YAML
        output_path = "prompts/bug_to_user_story_v1.yml"
        if save_yaml(prompt_data, output_path):
            print(f"   ✓ Prompt salvo em: {output_path}")
            return True
        else:
            print(f"   ❌ Erro ao salvar prompt em: {output_path}")
            return False

    except Exception as e:
        print(f"   ❌ Erro ao fazer pull do prompt: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "LANGSMITH_ENDPOINT"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    if not username:
        print("⚠️  USERNAME_LANGSMITH_HUB não configurada no .env")
        print("Como obter: Publique um prompt no LangSmith Hub, abra o prompt,")
        print("clique no ícone de cadeado para torná-lo público, e copie o username da URL.")
        return 1

    prompt_name = f"{username}/bug_to_user_story_v1"

    if pull_prompts_from_langsmith(prompt_name):
        print("\n✅ Pull realizado com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Edite o prompt em: prompts/bug_to_user_story_v1.yml")
        print("2. Crie uma versão otimizada: prompts/bug_to_user_story_v2.yml")
        print("3. Faça push do prompt otimizado: python src/push_prompts.py")
        return 0
    else:
        print("\n❌ Falha ao fazer pull do prompt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
