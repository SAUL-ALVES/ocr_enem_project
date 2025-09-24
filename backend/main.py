from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import pytesseract
import json
import os
import PyPDF2
from datetime import datetime

import traceback


from enem_question_analyzer import compare_answers
from roi_code import extrair_codigo_aluno_automatico
from leitor_gabarito import extrair_respostas_gabarito
import shutil
import uuid


app = FastAPI()

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.exists(os.path.join(FRONTEND_DIST, "assets")):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
        name="assets",
    )

UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs("resultados", exist_ok=True)


def carregar_dados_alunos():
    """Carrega os dados do arquivo alunos.json."""
    with open("alunos.json", "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_dados_alunos(dados):
    """Salva os dados no arquivo alunos.json."""
    with open("alunos.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


@app.get("/")
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))


@app.post("/corrigir/")
async def corrigir(
    file: UploadFile = File(...),
    day: str = Form(...),
    year: str = Form(...),
    language: str = Form(...),
):

    try:
        file_extension = file.filename.split(".")[-1].lower()
        temp_filename = f"{uuid.uuid4()}.{file_extension}"
        temp_filepath = os.path.join(UPLOADS_DIR, temp_filename)

        with open(temp_filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        codigo_aluno = None
        respostas_dict = None

        if file_extension in ["jpg", "jpeg", "png"]:
            codigo_aluno = extrair_codigo_aluno_automatico(temp_filepath)
            if not codigo_aluno or "?" in codigo_aluno:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Não foi possível ler o código do aluno."},
                )

            respostas_dict = extrair_respostas_gabarito(temp_filepath)
            if not respostas_dict:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Não foi possível extrair as respostas do gabarito."
                    },
                )
        else:
            return JSONResponse(
                status_code=400, content={"error": "Formato de arquivo não suportado."}
            )

        inicio_questao = 1
        fim_questao = 90
        list_answers = [
            respostas_dict.get(i, "X") for i in range(inicio_questao, fim_questao + 1)
        ]

        day_int = int(day)
        year_int = int(year)

        results_analysis = await compare_answers(
            list_answers, year_int, test_day=day_int, language=language
        )

        alunos_db = carregar_dados_alunos()
        if codigo_aluno not in alunos_db:
            return JSONResponse(
                status_code=404,
                content={"error": f"Aluno com código '{codigo_aluno}' não encontrado."},
            )

        aluno = alunos_db[codigo_aluno]
        if "historico" not in aluno:
            aluno["historico"] = []

        nova_entrada_historico = {
            "data_correcao": datetime.now().isoformat(),
            "mensagem": f"Prova do aluno {aluno.get('nome', '')} corrigida e histórico salvo!",
            "codigo_aluno": codigo_aluno,
            "nome_aluno": aluno.get("nome", "Não cadastrado"),
            "detalhes_prova": {"ano": year, "dia": day, "idioma": language},
            "analise": results_analysis,
        }

        aluno["historico"].append(nova_entrada_historico)
        salvar_dados_alunos(alunos_db)

        resultado_final = {
            "mensagem": f"Prova do aluno {aluno.get('nome', '')} corrigida e histórico salvo!",
            "codigo_aluno": codigo_aluno,
            "nome_aluno": aluno.get("nome", "Não cadastrado"),
            "detalhes_prova": {"ano": year, "dia": day, "idioma": language},
            "analise": results_analysis,
        }

        output_filename = os.path.join(
            "resultados", f"{codigo_aluno}_{year}_{day}.json"
        )
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(resultado_final, f, ensure_ascii=False, indent=4)

        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)

        return JSONResponse(resultado_final)

    except Exception as e:

        print("!!!!!!!!!! OCORREU UM ERRO CRÍTICO !!!!!!!!!!")
        print(traceback.format_exc())
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        if "temp_filepath" in locals() and os.path.exists(temp_filepath):
            os.remove(temp_filepath)

        return JSONResponse(
            status_code=500,
            content={"error": "Erro interno no servidor.", "details": str(e)},
        )

@app.get("/resumo_historico/")
def resumo_historico():
    try:
        alunos_db = carregar_dados_alunos()
        resumo_list = []

        for codigo, aluno in alunos_db.items():
            nome = aluno.get("nome", "Não cadastrado")
            historico = aluno.get("historico", [])

            resumo_list.append(f"{codigo} - {nome}")

            if not historico:
                resumo_list.append("   Sem histórico")
                continue

            for correcao in historico:
                # tenta pegar do novo formato
                detalhes = correcao.get("detalhes_prova", {})
                analise = correcao.get("analise", {})

                ano = detalhes.get("ano", "?")
                dia = detalhes.get("dia", "?")
                idioma = detalhes.get("idioma", "?")

                acertos = analise.get("acertos", 0)
                total_questoes = analise.get("total_questoes", 0)

                resumo_list.append(
                    f"   Ano: {ano} | Dia: {dia} | Idioma: {idioma} → {acertos} / {total_questoes}"
                )

        resumo_str = "\n".join(resumo_list)
        return JSONResponse({"resumo": resumo_str})

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Erro ao gerar resumo do histórico.", "details": str(e)},
        )

