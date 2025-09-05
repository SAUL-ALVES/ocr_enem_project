import cv2
import numpy as np
import pytesseract
import re
from typing import Dict, List, Optional
import os

# ========== CONFIGURAÇÃO DO TESSERACT ==========
TESSERACT_PATH = r"C:\Arquivos De Programas\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# ========== CONFIGURAÇÃO DAS REGIÕES ==========
REGIOES_CONFIG = {
    'nome': {'x1': 55, 'y1': 173, 'x2': 860, 'y2': 245},
    'codigo': {'x1': 115, 'y1': 280, 'x2': 205, 'y2': 495},
    'respostas': {'x1': 270, 'y1': 270, 'x2': 830, 'y2': 865},
}

class OCRGabaritoENEM:
    def __init__(self):
        self.config = {
            'total_questoes': 90,
            'alternativas': ['A', 'B', 'C', 'D', 'E'],
            'questoes_por_linha': 5,
        }
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Pré-processamento mais agressivo para remover quadrados"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Filtro para suavizar e remover ruído
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        
        # Binarização adaptativa para lidar com variações de iluminação
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 11, 2)
        
        # Operação morfológica para remover linhas finas (quadrados)
        kernel = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        return cleaned
    
    def extrair_nome_aluno(self, image: np.ndarray) -> str:
        """Extrai o nome do aluno - versão melhorada"""
        coord = REGIOES_CONFIG['nome']
        regiao_nome = image[coord['y1']:coord['y2'], coord['x1']:coord['x2']]
        
        # Pré-processamento específico para texto
        regiao_nome = cv2.GaussianBlur(regiao_nome, (3, 3), 0)
        _, regiao_nome = cv2.threshold(regiao_nome, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        cv2.imwrite("resultados/regiao_nome_processada.jpg", regiao_nome)
        
        try:
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
            nome = pytesseract.image_to_string(regiao_nome, config=custom_config)
            nome = re.sub(r'[^A-Za-z\s]', '', nome).strip()
            return nome if nome else "NOME_NAO_IDENTIFICADO"
        except:
            return "NOME_NAO_IDENTIFICADO"
    
    def extrair_codigo_aluno(self, image: np.ndarray) -> str:
        """Extrai código do aluno - foca apenas nas bolinhas"""
        coord = REGIOES_CONFIG['codigo']
        regiao_codigo = image[coord['y1']:coord['y2'], coord['x1']:coord['x2']]
        
        # Salvar região original para debug
        cv2.imwrite("resultados/regiao_codigo_original.jpg", regiao_codigo)
        
        # Pré-processamento para destacar bolinhas
        regiao_codigo = cv2.GaussianBlur(regiao_codigo, (5, 5), 0)
        _, regiao_codigo = cv2.threshold(regiao_codigo, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        cv2.imwrite("resultados/regiao_codigo_processada.jpg", regiao_codigo)
        
        # Procurar contornos em vez de círculos (mais robusto)
        contornos, _ = cv2.findContours(regiao_codigo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        codigo = ""
        bolinhas_info = []
        
        for i, contorno in enumerate(contornos[:10]):  # Máximo 10 dígitos
            area = cv2.contourArea(contorno)
            if 20 < area < 200:  # Filtro de tamanho para bolinhas
                x, y, w, h = cv2.boundingRect(contorno)
                
                # Calcular centro
                centro_x = x + w // 2
                centro_y = y + h // 2
                
                # Extrair ROI da bolinha
                roi = regiao_codigo[y:y+h, x:x+w]
                intensidade = np.mean(roi)
                
                # Considerar como marcada se tiver alta intensidade (já que está invertido)
                marcada = intensidade > 100
                
                if marcada:
                    codigo += str(i)
                
                bolinhas_info.append({
                    'digito': i,
                    'posicao': (centro_x, centro_y),
                    'marcada': marcada,
                    'area': area,
                    'intensidade': intensidade
                })
        
        # Ordenar bolinhas por posição vertical
        bolinhas_info.sort(key=lambda x: x['posicao'][1])
        codigo_ordenado = ''.join([str(b['digito']) for b in bolinhas_info if b['marcada']])
        
        return codigo_ordenado.zfill(2), bolinhas_info
    
    def extrair_respostas(self, image: np.ndarray) -> Dict[int, str]:
        """Extrai respostas - método completamente revisado"""
        coord = REGIOES_CONFIG['respostas']
        regiao_respostas = image[coord['y1']:coord['y2'], coord['x1']:coord['x2']]
        
        # Salvar região original
        cv2.imwrite("resultados/regiao_respostas_original.jpg", regiao_respostas)
        
        # Pré-processamento agressivo para remover quadrados
        regiao_processada = cv2.GaussianBlur(regiao_respostas, (5, 5), 0)
        _, regiao_processada = cv2.threshold(regiao_processada, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Operação morfológica para remover linhas (quadrados)
        kernel = np.ones((2, 2), np.uint8)
        regiao_processada = cv2.morphologyEx(regiao_processada, cv2.MORPH_OPEN, kernel)
        
        cv2.imwrite("resultados/regiao_respostas_processada.jpg", regiao_processada)
        
        respostas = {}
        h, w = regiao_processada.shape
        
        # Procurar todos os contornos (bolinhas)
        contornos, _ = cv2.findContours(regiao_processada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar apenas contornos que parecem bolinhas
        bolinhas = []
        for contorno in contornos:
            area = cv2.contourArea(contorno)
            if 10 < area < 100:  # Área típica de bolinhas
                x, y, w, h = cv2.boundingRect(contorno)
                bolinhas.append((x + w//2, y + h//2, area))  # (centro_x, centro_y, área)
        
        print(f"🔍 Encontradas {len(bolinhas)} bolinhas potenciais")
        
        # Agrupar bolinhas por questão
        for questao in range(1, self.config['total_questoes'] + 1):
            # Calcular posição aproximada da questão
            linha = (questao - 1) // self.config['questoes_por_linha']
            coluna = (questao - 1) % self.config['questoes_por_linha']
            
            # Calcular região aproximada da questão
            questao_x = coluna * (w // 5) + (w // 10)
            questao_y = linha * (h // 18) + (h // 36)
            
            # Procurar bolinhas próximas a esta posição
            bolinhas_questao = []
            for bx, by, area in bolinhas:
                dist_x = abs(bx - questao_x)
                dist_y = abs(by - questao_y)
                
                if dist_x < (w // 10) and dist_y < (h // 36):
                    # Calcular qual alternativa (A-E) baseado na posição X
                    pos_relativa = (bx - (questao_x - w//10)) / (w//5)
                    alternativa_idx = int(pos_relativa * 5)
                    alternativa_idx = max(0, min(4, alternativa_idx))  # Clamp entre 0-4
                    
                    bolinhas_questao.append((alternativa_idx, area))
            
            # Se encontrou bolinhas, verificar qual está marcada
            if bolinhas_questao:
                # Assumir que a maior área é a marcada (mais preenchida)
                alternativa_idx, _ = max(bolinhas_questao, key=lambda x: x[1])
                respostas[questao] = self.config['alternativas'][alternativa_idx]
            else:
                respostas[questao] = None
        
        return respostas
    
    def processar_gabarito(self, image: np.ndarray) -> Dict:
        """Processa o gabarito"""
        try:
            processed_image = self.preprocess_image(image)
            cv2.imwrite("resultados/imagem_preprocessada.jpg", processed_image)
            
            nome = self.extrair_nome_aluno(processed_image)
            codigo, bolinhas_info = self.extrair_codigo_aluno(processed_image)
            respostas = self.extrair_respostas(processed_image)
            
            respostas_validas = {k: v for k, v in respostas.items() if v is not None}
            
            return {
                'nome': nome,
                'codigo': codigo,
                'total_respostas_detectadas': len(respostas_validas),
                'respostas': respostas_validas,
                'bolinhas_codigo': bolinhas_info,
                'sucesso': True,
                'erro': None
            }
            
        except Exception as e:
            import traceback
            return {
                'nome': '',
                'codigo': '',
                'respostas': {},
                'sucesso': False,
                'erro': f"{str(e)}\n{traceback.format_exc()}"
            }