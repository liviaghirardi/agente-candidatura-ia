import os
from dotenv import load_dotenv
from google import genai

# Carrega as variáveis do arquivo .env
load_dotenv()

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("MODELO_GEMINI", "gemini-2.5-flash")
        
        if not self.api_key:
            raise ValueError("A chave GEMINI_API_KEY não foi encontrada no arquivo .env!")
        
        # Inicializa o cliente oficial da nova SDK do Google Genai
        self.client = genai.Client(api_key=self.api_key)

    def gerar_resposta(self, prompt: str) -> str:
        """Envia um prompt simples para o modelo Flash configurado."""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Erro ao comunicar com a API do Gemini: {e}")