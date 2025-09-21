from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import pytesseract
import json
import os
import PyPDF2
from pdf2image import convert_from_bytes
from enem_question_analyzer import compare_answers

# importa tuas funções já prontas
from roi_code import extrair_codigo_aluno_automatico
from leitor_gabarito import extrair_respostas_gabarito

app = FastAPI()

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
        file_extension = file.filename.split(".")[-1].lower()
        contents = await file.read()

        # === CASO IMAGEM (PNG/JPG) ===
        if file_extension in ["jpg", "jpeg", "png"]:
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # === CASO PDF ===
        elif file_extension == "pdf":
            reader = PyPDF2.PdfReader(file.file)
            if len(reader.pages) > 1:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Cada PDF deve conter apenas 1 página de gabarito."}
                )
            # Converter PDF em imagem
            imagens_pdf = convert_from_bytes(contents, dpi=300)
            if not imagens_pdf:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Falha ao converter PDF em imagem."}
                )
            # Converte PIL -> OpenCV
            image = cv2.cvtColor(np.array(imagens_pdf[0]), cv2.COLOR_RGB2BGR)

        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Formato de arquivo não suportado."}
            )

        # Salvar temporário
        temp_path = os.path.join("resultados", f"temp_{file.filename}.png")
        cv2.imwrite(temp_path, image)

        # Extrair código e gabarito
        codigo_aluno = extrair_codigo_aluno_automatico(temp_path)
        gabarito = extrair_respostas_gabarito(temp_path)

        # OCR do texto inteiro (opcional, debug)
        text = pytesseract.image_to_string(image)

        # Comparar respostas
        results = await compare_answers(
            list(gabarito.values()), 
            year, 
            test_day=day, 
            language=language
        )

        # Montar JSON final
        resultado = {
            "filename": file.filename,
            "day": day,
            "year": year,
            "language": language,
            "codigo_aluno": codigo_aluno,
            "gabarito": gabarito,
            "texto_reconhecido": text,
            "results": results
        }

        # Salvar resultado em JSON
        output_filename = os.path.join("resultados", f"{os.path.basename(file.filename)}.json")
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)

        return JSONResponse(resultado)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
