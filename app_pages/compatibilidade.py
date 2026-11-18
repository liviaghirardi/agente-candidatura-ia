import streamlit as st

from app import assistente_chat as chat

PREFIXO = "compat"
PROMPT = "compatibilidade_curriculo"

st.caption(
    "Uma banca de avaliadores tenta reprovar seu currículo para a vaga. Depois, a IA pergunta "
    "sobre cada lacuna (se você tem a habilidade e onde a adquiriu) antes de montar o currículo novo."
)

if not chat.conversa_iniciada(PREFIXO):
    with st.form(f"{PREFIXO}_form"):
        col_cv, col_vaga = st.columns(2)
        with col_cv:
            st.subheader("Seu currículo")
            usar_perfil, arquivo, texto = chat.campos_curriculo(PREFIXO)
        with col_vaga:
            st.subheader("A vaga")
            vaga = st.text_area("Descrição da vaga", height=320, key=f"{PREFIXO}_vaga")
        enviar = st.form_submit_button(
            "Analisar compatibilidade", type="primary", icon=":material/fact_check:"
        )

    if enviar:
        curriculo = chat.resolver_curriculo(usar_perfil, arquivo, texto)
        if not curriculo:
            st.warning("Envie o currículo (PDF ou texto) para continuar.")
        elif not vaga.strip():
            st.warning("Cole a descrição da vaga para continuar.")
        else:
            mensagem = f"MEU CURRÍCULO:\n{curriculo}\n\nA VAGA:\n{vaga.strip()}"
            with st.spinner("A banca está avaliando seu currículo..."):
                try:
                    chat.iniciar_conversa(PREFIXO, mensagem, PROMPT)
                except Exception as e:
                    st.error(str(e), title="Não foi possível analisar agora")
                    st.stop()
            st.rerun()
else:
    chat.exibir_conversa(
        PREFIXO,
        PROMPT,
        placeholder="Responda à pergunta da IA...",
        sugestoes={
            ":material/skip_next: Pular perguntas e montar o currículo": "Pode pular as perguntas restantes e montar o currículo final com o que você já tem.",
        },
        nome_arquivo="curriculo_otimizado.md",
    )
