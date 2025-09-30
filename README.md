# NUVE Violence Detection System

Sistema de detecção automatizada de violência em prontuários eletrônicos utilizando processamento de linguagem natural baseado em regras lexicais.

## 📋 Sobre o Projeto

Modelo desenvolvido para o Núcleo de Vigilância Epidemiológica (NUVE) do Hospital das Clínicas da FMUSP como parte do TCC do MBA em Data Science e Analytics da USP/ESALQ.

- **Sensibilidade**: 84.9% (IC95%: 79.2-90.6%)
- **Tempo de processamento**: 3.7s/prontuário
- **Redução de tempo**: 99.5%

## 🚀 Instalação

```bash
git clone https://github.com/rafamarquesg/MBA.git
cd MBA
pip install -r requirements.txt
```

## 📚 Documentação

- Código principal: `src/detector.py`
- Léxico: `src/lexicon.py` e `data/lexicon/violence_terms.json`
- Exemplos de uso: `examples/basic_usage.py`