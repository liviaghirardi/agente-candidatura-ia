from app.analisador_vaga import AnalisadorVaga

def testar():
    print("Inicializando o Analisador de Vagas...")
    analisador = AnalisadorVaga()

    # Exemplo de descrição de vaga fictícia para teste
    vaga_exemplo = """
    Buscamos Desenvolvedor(a) Python Júnior para compor nosso time de tecnologia.
    Requisitos obrigatórios:
    - Experiência com Python e FastAPI ou Flask.
    - Conhecimento em bancos de dados relacionais (PostgreSQL).
    - Noções de Git e controle de versão.
    Diferenciais:
    - Experiência com Docker e Cloud (AWS).
    - Conhecimento em Streamlit.
    """

    print("\nAnalisando a descrição da vaga...")
    resultado = analisador.analisar(vaga_exemplo)

    print("\n--- Resultado da Análise (JSON) ---")
    import json
    print(json.dumps(resultado, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    testar()