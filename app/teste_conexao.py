from app.gemini_client import GeminiClient

try:
    print("Conectando ao Gemini...")
    ia = GeminiClient()
    resposta = ia.gerar_resposta("Responda apenas com: 'Conexão estabelecida com sucesso!'")
    print(resposta.strip())
except Exception as e:
    print(f"Erro no teste: {e}")