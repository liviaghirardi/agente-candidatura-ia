"""Lógica compartilhada pelas páginas de conversa (compatibilidade e entrevista)."""

import json
from pathlib import Path

import streamlit as st
from pypdf import PdfReader

from app.gemini_client import GeminiClient

RAIZ = Path(__file__).resolve().parent.parent
PASTA_PROMPTS = RAIZ / "prompts"
PERFIL_PATH = RAIZ / "app" / "perfil.json"


def carregar_prompt(nome: str) -> str:
    """Lê um prompt de sistema da pasta `prompts/`."""
    return (PASTA_PROMPTS / f"{nome}.md").read_text(encoding="utf-8")


def ler_pdf(arquivo) -> str:
    """Extrai o texto de um PDF enviado pelo usuário."""
    leitor = PdfReader(arquivo)
    return "\n".join((pagina.extract_text() or "") for pagina in leitor.pages).strip()


def perfil_local_em_texto() -> str | None:
    """Devolve o perfil salvo em `app/perfil.json` (se existir) como texto JSON."""
    if not PERFIL_PATH.exists():
        return None
    with open(PERFIL_PATH, encoding="utf-8") as f:
        return json.dumps(json.load(f), ensure_ascii=False, indent=2)


def campos_curriculo(prefixo: str) -> tuple:
    """
    Desenha os campos para a pessoa informar o currículo (usar dentro de um st.form).
    Devolve (usar_perfil_local, arquivo_pdf, texto_colado).
    """
    usar_perfil = False
    if PERFIL_PATH.exists():
        usar_perfil = st.toggle(
            "Usar meu perfil salvo (app/perfil.json)",
            value=True,
            key=f"{prefixo}_usar_perfil",
        )
    arquivo = st.file_uploader(
        "Currículo em PDF",
        type=["pdf"],
        key=f"{prefixo}_pdf",
        help="Opcional se você colar o texto abaixo ou usar o perfil salvo.",
    )
    texto = st.text_area(
        "Ou cole o texto do currículo",
        height=180,
        key=f"{prefixo}_texto",
    )
    return usar_perfil, arquivo, texto


def resolver_curriculo(usar_perfil: bool, arquivo, texto: str) -> str:
    """Escolhe a fonte do currículo: texto colado > PDF > perfil salvo."""
    if texto.strip():
        return texto.strip()
    if arquivo is not None:
        return ler_pdf(arquivo)
    if usar_perfil:
        return perfil_local_em_texto() or ""
    return ""


def cliente_gemini() -> GeminiClient:
    """Cria o cliente usando a chave digitada na barra lateral, se houver."""
    return GeminiClient(api_key=st.session_state.get("gemini_api_key") or None)


def chave_estado(prefixo: str) -> str:
    return f"{prefixo}_mensagens"


def iniciar_conversa(prefixo: str, mensagem_inicial: str, nome_prompt: str) -> None:
    """Envia o contexto inicial (currículo, vaga etc.) e guarda a primeira resposta."""
    mensagens = [{"role": "user", "content": mensagem_inicial}]
    resposta = cliente_gemini().conversar(mensagens, carregar_prompt(nome_prompt))
    mensagens.append({"role": "assistant", "content": resposta})
    st.session_state[chave_estado(prefixo)] = mensagens


def conversa_iniciada(prefixo: str) -> bool:
    return bool(st.session_state.get(chave_estado(prefixo)))


def exibir_conversa(prefixo: str, nome_prompt: str, placeholder: str, sugestoes: dict[str, str], nome_arquivo: str) -> None:
    """Mostra o histórico, recebe novas mensagens e oferece download da última resposta."""
    mensagens = st.session_state[chave_estado(prefixo)]

    with st.container(horizontal=True):
        if st.button("Recomeçar", icon=":material/restart_alt:", key=f"{prefixo}_recomecar"):
            del st.session_state[chave_estado(prefixo)]
            st.rerun()
        st.download_button(
            "Baixar última resposta (.md)",
            data=mensagens[-1]["content"],
            file_name=nome_arquivo,
            mime="text/markdown",
            icon=":material/download:",
            key=f"{prefixo}_baixar",
        )

    with st.expander("Dados enviados (currículo e vaga)", icon=":material/description:"):
        st.text(mensagens[0]["content"])

    # A primeira mensagem (contexto) fica no expander acima; o chat começa na resposta da IA
    for msg in mensagens[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input(placeholder, key=f"{prefixo}_entrada", submit_mode="disable")

    if sugestoes and len(mensagens) <= 2:
        escolha = st.pills(
            "Sugestões",
            list(sugestoes.keys()),
            key=f"{prefixo}_sugestoes",
            label_visibility="collapsed",
        )
        if escolha and not prompt:
            prompt = sugestoes[escolha]

    if prompt:
        mensagens.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    resposta = cliente_gemini().conversar(mensagens, carregar_prompt(nome_prompt))
                except Exception as e:
                    mensagens.pop()  # descarta a mensagem para a pessoa poder reenviar
                    st.error(str(e), title="Não foi possível responder agora")
                    return
            st.markdown(resposta)
        mensagens.append({"role": "assistant", "content": resposta})
        st.rerun()  # atualiza o botão de download com a nova resposta
