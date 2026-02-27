# GF Agent — Grupo Fácil IA

> Agente de inteligência artificial institucional do Grupo Fácil, construído com arquitetura limpa e suporte a múltiplos provedores de LLM.

---

## Visão Geral

O GF Agent é o agente motor da empresa — uma base extensível para automação de processos, suporte a decisões e leitura inteligente de documentos. Ele foi projetado para evoluir em direção a agentes satélites por área, RAG com documentos internos e governança corporativa.

---

## Funcionalidades

- **Chat institucional** com identidade e comportamento definidos para o Grupo Fácil
- **Leitura inteligente de PDFs** com três estratégias automáticas:
  - Extração direta de texto (PDFs selecionáveis)
  - OCR via Tesseract (PDFs escaneados)
  - Análise via Claude Vision (diagramas e fluxogramas)
- **Sanitização de dados sensíveis** (CPF, CNPJ, e-mail) antes do envio ao LLM
- **Suporte a múltiplos provedores**: Gemini, OpenAI e Anthropic
- **Interface web** via Streamlit

---

## Arquitetura

O projeto segue arquitetura em camadas (Clean Architecture):

```
src/
├── domain/             # Entidades, contratos e identidade do agente
│   ├── models.py
│   ├── ports.py
│   └── agent_identity.py
├── application/        # Casos de uso e regras de negócio
│   ├── use_cases.py
│   ├── document_use_cases.py
│   └── policy_service.py
├── infrastructure/     # Adaptadores externos (LLMs, PDF)
│   ├── gemini_llm.py
│   ├── openai_llm.py
│   └── pdf_extractor.py
├── presentation/       # Interface com o usuário
│   └── streamlit_app.py
└── config.py           # Configurações centralizadas via pydantic-settings
```

---

## Pré-requisitos

- Python 3.12+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) instalado em `C:\Program Files\Tesseract-OCR\`
- [Poppler 23.11.0](https://github.com/oschwartz10612/poppler-windows/releases/tag/v23.11.0-0) extraído em `C:\poppler\poppler-23.11.0\`

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/Rezek-Saude/gf-agent.git
cd gf-agent

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

---

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
GEMINI_API_KEY=sua-chave-aqui
GEMINI_MODEL=gemini-2.5-flash

OPENAI_API_KEY=sua-chave-aqui       # opcional
ANTHROPIC_API_KEY=sua-chave-aqui    # necessário para análise de diagramas via Vision

POPPLER_PATH=C:\poppler\poppler-23.11.0\poppler-23.11.0\Library\bin
```

> O arquivo `.env` está no `.gitignore` e nunca deve ser commitado.

---

## Execução

```bash
streamlit run src/presentation/streamlit_app.py
```

---

## Dependências principais

| Pacote | Uso |
|---|---|
| `streamlit` | Interface web |
| `google-generativeai` | SDK oficial do Gemini |
| `openai` | SDK da OpenAI |
| `anthropic` | SDK da Anthropic (Claude Vision) |
| `pypdf` | Extração de texto em PDFs |
| `pytesseract` | OCR via Tesseract |
| `Pillow` | Processamento de imagens |
| `pdf2image` | Conversão de PDF para imagem |
| `pydantic-settings` | Gerenciamento de configurações |

---

## Roadmap

- [ ] RAG com documentos internos
- [ ] Agentes satélites por área (RH, Financeiro, Jurídico)
- [ ] Políticas de governança e auditoria (LGPD)
- [ ] Autenticação e controle de acesso
- [ ] Deploy em nuvem

---

## Licença

Uso interno — Grupo Fácil © 2026