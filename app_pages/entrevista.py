import streamlit as st

from app import assistente_chat as chat

PREFIXO = "entrevista"
PROMPT = "roteiro_entrevista"

st.caption(
    "Gera um roteiro de entrevista a partir do fit cultural da vaga, das suas experiências e do seu "
    "currículo. Depois você pode ajustar o roteiro ou fazer uma simulação de entrevista."
)

if not chat.conversa_iniciada(PREFIXO):
    with st.form(f"{PREFIXO}_form"):
        col_cv, col_vaga = st.columns(2)
        with col_cv:
            st.subheader("Seu currículo")
            usar_perfil, arquivo, texto = chat.campos_curriculo(PREFIXO)
        with col_vaga:
            st.subheader("A vaga e a empresa")
            vaga = st.text_area("Descrição da vaga", height=180, key=f"{PREFIXO}_vaga")
            empresa = st.text_area(
                "Sobre a empresa e a cultura (opcional)",
                height=100,
                key=f"{PREFIXO}_empresa",
                placeholder="Missão, valores, trechos do site ou do LinkedIn, o que você sabe do time...",
            )
            etapa = st.text_input(
                "Etapa e formato da entrevista (opcional)",
                key=f"{PREFIXO}_etapa",
                placeholder="Ex.: entrevista com o RH por vídeo, 30 min",
            )
        enviar = st.form_submit_button(
            "Montar roteiro", type="primary", icon=":material/record_voice_over:"
        )

    if enviar:
        curriculo = chat.resolver_curriculo(usar_perfil, arquivo, texto)
        if not curriculo:
            st.warning("Envie o currículo (PDF ou texto) para continuar.")
        elif not vaga.strip():
            st.warning("Cole a descrição da vaga para continuar.")
        else:
            partes = [f"MEU CURRÍCULO:\n{curriculo}", f"A VAGA:\n{vaga.strip()}"]
            if empresa.strip():
                partes.append(f"SOBRE A EMPRESA E A CULTURA:\n{empresa.strip()}")
            if etapa.strip():
                partes.append(f"ETAPA E FORMATO DA ENTREVISTA:\n{etapa.strip()}")
            with st.spinner("Montando seu roteiro de entrevista..."):
                try:
                    chat.iniciar_conversa(PREFIXO, "\n\n".join(partes), PROMPT)
                except Exception as e:
                    st.error(str(e), title="Não foi possível montar o roteiro agora")
                    st.stop()
            st.rerun()
else:
    chat.exibir_conversa(
        PREFIXO,
        PROMPT,
        placeholder="Peça ajustes ou responda à pergunta da simulação...",
        sugestoes={
            ":material/mic: Simular a entrevista": "Vamos fazer a simulação de entrevista. Pode começar com a primeira pergunta.",
            ":material/edit_note: Aprofundar as respostas técnicas": "Aprofunde as respostas das perguntas técnicas, com mais detalhes das minhas experiências.",
        },
        nome_arquivo="roteiro_entrevista.md",
    )
