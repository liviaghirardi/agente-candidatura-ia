import streamlit as st

st.set_page_config(page_title="Agente de Candidatura IA", page_icon=":material/smart_toy:", layout="wide")

with st.sidebar:
    st.text_input(
        "Sua chave do Gemini (opcional)",
        type="password",
        key="gemini_api_key",
        help=(
            "Se preencher, o app usa a sua chave em vez da chave do servidor. "
            "Crie uma grátis em aistudio.google.com. Ela fica só nesta sessão."
        ),
    )
    st.caption(
        "A IA nunca deve inventar experiências: tudo que entra no currículo vem do seu "
        "currículo ou das suas respostas."
    )

pagina = st.navigation(
    [
        st.Page(
            "app_pages/compatibilidade.py",
            title="Compatibilidade e currículo",
            icon=":material/fact_check:",
            default=True,
            help=(
                "Avalia seu currículo para a vaga, pergunta sobre as habilidades que faltam "
                "e onde você as adquiriu, e só então monta o currículo otimizado."
            ),
        ),
        st.Page(
            "app_pages/entrevista.py",
            title="Roteiro de entrevista",
            icon=":material/record_voice_over:",
            help=(
                "Monta um roteiro de entrevista com base no fit cultural da vaga e nas suas "
                "experiências, com opção de simular a entrevista."
            ),
        ),
        st.Page(
            "app_pages/analise_rapida.py",
            title="Análise rápida",
            icon=":material/bolt:",
            help="Extrai requisitos e palavras-chave da vaga e estima o match com seu perfil.",
        ),
    ],
    position="top",
)

st.title(pagina.title, icon=pagina.icon)
pagina.run()
