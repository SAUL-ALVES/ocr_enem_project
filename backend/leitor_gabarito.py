# -*- coding: utf-8 -*-
import cv2
import pytesseract
import numpy as np
from imutils import contours
import unicodedata
import os


try:
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    pytesseract.get_tesseract_version()
except Exception as e:
    print(
        "ERRO: Tesseract não encontrado. Verifique o caminho na variável 'pytesseract.pytesseract.tesseract_cmd'."
    )
    exit()


def processar_bloco_respostas(roi_bloco, questao_inicial, imagem_para_desenhar):
    """
    Analisa uma ROI, detecta as respostas marcadas e as retorna em um dicionário.
    *** VERSÃO CORRIGIDA: Usa intensidade média em escala de cinza para robustez. ***
    """
    LIMIAR_DE_PREENCHIMENTO = 90.0

    gabarito_parcial = {}
    if roi_bloco is None or roi_bloco.size < 200:
        print(f"Aviso: ROI para questão inicial {questao_inicial} inválida. Pulando.")
        return {}

    img_cinza = cv2.cvtColor(roi_bloco, cv2.COLOR_BGR2GRAY)

    img_blur_thresh = cv2.GaussianBlur(img_cinza, (5, 5), 0)
    img_thresh = cv2.adaptiveThreshold(
        img_blur_thresh,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        15,
        4,
    )

    img_cinza_invertida = cv2.bitwise_not(img_cinza)

    cnts, _ = cv2.findContours(
        img_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    bolhas_validas = []
    MIN_BUBBLE_DIAMETER = int(roi_bloco.shape[1] * 0.1)
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        aspect_ratio = w / float(h)
        if (
            w >= MIN_BUBBLE_DIAMETER
            and h >= MIN_BUBBLE_DIAMETER
            and 0.8 <= aspect_ratio <= 1.2
        ):
            bolhas_validas.append(c)

    if len(bolhas_validas) < 5:
        return {}

    bolhas_validas = contours.sort_contours(bolhas_validas, method="top-to-bottom")[0]

    mapa_respostas = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}

    LIMIAR_DE_PREENCHimento = 90.0

    for i in range(0, len(bolhas_validas), 5):
        grupo_atual = bolhas_validas[i : i + 5]
        if len(grupo_atual) != 5:
            continue
        grupo_atual = contours.sort_contours(grupo_atual, method="left-to-right")[0]

        medias_intensidade = []
        for c in grupo_atual:

            mask = np.zeros(img_cinza.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)

            pixels_da_bolha = cv2.bitwise_and(
                img_cinza_invertida, img_cinza_invertida, mask=mask
            )

            media = np.mean(pixels_da_bolha[mask > 0])
            medias_intensidade.append(media)

        indice_marcado = np.argmax(medias_intensidade)
        maior_intensidade = medias_intensidade[indice_marcado]
        numero_questao_atual = questao_inicial + (i // 5)
        resposta_marcada = "X"

        if maior_intensidade > LIMIAR_DE_PREENCHIMENTO:
            resposta_marcada = mapa_respostas[indice_marcado]
            (x, y, w, h) = cv2.boundingRect(grupo_atual[indice_marcado])
            cv2.circle(
                imagem_para_desenhar,
                (x + w // 2, y + h // 2),
                int(w * 0.6),
                (0, 255, 0),
                2,
            )

        gabarito_parcial[numero_questao_atual] = resposta_marcada
    return gabarito_parcial


def extrair_respostas_gabarito(caminho_imagem):
    """
    Função principal que orquestra a leitura completa do gabarito.
    *** VERSÃO SEM REDIMENSIONAMENTO FIXO: Coordenadas são escaladas dinamicamente ***
    """
    imagem_original = cv2.imread(caminho_imagem)
    if imagem_original is None:
        print(f"ERRO: Não foi possível carregar a imagem: '{caminho_imagem}'")
        return None

    
    imagem = imagem_original.copy()
    imagem_resultado = imagem.copy()
    
    altura_real, largura_real, _ = imagem.shape
    print(f"Tratando imagem original com tamanho: {largura_real}x{altura_real}")

    # --- BASE DE CÁLCULO PARA AS COORDENADAS ---
    
    LARGURA_REF = 750
    ALTURA_REF = 898

    
    fator_escala_x = largura_real / LARGURA_REF
    fator_escala_y = altura_real / ALTURA_REF

    
    print("Procurando âncora 'Simulado'...")
    img_cinza_ocr = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    dados = pytesseract.image_to_data(
        img_cinza_ocr, output_type=pytesseract.Output.DICT, lang="por"
    )

    ancora_x, ancora_y = None, None
    for i, palavra in enumerate(dados["text"]):
        palavra_limpa = (
            unicodedata.normalize("NFKD", palavra)
            .encode("ascii", "ignore")
            .decode("utf-8")
            .lower()
        )
        if "simulado" in palavra_limpa and dados["conf"][i] > 50:
            ancora_x = dados["left"][i]
            ancora_y = dados["top"][i]
            print(f"✅ Âncora 'Simulado' encontrada em (x={ancora_x}, y={ancora_y})")
            cv2.rectangle(
                imagem_resultado,
                (ancora_x, ancora_y),
                (ancora_x + dados["width"][i], ancora_y + dados["height"][i]),
                (0, 0, 255),
                2,
            )
            break

    if ancora_x is None:
        print(
            "ERRO CRÍTICO: Âncora 'Simulado' não encontrada na imagem. Não é possível continuar."
        )
        return None

    # --- CONFIGURAÇÃO DOS DESLOCAMENTOS (OFFSETS) ---
    
    
    bloco_1 = {"x": -50, "y": 110, "largura": 100, "altura": 500}
    bloco_2 = {"x": 75, "y": 110, "largura": 100, "altura": 250}
    bloco_3 = {"x": 190, "y": 110, "largura": 100, "altura": 500}
    bloco_4 = {"x": 300, "y": 110, "largura": 100, "altura": 250}

    todos_blocos = [
        {"config": bloco_1, "questao_inicial": 1, "label": "Bloco 1 (Questões 1-30)"},
        {"config": bloco_2, "questao_inicial": 31, "label": "Bloco 2 (Questões 31-45)"},
        {"config": bloco_3, "questao_inicial": 46, "label": "Bloco 3 (Questões 46-75)"},
        {"config": bloco_4, "questao_inicial": 76, "label": "Bloco 4 (Questões 76-90)"},
    ]

    gabarito_final = {}

    for bloco in todos_blocos:
        print(f"Processando {bloco['label']}...")
        conf = bloco["config"]

        
        offset_x_escalado = int(conf["x"] * fator_escala_x)
        offset_y_escalado = int(conf["y"] * fator_escala_y)
        w_escalado = int(conf["largura"] * fator_escala_x)
        h_escalado = int(conf["altura"] * fator_escala_y)

       
        x_abs = ancora_x + offset_x_escalado
        y_abs = ancora_y + offset_y_escalado
        
        
        x_abs = max(0, x_abs)
        y_abs = max(0, y_abs)
        w = min(w_escalado, largura_real - x_abs)
        h = min(h_escalado, altura_real - y_abs)

        roi_recortada = imagem[y_abs : y_abs + h, x_abs : x_abs + w]
        roi_para_desenhar = imagem_resultado[y_abs : y_abs + h, x_abs : x_abs + w]

        respostas_parciais = processar_bloco_respostas(
            roi_recortada, bloco["questao_inicial"], roi_para_desenhar
        )
        gabarito_final.update(respostas_parciais)
        cv2.rectangle(
            imagem_resultado, (x_abs, y_abs), (x_abs + w, y_abs + h), (255, 0, 0), 3
        )

    
    print("\n\n--- GABARITO EXTRAÍDO COM SUCESSO ---")
    
    for i in range(30):
        linha_str = ""
        if (i + 1) in gabarito_final:
            linha_str += f"Q{i+1:02d}: {gabarito_final[i+1]}   \t"
        else:
            linha_str += " " * 10 + "\t"
        if (i + 31) in gabarito_final:
            linha_str += f"Q{i+31:02d}: {gabarito_final[i+31]}   \t"
        else:
            linha_str += " " * 10 + "\t"
        if (i + 46) in gabarito_final:
            linha_str += f"Q{i+46:02d}: {gabarito_final[i+46]}   \t"
        else:
            linha_str += " " * 10 + "\t"
        if (i + 76) in gabarito_final:
            linha_str += f"Q{i+76:02d}: {gabarito_final[i+76]}"
        print(linha_str)

    cv2.imwrite("gabarito_resultado_visual.jpg", imagem_resultado)
    print("\n📝 Imagem 'gabarito_resultado_visual.jpg' salva com as detecções.")
    return gabarito_final


if __name__ == "__main__":
    
    diretorio_do_script = os.path.dirname(os.path.abspath(__file__))
    nome_do_arquivo = "prova5.png"
    caminho_do_gabarito = os.path.join(diretorio_do_script, nome_do_arquivo)
   

    extrair_respostas_gabarito(caminho_do_gabarito)
