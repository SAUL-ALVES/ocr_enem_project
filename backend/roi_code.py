# -*- coding: utf-8 -*-
import cv2
import pytesseract
import re
import numpy as np
from imutils import contours
import unicodedata

try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    pytesseract.get_tesseract_version()
except Exception as e:
    print("ERRO: Tesseract não encontrado ou o caminho está incorreto.")
    print("Verifique o caminho na variável 'pytesseract.pytesseract.tesseract_cmd'.")
    exit()


def detectar_codigo_por_bolhas(roi_gabarito):
    """
    ### ALTERAÇÃO ###
    Versão modificada para usar valores dinâmicos baseados no tamanho da ROI,
    tornando a detecção de bolhas e colunas mais robusta.
    """
    if roi_gabarito is None or roi_gabarito.size == 0:
        return "", roi_gabarito

    LIMIAR_DE_PREENCHIMENTO = 90.0
    roi_h, roi_w, _ = roi_gabarito.shape

    
    MIN_BUBBLE_SIZE = int(roi_w * 0.1)
    
    
    MAX_COL_DIST = int(roi_w * 0.13)

    img_cinza = cv2.cvtColor(roi_gabarito, cv2.COLOR_BGR2GRAY)
    img_cinza_invertida = cv2.bitwise_not(img_cinza)

    img_blur = cv2.GaussianBlur(img_cinza, (5, 5), 0)
    img_thresh = cv2.adaptiveThreshold(
        img_blur, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        15, 
        4   
    )

    cnts, _ = cv2.findContours(img_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bolhas_validas = []
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        aspect_ratio = w / float(h)
        
        if w >= MIN_BUBBLE_SIZE and h >= MIN_BUBBLE_SIZE and 0.8 <= aspect_ratio <= 1.2:
            bolhas_validas.append(c)

    if not bolhas_validas:
        return "", roi_gabarito

    bolhas_validas = contours.sort_contours(bolhas_validas, method="left-to-right")[0]
    colunas = []
    coluna_atual = [bolhas_validas[0]]
    last_x = cv2.boundingRect(bolhas_validas[0])[0]

    for bolha in bolhas_validas[1:]:
        x, _, _, _ = cv2.boundingRect(bolha)
        
        if abs(x - last_x) < MAX_COL_DIST:
            coluna_atual.append(bolha)
        else:
            colunas.append(coluna_atual)
            coluna_atual = [bolha]
            last_x = x
    colunas.append(coluna_atual)

    codigo_aluno = ""

    for idx, coluna_cnts in enumerate(colunas[:2]):
        coluna_cnts = contours.sort_contours(coluna_cnts, method="top-to-bottom")[0]

        medias_intensidade = []
        for c in coluna_cnts:
            mask = np.zeros(img_cinza_invertida.shape, dtype="uint8")
            (x, y, w, h) = cv2.boundingRect(c)
            centro_x, centro_y = x + w // 2, y + h // 2
            raio = int(w * 0.4)
            cv2.circle(mask, (centro_x, centro_y), raio, 255, -1)

            mask = cv2.bitwise_and(img_cinza_invertida, img_cinza_invertida, mask=mask)
            pixels_da_bolha = mask[mask > 0]
            media = np.mean(pixels_da_bolha) if pixels_da_bolha.size > 0 else 0
            medias_intensidade.append(media)

        if not medias_intensidade:
            continue
        
        indice_marcado_na_lista = np.argmax(medias_intensidade)
        maior_media_encontrada = medias_intensidade[indice_marcado_na_lista]

        if maior_media_encontrada > LIMIAR_DE_PREENCHIMENTO:
            contorno_marcado = coluna_cnts[indice_marcado_na_lista]
            y_marcado = cv2.boundingRect(contorno_marcado)[1]
            y_primeira_encontrada = cv2.boundingRect(coluna_cnts[0])[1]
            y_ultima_encontrada = cv2.boundingRect(coluna_cnts[-1])[1]
            
            if len(coluna_cnts) > 1:
                altura_celula = (y_ultima_encontrada - y_primeira_encontrada) / (len(coluna_cnts) - 1)
            else:
                altura_celula = 0

            if altura_celula > 0:
                indice_relativo = round((y_marcado - y_primeira_encontrada) / altura_celula)
            else:
                indice_relativo = 0

            digito_real_da_primeira = 0
            digito_marcado = digito_real_da_primeira + indice_relativo
            codigo_aluno += str(digito_marcado)

            (x, y, w, h) = cv2.boundingRect(contorno_marcado)
            cv2.circle(roi_gabarito, (x + w // 2, y + h // 2), int(w * 0.6), (0, 255, 0), 2)
            print(f"Análise da Coluna {idx+1}: Bolha MARCADA encontrada com intensidade {maior_media_encontrada:.2f}, dígito {digito_marcado}\n")
        else:
            codigo_aluno += "?"
            print(f"Análise da Coluna {idx+1}: Nenhuma bolha marcada (maior intensidade foi {maior_media_encontrada:.2f}, abaixo de {LIMIAR_DE_PREENCHIMENTO})\n")

    if codigo_aluno == "??":
        return "", roi_gabarito

    return codigo_aluno, roi_gabarito


def normalizar_texto(texto):
    if not texto:
        return ""
    texto = texto.lower()
    texto = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    return texto


def extrair_codigo_aluno_automatico(caminho_imagem):
    try:
        imagem_original = cv2.imread(caminho_imagem)
        if imagem_original is None:
            print(f"ERRO: Não foi possível carregar a imagem: '{caminho_imagem}'")
            return None

        
        LARGURA_PADRAO = 1285
        altura, largura, _ = imagem_original.shape
        fator_redimensionamento = LARGURA_PADRAO / largura
        nova_altura = int(altura * fator_redimensionamento)
        
        print(f"Redimensionando imagem de {largura}x{altura} para {LARGURA_PADRAO}x{nova_altura}")
        imagem_original = cv2.resize(imagem_original, (LARGURA_PADRAO, nova_altura), interpolation=cv2.INTER_AREA)
        

        imagem_cinza = cv2.cvtColor(imagem_original, cv2.COLOR_BGR2GRAY)
        _, imagem_binaria = cv2.threshold(imagem_cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        dados = pytesseract.image_to_data(imagem_binaria, output_type=pytesseract.Output.DICT, lang="por")

        anchor_box = None
        for i in range(len(dados["level"])):
            conf = int(dados["conf"][i])
            palavra = normalizar_texto(dados["text"][i])

            if conf > 40 and re.search(r"assinatur", palavra):
                x_ancora, y_ancora = dados["left"][i], dados["top"][i]
                anchor_box = (x_ancora, y_ancora)
                print(f"✅ Âncora 'Assinatura' encontrada (variação: '{palavra}') em: x={x_ancora}, y={y_ancora}")
                break

        if anchor_box is None:
            print("ERRO: Âncora 'Assinatura' não encontrada. Usando fallback...")
            for i, palavra in enumerate(dados["text"]):
                if "simulado" in palavra.lower():
                    x_ancora = dados["left"][i]
                    y_ancora = dados["top"][i]
                    
                    
                    x_ancora = x_ancora - 280
                    y_ancora = y_ancora + 10
                    anchor_box = (x_ancora, y_ancora)
                    print(f"⚠️ Usando fallback com 'Simulado' em x={x_ancora}, y={y_ancora}")
                    break

        if anchor_box is None:
            print("ERRO: Nenhuma âncora válida encontrada.")
            return None

        x_ancora, y_ancora = anchor_box

        
        offset_y = 188
        offset_x = 7
        roi_height = 270
        roi_width = 100
        y_roi_start = y_ancora + offset_y
        y_roi_end = y_roi_start + roi_height
        x_roi_start = x_ancora + offset_x
        x_roi_end = x_roi_start + roi_width

        h_img, w_img, _ = imagem_original.shape
        print("\n--- Depuração da ROI ---")
        print(f"Dimensões da Imagem (Pós-redimensionamento): Largura={w_img}, Altura={h_img}")
        print(f"ROI Calculada: x=[{x_roi_start}:{x_roi_end}], y=[{y_roi_start}:{y_roi_end}]")

        
        if x_roi_start < 0 or y_roi_start < 0 or x_roi_end > w_img or y_roi_end > h_img:
            print("AVISO: Coordenadas da ROI fora dos limites. Ajustando para caber na imagem.")
            x_roi_start = max(0, x_roi_start)
            y_roi_start = max(0, y_roi_start)
            x_roi_end = min(w_img, x_roi_end)
            y_roi_end = min(h_img, y_roi_end)
            print(f"▶️ ROI Ajustada: x=[{x_roi_start}:{x_roi_end}], y=[{y_roi_start}:{y_roi_end}]")

        print("Coordenadas da ROI são válidas. Analisando bolhas...")

        roi_para_analise = imagem_original[y_roi_start:y_roi_end, x_roi_start:x_roi_end]
        codigo_limpo, roi_com_deteccoes = detectar_codigo_por_bolhas(roi_para_analise)

        imagem_original[y_roi_start:y_roi_end, x_roi_start:x_roi_end] = roi_com_deteccoes

        cv2.rectangle(imagem_original, (x_roi_start, y_roi_start), (x_roi_end, y_roi_end), (0, 0, 255), 2)
        cv2.imwrite("resultado_deteccao_bolhas.jpg", imagem_original)

        print("\n--- RESULTADO ---")
        print(f"Código do Aluno por Bolhas: {codigo_limpo if codigo_limpo else 'Nenhum código detectado.'}")
        print("\n📝 Imagem 'resultado_deteccao_bolhas.jpg' salva com as detecções.")

        return codigo_limpo

    except Exception as e:
        print(f"ERRO GERAL INESPERADO: {e}")
        return None


if __name__ == "__main__":
    
    caminho_da_prova = "backend/prova4.png"
    extrair_codigo_aluno_automatico(caminho_da_prova)