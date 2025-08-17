# Projeto: OCR para Gabaritos do ENEM

## Visão Geral

[cite_start]Este projeto visa desenvolver um sistema de reconhecimento óptico de caracteres (OCR) focado na leitura e correção automática de gabaritos de simulados do ENEM[cite: 9]. [cite_start]O sistema será capaz de processar entradas em formato PDF (digital e escaneado) e imagens capturadas por smartphones (JPG, PNG)[cite: 10, 32]. [cite_start]Atualmente, a correção manual desses gabaritos é um processo demorado e sujeito a erros humanos, com baixo aproveitamento na geração de relatórios de desempenho individual e coletivo[cite: 14]. [cite_start]A automação desse processo busca reduzir significativamente o tempo de processamento e aumentar a precisão dos resultados[cite: 15].

## Funcionalidades Principais

O sistema oferece as seguintes funcionalidades:

* [cite_start]**Processamento de Entrada**: Suporte para arquivos PDF (digital e escaneado) e imagens (JPG, PNG) de smartphones[cite: 36, 37].
* [cite_start]**Pré-processamento de Imagens**: Correção de inclinação, remoção de ruídos e sombras, ajuste de contraste e brilho, e detecção automática de bordas do gabarito[cite: 40, 41, 42, 43].
* [cite_start]**Reconhecimento OCR Especializado**: Modelo customizado para reconhecer marcas de preenchimento, letras (A-E) e números (questões)[cite: 46, 47]. [cite_start]O sistema também valida o preenchimento, verificando duplo preenchimento e detectando respostas em branco[cite: 50, 51].
* [cite_start]**Saída e Análise**: Geração de relatórios individuais com nota final, acertos por área e questões incorretas para os alunos[cite: 24, 6, 26, 6]. [cite_start]O sistema também permite a visualização de relatórios por turma para professores[cite: 21].
* [cite_start]**Exportação de Resultados**: Os resultados podem ser exportados para planilhas (CSV), para integração com outros sistemas (JSON) ou como um relatório PDF formatado[cite: 58, 59, 60].

## Arquitetura Técnica

O projeto é construído com os seguintes componentes:

* [cite_start]**Backend (Python)**: Utiliza **FastAPI** para o serviço web [cite: 73][cite_start], **OpenCV** para o processamento de imagens [cite: 70][cite_start], **Tesseract OCR** com modelos treinados [cite: 71] [cite_start]e **PyPDF2** para a manipulação de PDFs[cite: 72].
* [cite_start]**Frontend (Web)**: A interface web será desenvolvida usando **React.js**[cite: 76].
* **Armazenamento de Dados**: Os resultados serão armazenados em arquivos **JSON** bem organizados. [cite_start]O **Redis** é utilizado para cache de processamento, otimizando a performance[cite: 28, 5, 29, 2].

## Requisitos de Sistema

* [cite_start]Python 3.9+ [cite: 81]
* [cite_start]Tesseract OCR 5.0+ [cite: 82]
* [cite_start]OpenCV 4.5+ [cite: 83]

## Como Rodar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/SAUL-ALVES/ocr_enem_project
    cd ocr_enem_project
    ```
2.  **Crie e ative o ambiente virtual:**
    ```bash
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Execute a aplicação:**
    ```bash
    uvicorn main:app --reload
    ```
    A API estará disponível em `http://127.0.0.1:8000`. Você pode acessar a documentação interativa em `http://127.0.0.1:8000/docs`.

## Contribuição

Contribuições são bem-vindas! Se você tiver alguma ideia ou encontrar um bug, sinta-se à vontade para abrir uma issue ou enviar um pull request.