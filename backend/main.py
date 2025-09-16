from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import pytesseract
import json
import os
import PyPDF2
from enem_question_analyzer import compare_answers

# Inicialização do FastAPI
app = FastAPI()

from fastapi.staticfiles import StaticFiles
import os

FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

if not os.path.exists("resultados"):
    os.makedirs("resultados")


@app.get("/")
def read_root():
   return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
    
    
@app.post("/corrigir/")
async def corrigir(
    file: UploadFile = File(...),
    day: str = Form(...),
    year: int = Form(...),
    language: str = Form(...)
):
    try:
        # Detecta extensão do arquivo
        file_extension = file.filename.split(".")[-1].lower()
        contents = await file.read()

        if file_extension in ["jpg", "jpeg", "png"]:
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # OCR
            text = pytesseract.image_to_string(image)

            # Aqui você pode extrair lista de respostas do texto OCR
            list_answers = []  # TODO: extrair respostas reais

        elif file_extension == "pdf":
            reader = PyPDF2.PdfReader(file.file)
            if len(reader.pages) > 1:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Cada arquivo PDF deve conter apenas um gabarito."}
                )
            # TODO: converter PDF para imagem e extrair respostas
            list_answers = []

        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Formato de arquivo não suportado."}
            )

        # Rodar análise de respostas
        results = await compare_answers(list_answers, year, test_day=day, language=language)  #linguagem a adicionar 

        # Preparar resultado final
        resultado = {
            "filename": file.filename,
            "day": day,
            "year": year,
            "language": language,
            "texto_reconhecido": text if 'text' in locals() else None,
            "results": results
        }

        # Salvar JSON
        output_filename = os.path.join("resultados", f"{os.path.basename(file.filename)}.json")
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)

        return JSONResponse(resultado)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
# Para rodar a aplicação: uvicorn main:app --reload