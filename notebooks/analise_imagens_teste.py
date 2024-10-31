import cv2
import numpy as np
import os
import pytesseract

# Configurar o caminho do Tesseract se necessário
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Gabriel\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
imgFolder = r'C:\Users\Gabriel\Desktop\.vscode\projetosPessoais\analises_escritorio\scripts\images'
# Carregar a imagem
for img in os.listdir(imgFolder):
    image_path = os.path.join(imgFolder, img)
    image = cv2.imread(image_path)

    # Converter a imagem para escala de cinza
    imagem_cinza = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplicar um filtro de nitidez
    kernel = np.array([[0, -1, 0],
                    [-1, 5, -1],
                    [0, -1, 0]])
    sharpened_image = cv2.filter2D(imagem_cinza, -1, kernel)

    # Usar pytesseract para extrair texto
    dado = pytesseract.image_to_data(sharpened_image, output_type=pytesseract.Output.DICT)

    # Processando as palavras detectadas
    for i in range(len(dado['text'])):
        if int(dado['conf'][i]) > 0:  # Apenas palavras com uma confiança razoável
            texto = dado['text'][i]
            left = dado['left'][i]
            top = dado['top'][i]
            largura = dado['width'][i]
            altura = dado['height'][i]

            # Imprimir o texto e suas coordenadas
            print(f'Texto: {texto}, Coordenadas: ({left}, {top}), Largura: {largura}, Altura: {altura}')

    # Mostrar a imagem (opcional)
    cv2.imshow('Imagem Nitida', sharpened_image)
    cv2.waitKey(0)
