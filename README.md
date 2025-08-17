# Projeto: OCR para Gabaritos do ENEM

## Visão Geral

Este projeto visa desenvolver um sistema de reconhecimento óptico de caracteres (OCR) focado na leitura e correção automática de gabaritos de simulados do ENEM.  
O sistema será capaz de processar entradas em formato PDF (digital e escaneado) e imagens capturadas por smartphones (JPG, PNG).  
Atualmente, a correção manual desses gabaritos é um processo demorado e sujeito a erros humanos, com baixo aproveitamento na geração de relatórios de desempenho individual e coletivo.  
A automação desse processo busca reduzir significativamente o tempo de processamento e aumentar a precisão dos resultados.

## Funcionalidades Principais

O sistema oferece as seguintes funcionalidades:

- **Processamento de Entrada**: Suporte para arquivos PDF (digital e escaneado) e imagens (JPG, PNG) de smartphones.
- **Pré-processamento de Imagens**: Correção de inclinação, remoção de ruídos e sombras, ajuste de contraste e brilho, e detecção automática de bordas do gabarito.
- **Reconhecimento OCR Especializado**: Modelo customizado para reconhecer marcas de preenchimento, letras (A-E) e números (questões). O sistema também valida o preenchimento, verificando duplo preenchimento e detectando respostas em branco.
- **Saída e Análise**: Geração de relatórios individuais com nota final, acertos por área e questões incorretas para os alunos. O sistema também permite a visualização de relatórios por turma para professores.
- **Exportação de Resultados**: Os resultados podem ser exportados para planilhas (CSV), para integração com outros sistemas (JSON) ou como um relatório PDF formatado.

## Arquitetura Técnica

O projeto é construído com os seguintes componentes:

- **Backend (Python)**: Utiliza **FastAPI** para o serviço web, **OpenCV** para o processamento de imagens, **Tesseract OCR** com modelos treinados e **PyPDF2** para a manipulação de PDFs.
- **Frontend (Web)**: A interface web será desenvolvida usando **React.js**.
- **Armazenamento de Dados**: Os resultados serão armazenados em arquivos **JSON** bem organizados. O **Redis** é utilizado para cache de processamento, otimizando a performance.

## Requisitos de Sistema

- Python 3.9+
- Tesseract OCR 5.0+
- OpenCV 4.5+

## Como Rodar o Projeto

1. **Clone o repositório:**
    ```bash
    git clone https://github.com/SAUL-ALVES/ocr_enem_project
    cd ocr_enem_project
    ```

2. **Crie e ative o ambiente virtual:**
    ```bash
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3. **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Execute a aplicação:**
    ```bash
    uvicorn main:app --reload
    ```

    A API estará disponível em `http://127.0.0.1:8000`.  
    Você pode acessar a documentação interativa em `http://127.0.0.1:8000/docs`.

## Contribuição

Contribuições são bem-vindas! Se você tiver alguma ideia ou encontrar um bug, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a licença **MIT**.  
Você pode usar, modificar e distribuir este projeto livremente, desde que mantenha os créditos aos autores originais.
