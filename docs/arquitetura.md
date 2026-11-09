# Arquitetura do Sistema - Agente de Candidatura IA

```mermaid
graph TD
    A[Usuário e Streamlit] -->|Carrega Perfil JSON| B[Módulo Pydantic]
    A -->|Cola Descrição da Vaga| C[Analisador de Vaga]
    C -->|Prompt e Dados| D[Google Gemini SDK]
    D -->|JSON Estruturado| E[Adaptador e Verificador]
    E -->|Validação| F[Aprovado?]
    F -->|Não| E
    F -->|Sim| G[Gerador de PDF ATS]
    G -->|PDF e Relatório| A