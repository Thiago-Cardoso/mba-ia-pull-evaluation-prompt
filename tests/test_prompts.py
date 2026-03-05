"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture
    def prompt_file(self):
        """Fixture que carrega o prompt otimizado."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
        return load_prompts(str(prompt_path))

    def test_prompt_has_system_prompt(self, prompt_file):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert prompt_file is not None, "Arquivo de prompt não foi carregado"
        assert "bug_to_user_story_v2" in prompt_file, "Chave 'bug_to_user_story_v2' não encontrada"

        prompt_data = prompt_file["bug_to_user_story_v2"]
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não existe"
        assert prompt_data["system_prompt"].strip(), "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self, prompt_file):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompt_data = prompt_file["bug_to_user_story_v2"]
        system_prompt = prompt_data["system_prompt"].lower()

        # Verificar presença de definição de role em inglês ou português
        role_indicators = [
            "you are",
            "você é",
            "product manager",
            "gerente de produto",
            "experienced",
            "expertise",
            "especialista",
        ]

        has_role = any(indicator in system_prompt for indicator in role_indicators)
        assert has_role, (
            "Prompt não define claramente uma persona/role. "
            "Deveria conter frases como 'You are...' ou 'Você é...'"
        )

    def test_prompt_mentions_format(self, prompt_file):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt_data = prompt_file["bug_to_user_story_v2"]
        system_prompt = prompt_data["system_prompt"].lower()

        # Verificar menção de formato
        format_indicators = [
            "user story",
            "user stories",
            "markdown",
            "format",
            "formato",
            "como um",
            "as a",
            "i want",
            "eu quero",
            "given-when-then",
        ]

        has_format = any(indicator in system_prompt for indicator in format_indicators)
        assert has_format, (
            "Prompt não menciona formato esperado. "
            "Deveria mencionar 'User Story', 'Markdown' ou o padrão 'Como um...'"
        )

    def test_prompt_has_few_shot_examples(self, prompt_file):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt_data = prompt_file["bug_to_user_story_v2"]
        system_prompt = prompt_data["system_prompt"]

        # Verificar presença de exemplos - procurar por múltiplas ocorrências de "Example" ou "Como um"
        example_indicators = [
            "example",
            "exemplo",
            "**BUG REPORT:**",
            "**USER STORY:**",
            "Given",
            "When",
            "Then",
        ]

        count_indicators = sum(1 for indicator in example_indicators if indicator in system_prompt)

        assert count_indicators >= 3, (
            f"Prompt deveria conter exemplos (Few-shot Learning). "
            f"Encontrados {count_indicators} indicadores de exemplo, esperado >= 3"
        )

    def test_prompt_no_todos(self, prompt_file):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_data = prompt_file["bug_to_user_story_v2"]
        full_prompt = str(prompt_data)

        assert "[TODO]" not in full_prompt, (
            "Prompt ainda contém [TODO]. Por favor, complete todos os TODOs antes de submeter."
        )
        assert "TODO:" not in full_prompt, (
            "Prompt ainda contém TODO:. Por favor, complete todos os TODOs antes de submeter."
        )

    def test_minimum_techniques(self, prompt_file):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompt_data = prompt_file["bug_to_user_story_v2"]

        assert "techniques_applied" in prompt_data, (
            "Campo 'techniques_applied' não encontrado nos metadados"
        )

        techniques = prompt_data["techniques_applied"]
        assert isinstance(techniques, list), (
            "'techniques_applied' deveria ser uma lista YAML"
        )
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requerido, mas encontradas {len(techniques)}. "
            f"Técnicas encontradas: {techniques}"
        )

        # Validar que cada técnica é uma string não-vazia
        for tech in techniques:
            assert isinstance(tech, str) and tech.strip(), (
                f"Cada técnica deveria ser uma string não-vazia. Encontrado: {tech}"
            )

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])