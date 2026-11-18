import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

# Carrega as variáveis do arquivo .env
load_dotenv()

# Tempo máximo (em segundos) de cada requisição à API
TIMEOUT_SEGUNDOS = int(os.getenv("GEMINI_TIMEOUT", "60"))

# Códigos de erro em que vale a pena tentar outro modelo
CODIGOS_TENTAR_PROXIMO = (404, 429, 500, 502, 503, 504)


class GeminiClient:
    def __init__(self, api_key: str | None = None):
        # Uma chave informada pelo usuário na interface tem prioridade sobre a do .env
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("MODELO_GEMINI", "gemini-3.8-flash")
        # Modelos alternativos (separados por vírgula) usados se o principal estiver indisponível
        self.modelos_reserva = [
            m.strip()
            for m in os.getenv(
                "MODELOS_GEMINI_RESERVA",
                "gemini-3.7-flash,gemini-3.5-flash-lite,gemini-3.1-flash-lite",
            ).split(",")
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

    def _gerar(self, contents, config: types.GenerateContentConfig | None = None) -> str:
        """Chama o modelo principal e, se ele estiver indisponível, os modelos reserva."""
        ultimo_erro = None
        for modelo in [self.model_name, *self.modelos_reserva]:
            try:
                response = self.client.models.generate_content(
                    model=modelo,
                    contents=contents,
                    config=config,
                )
                return response.text or ""
            except errors.APIError as e:
                ultimo_erro = e
                if e.code in CODIGOS_TENTAR_PROXIMO:
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

    def gerar_resposta(self, prompt: str) -> str:
        """Envia um prompt único e devolve o texto da resposta."""
        return self._gerar(prompt)

    def conversar(self, mensagens: list[dict], instrucao_sistema: str) -> str:
        """
        Continua uma conversa de vários turnos.

        `mensagens` é uma lista de {"role": "user" | "assistant", "content": str}.
        `instrucao_sistema` define o papel e as regras do assistente.
        """
        contents = [
            types.Content(
                role="model" if m["role"] == "assistant" else "user",
                parts=[types.Part(text=m["content"])],
            )
            for m in mensagens
        ]
        config = types.GenerateContentConfig(system_instruction=instrucao_sistema)
        return self._gerar(contents, config)
