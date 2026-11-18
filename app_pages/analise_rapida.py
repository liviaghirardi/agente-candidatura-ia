import streamlit as st

from app import assistente_chat as chat
from app.adaptador_curriculo import AdaptadorCurriculo
from app.analisador_vaga import AnalisadorVaga

PREFIXO = "rapida"

st.caption(
    "Cole a descrição da vaga para extrair os requisitos e ver um resumo rápido de compatibilidade "
    "com o seu perfil."
)

with st.form(f"{PREFIXO}_form"):
    col_cv, col_vaga = st.columns(2)
    with col_cv:
        st.subheader("Seu currículo")
        usar_perfil, arquivo, texto = chat.campos_curriculo(PREFIXO)
    with col_vaga:
        st.subheader("A vaga")
        descricao_vaga = st.text_area(
            "Descrição da vaga",
            height=320,
            placeholder="Ex: Buscamos Desenvolvedor(a) Python...",
        )
    enviar = st.form_submit_button(
        "Analisar vaga e adaptar currículo", type="primary", icon=":material/rocket_launch:"
    )

if enviar:
    curriculo = chat.resolver_curriculo(usar_perfil, arquivo, texto)
    if not descricao_vaga.strip():
        st.warning("Por favor, cole a descrição de uma vaga antes de continuar.")
    elif not curriculo:
        st.warning("Envie o currículo (PDF ou texto) para continuar.")
    else:
        with st.spinner("Analisando vaga e cruzando com o seu perfil profissional..."):
            try:
                chave = st.session_state.get("gemini_api_key") or None
                analisador = AnalisadorVaga(api_key=chave)
                adaptador = AdaptadorCurriculo(api_key=chave)

                analise_vaga = analisador.analisar(descricao_vaga)
                resultado_adaptacao = adaptador.adaptar({"curriculo": curriculo}, analise_vaga)
            except Exception as e:
                st.error(f"Ocorreu um erro durante o processamento: {e}")
                st.stop()

        st.success("Análise concluída com sucesso!")

        aba1, aba2, aba3 = st.tabs(["Adaptação e match", "Análise da vaga", "Palavras-chave ATS"])

        with aba1:
            st.metric(label="Match com a vaga", value=resultado_adaptacao.get("match_score_estimado", "N/A"))

            st.subheader("Resumo profissional personalizado")
            st.info(resultado_adaptacao.get("resumo_personalizado", ""))

            st.subheader("Pontos fortes alinhados")
            for ponto in resultado_adaptacao.get("pontos_fortes", []):
                st.markdown(f"- {ponto}")

            st.subheader("Recomendações de melhoria")
            for rec in resultado_adaptacao.get("recomendacoes_melhoria", []):
                st.markdown(f"- {rec}")

        with aba2:
            st.subheader("Detalhes extraídos da vaga")
            st.write(f"**Cargo:** {analise_vaga.get('cargo', 'N/A')}")
            st.write(f"**Nível:** {analise_vaga.get('nivel', 'N/A')}")

            st.markdown("**Requisitos obrigatórios:**")
            for req in analise_vaga.get("requisitos_obrigatorios", []):
                st.markdown(f"- {req}")

            st.markdown("**Diferenciais:**")
            for dif in analise_vaga.get("diferenciais", []):
                st.markdown(f"- {dif}")

        with aba3:
            st.subheader("Palavras-chave para otimização ATS")
            palavras = analise_vaga.get("palavras_chave", [])
            if palavras:
                st.write("Inclua termos como estes no seu currículo para passar pelos filtros automáticos:")
                st.code(", ".join(palavras))
            else:
                st.write("Nenhuma palavra-chave destacada.")
