import streamlit as st
import json
import os
from app.analisador_vaga import AnalisadorVaga
from app.adaptador_curriculo import AdaptadorCurriculo

# Configuração da página
st.set_page_config(page_title="Agente de Candidatura IA", page_icon="🤖", layout="wide")

st.title("🤖 Agente Inteligente de Candidatura e Otimização de Currículo")
st.markdown("Cole a descrição da vaga desejada abaixo para analisar os requisitos e adaptar o seu perfil profissional com inteligência artificial.")

# Carrega o perfil do candidato local
PERFIL_PATH = os.path.join("app", "perfil.json")
try:
    with open(PERFIL_PATH, "r", encoding="utf-8") as f:
        perfil_data = json.load(f)
except FileNotFoundError:
    st.error("Arquivo `perfil.json` não encontrado na pasta `app`!")
    perfil_data = {}

# Área de entrada da vaga
descricao_vaga = st.text_area("📋 Cole a Descrição da Vaga Aqui:", height=200, placeholder="Ex: Buscamos Desenvolvedor(a) Python...")

if st.button("🚀 Analisar Vaga e Adaptar Currículo", type="primary"):
    if not descricao_vaga.strip():
        st.warning("Por favor, cole a descrição de uma vaga antes de continuar.")
    else:
        with st.spinner("Analisando vaga e cruzando com o seu perfil profissional..."):
            try:
                # Inicializa os módulos
                analisador = AnalisadorVaga()
                adaptador = AdaptadorCurriculo()

                # Processa a vaga
                analise_vaga = analisador.analisar(descricao_vaga)
                
                # Adapta o currículo
                resultado_adaptacao = adaptador.adaptar(perfil_data, analise_vaga)

                st.success("Análise concluída com sucesso!")

                # Layout em abas para organizar os resultados
                aba1, aba2, aba3 = st.tabs(["🎯 Adaptação & Match", "📊 Análise da Vaga", "💡 Palavras-Chave ATS"])

                with aba1:
                    st.subheader("Compatibilidade Estimada")
                    match_score = resultado_adaptacao.get("match_score_estimado", "N/A")
                    st.metric(label="Match com a Vaga", value=match_score)

                    st.subheader("Resumo Profissional Personalizado")
                    st.info(resultado_adaptacao.get("resumo_personalizado", ""))

                    st.subheader("Pontos Fortes Alinhados")
                    for ponto in resultado_adaptacao.get("pontos_fortes", []):
                        st.markdown(f"- {ponto}")

                    st.subheader("Recomendações de Melhoria")
                    for rec in resultado_adaptacao.get("recomendacoes_melhoria", []):
                        st.markdown(f"- {rec}")

                with aba2:
                    st.subheader("Detalhes Extraídos da Vaga")
                    st.write(f"**Cargo:** {analise_vaga.get('cargo', 'N/A')}")
                    st.write(f"**Nível:** {analise_vaga.get('nivel', 'N/A')}")
                    
                    st.markdown("**Requisitos Obrigatórios:**")
                    for req in analise_vaga.get("requisitos_obrigatorios", []):
                        st.markdown(f"- {req}")

                    st.markdown("**Diferenciais:**")
                    for dif in analise_vaga.get("diferenciais", []):
                        st.markdown(f"- {dif}")

                with aba3:
                    st.subheader("Palavras-Chave para Otimização ATS")
                    palavras = analise_vaga.get("palavras_chave", [])
                    if palavras:
                        st.write("Inclua termos como estes no seu currículo para passar pelos filtros automáticos:")
                        st.code(", ".join(palavras))
                    else:
                        st.write("Nenhuma palavra-chave destacada.")

            except Exception as e:
                st.error(f"Ocorreu um erro durante o processamento: {e}")