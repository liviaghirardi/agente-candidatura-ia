import json
from app.gemini_client import GeminiClient

class AnalisadorVaga:
    def __init__(self, api_key: str | None = None):
        self.gemini = GeminiClient(api_key=api_key)

    def analisar(self, descricao_vaga: str) -> dict:
        """
        Analisa a descrição da vaga e retorna um dicionário estruturado
        com requisitos, diferenciais e palavras-chave.
        """
        prompt = f"""
        Você é um recrutador técnico especialista em tecnologia e sistemas. 
        Analise a descrição da vaga abaixo e extraia as seguintes informações em formato JSON estrito (sem blocos de código markdown extras, apenas o JSON puro):
        - cargo: O título exato ou aproximado do cargo.
        - nivel: O nível da vaga (Ex: Júnior, Pleno, Sênior, Estágio).
        - requisitos_obrigatorios: Lista de tecnologias, competências ou experiências obrigatórias.
        - diferenciais: Lista de itens desejáveis ou diferenciais.
        - palavras_chave: Lista de palavras-chave cruciais para otimização de ATS (Applicant Tracking Systems).

        Descrição da Vaga:
        {descricao_vaga}
        """

        resposta_bruta = self.gemini.gerar_resposta(prompt)
        
        # Limpa eventuais marcações de bloco de código markdown que a IA possa retornar
        resposta_limpa = resposta_bruta.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(resposta_limpa)
        except json.JSONDecodeError:
            # Caso a IA retorne texto livre, encapsulamos em um dicionário de fallback
            return {
                "cargo": "Não identificado",
                "nivel": "Não identificado",
                "requisitos_obrigatorios": [],
                "diferenciais": [],
                "palavras_chave": [],
                "analise_bruta": resposta_bruta
            }