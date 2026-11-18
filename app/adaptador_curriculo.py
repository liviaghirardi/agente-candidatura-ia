import json
from app.gemini_client import GeminiClient

class AdaptadorCurriculo:
    def __init__(self, api_key: str | None = None):
        self.gemini = GeminiClient(api_key=api_key)

    def adaptar(self, perfil_json: dict, analise_vaga: dict) -> dict:
        """
        Cruza os dados do perfil com a análise da vaga para gerar 
        sugestões de adaptação e um resumo direcionado.
        """
        prompt = f"""
        Você é um especialista em carreira, recrutamento e otimização de currículos para sistemas ATS.
        Com base no perfil do candidato e na análise da vaga fornecidos abaixo, gere um JSON estrito (sem blocos de markdown extras, apenas o JSON puro) contendo:
        - resumo_personalizado: Um resumo profissional curto e de alto impacto adaptado especificamente para esta vaga.
        - pontos_fortes: Lista de pontos do perfil que mais se alinham aos requisitos obrigatórios da vaga.
        - recomendacoes_melhoria: Sugestões prontas de o que o candidato pode destacar ou ajustar no currículo para aumentar a aderência.
        - match_score_estimado: Uma porcentagem estimada de compatibilidade (ex: "85%").

        Perfil do Candidato:
        {json.dumps(perfil_json, ensure_ascii=False)}

        Análise da Vaga:
        {json.dumps(analise_vaga, ensure_ascii=False)}
        """

        resposta_bruta = self.gemini.gerar_resposta(prompt)
        resposta_limpa = resposta_bruta.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(resposta_limpa)
        except json.JSONDecodeError:
            return {
                "resumo_personalizado": "Erro ao processar o formato JSON pela IA.",
                "pontos_fortes": [],
                "recomendacoes_melhoria": [],
                "match_score_estimado": "N/A",
                "analise_bruta": resposta_bruta
            }