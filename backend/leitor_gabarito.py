# -*- coding: utf-8 -*-
import cv2
import numpy as np
import csv
import os
from math import hypot

# -------------------------
# Utilitários
# -------------------------
def order_points(pts):
    # pts: array Nx2
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect

def group_positions(positions, tol=None):
    """Agrupa posições 1D (sorted) em clusters próximos. Retorna média de cada cluster."""
    if len(positions) == 0:
        return []
    pos = sorted(positions)
    diffs = np.diff(pos) if len(pos) > 1 else np.array([0])
    if tol is None:
        med = np.median(diffs) if len(diffs) > 0 else 0
        tol = max(10, med * 0.6)  # heurística
    clusters = []
    current = [pos[0]]
    for p in pos[1:]:
        if p - current[-1] <= tol:
            current.append(p)
        else:
            clusters.append(int(np.mean(current)))
            current = [p]
    clusters.append(int(np.mean(current)))
    return clusters

# -------------------------
# Detecta quadradinhos (âncoras) — retorna centros e bboxes
# -------------------------
def detectar_quadrados(imagem, debug=False):
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # fecha pequenos furos
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    conts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    marcadores = []
    for c in conts:
        area = cv2.contourArea(c)
        if area < 200 or area > 8000:
            continue
        x,y,w,h = cv2.boundingRect(c)
        ar = w / float(h) if h>0 else 0
        # quadrado razoável
        if 0.7 <= ar <= 1.3:
            # aproximar para polígono e ver se tem 4 vértices
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                cx = x + w//2
                cy = y + h//2
                marcadores.append({"x": x, "y": y, "w": w, "h": h, "cx": cx, "cy": cy, "area": area})

    # ordenar por posição (y then x)
    marcadores = sorted(marcadores, key=lambda m: (m["y"], m["x"]))

    if debug:
        img = imagem.copy()
        for m in marcadores:
            cv2.rectangle(img, (m["x"], m["y"]), (m["x"]+m["w"], m["y"]+m["h"]), (0,0,255), 2)
        cv2.imwrite("debug_markers.png", img)
        print(f"[DEBUG] Marcadores detectados: {len(marcadores)} -> debug_markers.png")

    return marcadores

# -------------------------
# Warpar imagem usando os 4 marcadores (se encontrados)
# -------------------------
def warp_from_markers(imagem, marcadores, debug=False):
    if len(marcadores) < 4:
        return imagem  # sem warp, retorna original

    # pegar 4 marcadores extremos (top-left, top-right, bottom-right, bottom-left)
    centers = np.array([[m["cx"], m["cy"]] for m in marcadores], dtype=np.float32)

    # selecionar quatro extremos: usar convex hull dos centros e escolher 4 com extremos por quadrantes
    # abordagem simples: pegar os 4 com x+y min/max e x-y min/max
    sums = centers.sum(axis=1)
    diffs = centers[:,0] - centers[:,1]
    tl = centers[np.argmin(sums)]
    br = centers[np.argmax(sums)]
    tr = centers[np.argmin(diffs)]
    bl = centers[np.argmax(diffs)]

    pts = np.array([tl, tr, br, bl], dtype="float32")
    rect = order_points(pts)

    (tl, tr, br, bl) = rect
    # largura e altura de destino
    widthA = hypot(br[0] - bl[0], br[1] - bl[1])
    widthB = hypot(tr[0] - tl[0], tr[1] - tl[1])
    maxWidth = int(max(widthA, widthB) * 1.05)

    heightA = hypot(tr[0] - br[0], tr[1] - br[1])
    heightB = hypot(tl[0] - bl[0], tl[1] - bl[1])
    maxHeight = int(max(heightA, heightB) * 1.05)

    # garantir tamanhos razoáveis
    maxWidth = max(1000, maxWidth)
    maxHeight = max(1200, maxHeight)

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(imagem, M, (maxWidth, maxHeight))

    if debug:
        cv2.imwrite("debug_warp.png", warped)
        print("[DEBUG] warped salvo em debug_warp.png")

    return warped

# -------------------------
# Detecta bolhas e retorna centros e tamanhos
# -------------------------
def detectar_bolhas(imagem_warp, debug=False):
    gray = cv2.cvtColor(imagem_warp, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,15,4)
    # limpar ruído
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers = []
    h_img, w_img = imagem_warp.shape[:2]
    # heurísticas de tamanho relativas
    min_w = max(6, int(w_img * 0.012))
    max_w = max(20, int(w_img * 0.045))

    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        ar = w / float(h) if h>0 else 0
        if min_w <= w <= max_w and 0.7 <= ar <= 1.3 and area > 20:
            cx = x + w//2
            cy = y + h//2
            centers.append({"cx": cx, "cy": cy, "w": w, "h": h, "bbox":(x,y,w,h)})

    if debug:
        img = imagem_warp.copy()
        for c in centers:
            cv2.circle(img, (c["cx"], c["cy"]), int(max(c["w"], c["h"])//2), (255,0,0), 1)
        cv2.imwrite("debug_centers.png", img)
        print(f"[DEBUG] bolhas detectadas: {len(centers)} -> debug_centers.png")

    return centers, thresh

# -------------------------
# Mapeia colunas e linhas (grid) e decide alternativa por linha
# -------------------------
def extrair_gabarito_da_pagina(imagem_warp, debug=False):
    centers, thresh = detectar_bolhas(imagem_warp, debug=debug)
    if len(centers) == 0:
        raise RuntimeError("Nenhuma bolha detectada na página (centers vazio).")

    xs = sorted(list({c["cx"] for c in centers}))
    ys = sorted(list({c["cy"] for c in centers}))

    grouped_x = group_positions(xs)
    grouped_y = group_positions(ys)

    # se houver ~10 colunas (duas colunas de 5) -> página 1 (1-90)
    # se houver ~5 colunas -> possivelmente apenas um bloco
    if len(grouped_x) >= 9:
        # ordenar e dividir em duas metades
        grouped_x = sorted(grouped_x)
        left_cols = grouped_x[:5]
        right_cols = grouped_x[5:10]
        cols_blocks = [sorted(left_cols), sorted(right_cols)]
        starts = [1, 46]
    elif len(grouped_x) >= 5:
        cols_blocks = [sorted(grouped_x[:5])]
        starts = [1]
    else:
        # fallback: tentar agrupar por quantas colunas existem
        cols_blocks = [sorted(grouped_x)]
        starts = [1]

    # garantir linhas (deveria ser 45)
    # se grouped_y tiver muito mais/menos valores, refinar tol
    if len(grouped_y) < 40 or len(grouped_y) > 60:
        # tentar recomputar com tol menor/maior
        grouped_y = group_positions(ys, tol= int(np.median(np.diff(sorted(ys))) if len(ys)>1 else 25))

    grouped_y = sorted(grouped_y)
    num_rows = len(grouped_y)
    # se num_rows > 60 -> reduzir (possivelmente detectou múltiplas por linha)
    # meta: 45
    # criar mapeamento final: para cada bloco (left/right), percorre todas as linhas
    gabarito = {}

    # prepare image copy to draw results
    visual = imagem_warp.copy()

    for b_idx, cols in enumerate(cols_blocks):
        start_q = starts[b_idx]
        for row_idx, row_y in enumerate(grouped_y):
            # para cada das 5 colunas em cols calcular fill fraction
            fills = []
            for col_x in cols:
                r = max(8, int(np.mean([c["w"] for c in centers]) * 0.6))
                # criar máscara circular
                mask = np.zeros(thresh.shape, dtype="uint8")
                cv2.circle(mask, (int(col_x), int(row_y)), r, 255, -1)
                # contar pixels preenchidos dentro da máscara (thresh já é invertida: preenchido = white)
                filled = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))
                area = np.pi * (r ** 2)
                fills.append(filled / (area + 1e-8))
            # escolher maior
            idx_max = int(np.argmax(fills))
            best = fills[idx_max]
            # heurística: considerar marcada se fração > 0.20 (20%)
            chosen = "-" if best < 0.20 else "ABCDE"[idx_max]
            question_number = start_q + row_idx
            gabarito[question_number] = chosen

            # desenhar no visual
            color = (0,255,0) if chosen != "-" else (0,0,255)
            cv2.putText(visual, chosen, (int(cols[idx_max]-10), int(row_y+6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    if debug:
        cv2.imwrite("debug_gabarito_visual.png", visual)
        print("[DEBUG] visual com escolhas salvo em debug_gabarito_visual.png")

    # ordenar por questão e retornar lista ordenada
    max_q = max(gabarito.keys())
    result_list = [gabarito.get(i, "-") for i in range(1, max_q+1)]
    return result_list, visual

# -------------------------
# Interface principal: processa 1 ou 2 páginas e retorna gabarito 1..N
# -------------------------
def processar_arquivos(pages):
    """
    pages: lista de caminhos (1 ou 2 imagens). Retorna lista de respostas ordenadas (1..N)
    """
    all_answers = {}
    for i, path in enumerate(pages):
        img = cv2.imread(path)
        if img is None:
            raise FileNotFoundError(f"Imagem não encontrada: {path}")

        marcadores = detectar_quadrados(img, debug=True)
        warped = warp_from_markers(img, marcadores, debug=True)
        answers, visual = extrair_gabarito_da_pagina(warped, debug=True)

        # se page é primeira (i==0) e answers length == 90 -> assume 1..90
        if len(answers) >= 90:
            # assume page contains 90 (1..90)
            for q_idx, ans in enumerate(answers[:90], start=1):
                all_answers[q_idx] = ans
        else:
            # assume answers correspond to a single block of 45
            offset = 1 if i == 0 else 91
            for q_idx, ans in enumerate(answers[:45], start=offset):
                all_answers[q_idx] = ans

        # salvar visual anotado por página (opcional)
        base = os.path.splitext(os.path.basename(path))[0]
        cv2.imwrite(f"marked_{base}.png", visual)
        print(f"[INFO] marked image salvo: marked_{base}.png")

    # juntar e ordenar
    max_q = max(all_answers.keys())
    final = [all_answers.get(i, "-") for i in range(1, max_q+1)]
    # salvar CSV
    with open("gabarito_final.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Questao", "Resposta"])
        for i, r in enumerate(final, start=1):
            writer.writerow([i, r])
    print("[INFO] gabarito_final.csv salvo.")
    return final

# -------------------------
# Executar (exemplo)
# -------------------------
if __name__ == "__main__":
    # exemplo: se você tiver apenas a página 1 (1-90)
    pages = ["backend/prova_1.png"]   # ou ["backend/prova_1.png", "backend/prova_2.png"]
    final = processar_arquivos(pages)
    print(final)
