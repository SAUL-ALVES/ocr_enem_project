from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import pytesseract
import json
import os
import PyPDF2
import asyncio
from enem_question_analyzer import compare_answers

# Inicialização do FastAPI
app = FastAPI()


# Diretório para salvar os resultados
if not os.path.exists("resultados"):
    os.makedirs("resultados")


@app.get("/")
def read_root():
    # aqui vai render do html da tela de boas-vindas
    return {"message": "Bem-vindo ao sistema de OCR para Gabaritos do ENEM"}


@app.post("/upload_gabarito/")
async def upload_gabarito(file: UploadFile = File(...)):
    """
    Endpoint para fazer o upload e processar um gabarito.
    Aceita arquivos nos formatos PDF, JPG, JPEG ou PNG.
    """
    try:
        # 1. Processamento de Entrada
        # Suporte a múltiplos formatos
        file_extension = file.filename.split(".")[-1].lower()

        if file_extension in ["jpg", "jpeg", "png"]:
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # 2. Pré-processamento de Imagens
            # Aqui você adicionaria a lógica para correção de inclinação, etc.
            # Por enquanto, usaremos a imagem diretamente

            # Exemplo de reconhecimento simples com Tesseract
            text = pytesseract.image_to_string(image)

            # Simulação de análise e resultado
            resultado = {
                "filename": file.filename,
                "status": "Processado com sucesso",
                "texto_reconhecido_exemplo": text,
            }

        elif file_extension == "pdf":
            # Leitura de PDFs
            reader = PyPDF2.PdfReader(file.file)
            num_pages = len(reader.pages)

            if num_pages > 1:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Cada arquivo PDF deve conter apenas um gabarito."
                    },
                )

            # Aqui você precisaria converter a página do PDF para uma imagem para o OCR
            
            return JSONResponse(
                status_code=501,
                content={
                    "message": "Processamento de PDF ainda não implementado completamente."
                },
            )

        else:
            return JSONResponse(
                status_code=400, content={"error": "Formato de arquivo não suportado."}
            )

        # 3. Saída e Análise (Salvar em JSON)
        # Salva o resultado em um arquivo JSON
        output_filename = os.path.join(
            "resultados", f"{os.path.basename(file.filename)}.json"
        )
        with open(output_filename, "w") as f:
            json.dump(resultado, f, indent=4)

        return JSONResponse(content=resultado)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@app.get("/results/")
def send_questions(list_answers, year, test_day):
    results = asyncio.run(compare_answers(list_answers, year)) 


# Para rodar a aplicação: uvicorn main:app --reload
