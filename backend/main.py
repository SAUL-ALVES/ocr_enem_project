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

from roi_code import extrair_codigo_aluno_automatico
import shutil
import uuid

# Inicialização do FastAPI
app = FastAPI()

FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")


UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs("resultados", exist_ok=True)


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
    
    file_extension = file.filename.split(".")[-1].lower()
    temp_filename = f"{uuid.uuid4()}.{file_extension}"
    temp_filepath = os.path.join(UPLOADS_DIR, temp_filename)

    try:
        with open(temp_filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # --- NOVA ADIÇÃO: Variável para armazenar o código do aluno ---
        codigo_aluno = None

        if file_extension in ["jpg", "jpeg", "png"]:
            # --- NOVA ADIÇÃO: Chamar a função para extrair o código do aluno ---
            codigo_aluno = extrair_codigo_aluno_automatico(temp_filepath)

            # O resto do seu código original continua aqui, lendo do arquivo salvo
            image = cv2.imread(temp_filepath)
            text = pytesseract.image_to_string(image)
            list_answers = []  # TODO: extrair respostas reais

        elif file_extension == "pdf":
            with open(temp_filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                if len(reader.pages) > 1:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Cada arquivo PDF deve conter apenas um gabarito."}
                    )
            list_answers = [] # TODO: 
        
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Formato de arquivo não suportado."}
            )

        # Rodar análise de respostas
        results = await compare_answers(list_answers, year, test_day=day, language=language)

        # Preparar resultado final
        resultado = {
            
            "codigo_aluno": codigo_aluno,
            "filename": file.filename,
            "day": day,
            "year": year,
            "language": language,
            "texto_reconhecido": text if 'text' in locals() else None,
            "results": results
        }

        
        output_filename = os.path.join("resultados", f"{os.path.basename(file.filename)}.json")
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)

        return JSONResponse(resultado)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)

# Para rodar a aplicação: uvicorn main:app --reload