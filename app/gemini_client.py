import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

# Carrega as variáveis do arquivo .env
load_dotenv()

# Tempo máximo (em segundos) de cada requisição à API
TIMEOUT_SEGUNDOS = int(os.getenv("GEMINI_TIMEOUT", "60"))


class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("MODELO_GEMINI", "gemini-3.8-flash")
        # Modelos alternativos (separados por vírgula) usados se o principal estiver indisponível
        self.modelos_reserva = [
            m.strip()
            for m in os.getenv("MODELOS_GEMINI_RESERVA", "gemini-3.7-flash,gemini-3.5-flash-lite,gemini-3.1-flash-lite").split(",")
            if m.strip() and m.strip() != self.model_name
        ]

        if not self.api_key:
            raise ValueError("A chave GEMINI_API_KEY não foi encontrada no arquivo .env!")

        # Inicializa o cliente com timeout e número limitado de tentativas,
        # para não ficar travado quando a API estiver sobrecarregada (erro 503).
        self.client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(
                timeout=TIMEOUT_SEGUNDOS * 1000,  # o SDK espera milissegundos
                retry_options=types.HttpRetryOptions(
                    attempts=3,
                    initial_delay=2.0,
                    max_delay=10.0,
                    http_status_codes=[429, 500, 502, 503, 504],
                ),
            ),
        )

    def gerar_resposta(self, prompt: str) -> str:
        """Envia o prompt ao modelo configurado, tentando os modelos reserva se ele estiver indisponível."""
        ultimo_erro = None
        for modelo in [self.model_name, *self.modelos_reserva]:
            try:
                response = self.client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                )
                return response.text
            except errors.APIError as e:
                ultimo_erro = e
                # 503/429/5xx: modelo sobrecarregado -> tenta o próximo; 404: modelo inexistente -> tenta o próximo
                if e.code in (404, 429, 500, 502, 503, 504):
                    print(f"[GeminiClient] Modelo '{modelo}' indisponível ({e.code}). Tentando o próximo...")
                    continue
                raise RuntimeError(f"Erro ao comunicar com a API do Gemini: {e}") from e
            except Exception as e:
                ultimo_erro = e
                print(f"[GeminiClient] Falha com o modelo '{modelo}': {e}. Tentando o próximo...")
                continue

        raise RuntimeError(
            "Nenhum modelo do Gemini respondeu. A API pode estar sobrecarregada; "
            f"tente novamente em alguns minutos. Último erro: {ultimo_erro}"
        )
