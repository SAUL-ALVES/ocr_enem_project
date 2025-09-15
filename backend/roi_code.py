# -*- coding: utf-8 -*-
import cv2
import pytesseract
import re
import numpy as np
from imutils import contours 


try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    pytesseract.get_tesseract_version()
except Exception as e:
    print("ERRO: Tesseract não encontrado ou o caminho está incorreto.")
    print("Verifique o caminho na variável 'pytesseract.pytesseract.tesseract_cmd'.")
    exit()


def detectar_codigo_por_bolhas(roi_gabarito):
    """
    Detecta o código do aluno analisando as bolhas preenchidas dentro de uma ROI.
    Recebe uma imagem (a ROI) e retorna o código e a mesma imagem com detecções.
    """
    if roi_gabarito is None or roi_gabarito.size == 0:
        print("ERRO INTERNO: A função de detecção de bolhas recebeu uma ROI vazia.")
        return "", roi_gabarito

    img_cinza = cv2.cvtColor(roi_gabarito, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_cinza, (5, 5), 0)
    img_thresh = cv2.threshold(img_blur, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    
    cv2.imwrite('debug_roi_preto_e_branco.jpg', img_thresh)

    cnts, _ = cv2.findContours(img_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bolhas_validas = []
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        aspect_ratio = w / float(h)
        
        if w >= 15 and h >= 15 and 0.9 <= aspect_ratio <= 1.1:
            bolhas_validas.append(c)
    
    if not bolhas_validas:
        print("AVISO: Nenhuma bolha válida foi encontrada na ROI.")
        return "", roi_gabarito 

    bolhas_validas = contours.sort_contours(bolhas_validas, method="left-to-right")[0]
    
    num_digitos = len(bolhas_validas) // 10
    if num_digitos == 0:
        print("AVISO: Não há bolhas suficientes para formar um dígito completo.")
        return "", roi_gabarito
        
    codigo_aluno = ""
    for i in range(num_digitos):
        coluna_cnts = contours.sort_contours(bolhas_validas[i * 10 : (i + 1) * 10], method="top-to-bottom")[0]
        maior_preenchimento = 0
        digito_marcado = -1
        
        for j, c in enumerate(coluna_cnts):
            mask = np.zeros(img_thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            mask = cv2.bitwise_and(img_thresh, img_thresh, mask=mask)
            total_pixels_brancos = cv2.countNonZero(mask)
            if total_pixels_brancos > maior_preenchimento:
                maior_preenchimento = total_pixels_brancos
                digito_marcado = j

        if digito_marcado != -1:
            codigo_aluno += str(digito_marcado)
            (x, y, w, h) = cv2.boundingRect(coluna_cnts[digito_marcado])
            cv2.circle(roi_gabarito, (x + w//2, y + h//2), int(w*0.6), (0, 255, 0), 2)
            
    return codigo_aluno, roi_gabarito


def extrair_codigo_aluno_automatico(caminho_imagem):
    try:
        imagem_original = cv2.imread(caminho_imagem)
        if imagem_original is None:
            print(f"ERRO: Não foi possível carregar a imagem: '{caminho_imagem}'")
            return None

        imagem_cinza = cv2.cvtColor(imagem_original, cv2.COLOR_BGR2GRAY)
        _, imagem_binaria = cv2.threshold(imagem_cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        dados = pytesseract.image_to_data(imagem_binaria, output_type=pytesseract.Output.DICT, lang='por')
        
        anchor_box = None
        for i in range(len(dados['level'])):
            if int(dados['conf'][i]) > 60 and 'Assinatura' in dados['text'][i]:
                x_ancora, y_ancora, _, _ = dados['left'][i], dados['top'][i], dados['width'][i], dados['height'][i]
                anchor_box = (x_ancora, y_ancora)
                print(f"✅ Âncora 'Assinatura' encontrada em: x={x_ancora}, y={y_ancora}")
                break

        if anchor_box is None:
            print("ERRO: Âncora 'Assinatura' não encontrada. Verifique a qualidade da imagem ou o texto.")
            return None

        x_ancora, y_ancora = anchor_box

        
        
        offset_y = 70
        offset_x = 30
        roi_height = 300
        roi_width = 100        
        y_roi_start = y_ancora + offset_y
        y_roi_end = y_roi_start + roi_height
        x_roi_start = x_ancora + offset_x
        x_roi_end = x_roi_start + roi_width

        h_img, w_img, _ = imagem_original.shape
        print("\n--- Depuração da ROI ---")
        print(f"Dimensões da Imagem: Largura={w_img}, Altura={h_img}")
        print(f"ROI Calculada: x=[{x_roi_start}:{x_roi_end}], y=[{y_roi_start}:{y_roi_end}]")

        if x_roi_start < 0 or y_roi_start < 0 or x_roi_end > w_img or y_roi_end > h_img:
            print("ERRO CRÍTICO: As coordenadas da ROI estão fora dos limites da imagem.")
            print("▶️ Ação: Ajuste os valores de offset_y, offset_x, roi_height e roi_width.")
            return None
        
        print("Coordenadas da ROI são válidas. Analisando bolhas...")
        
        roi_para_analise = imagem_original[y_roi_start:y_roi_end, x_roi_start:x_roi_end]
        codigo_limpo, roi_com_deteccoes = detectar_codigo_por_bolhas(roi_para_analise)

        imagem_original[y_roi_start:y_roi_end, x_roi_start:x_roi_end] = roi_com_deteccoes
        
        cv2.rectangle(imagem_original, (x_roi_start, y_roi_start), (x_roi_end, y_roi_end), (0, 0, 255), 2)
        cv2.imwrite('resultado_deteccao_bolhas.jpg', imagem_original)
        
        print("\n--- RESULTADO ---")
        print(f"Código do Aluno por Bolhas: {codigo_limpo if codigo_limpo else 'Nenhum código detectado.'}")
        print("\n📝 Imagem 'resultado_deteccao_bolhas.jpg' salva com as detecções.")
        
        return codigo_limpo

    except Exception as e:
        print(f"ERRO GERAL INESPERADO: {e}")
        return None


if __name__ == '__main__':
    caminho_da_prova = 'backend/prova.jpg' 
    extrair_codigo_aluno_automatico(caminho_da_prova)