import cv2
import pytesseract as pytesseract
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Gabriel\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Carregar a imagem
imagem = cv2.imread(r'C:\Users\Gabriel\Desktop\.vscode\projetosPessoais\analises_escritorio\scripts\images\NATHALYA-TITULO DE ELEITOR.jpeg')

# Converter para escala de cinza
imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

# Aplicar limiarização para destacar o texto
_, imagem_binaria = cv2.threshold(imagem_cinza, 150, 255, cv2.THRESH_BINARY)

cv2.imshow("Imagem Processada", imagem_binaria)
cv2.waitKey(0)

# Usando o pytesseract para extrair textos e suas posições
dado = pytesseract.image_to_data(imagem_binaria, output_type=pytesseract.Output.DICT)

# Inicializando variáveis
cpf = ""
nome = ""
nomeIdentif = False
nascIdentif = False

# Processando as palavras detectadas
for i in range(len(dado['text'])):
    if int(dado['conf'][i]) > 0:  # Apenas palavras com uma confiança razoável
        texto = dado['text'][i]
        left = dado['left'][i]
        top = dado['top'][i]
        print(texto, left, top)
        
        # Agrupando "CPF" com o número do CPF
        if len(texto) == 14:
            cpf = texto  # "CPF" e o próximo texto devem ser o número de CPF
        
        # Agrupando o nome completo
        if "Nome" in texto:
            nomeIdentif = True

        if nomeIdentif:
            if "Nascimento" in texto:
                dataNasc = dado['text'][i + 2]
                break
            elif "Nome" in texto:
                continue
            else:
                if nome == "":
                    nome = texto
                else:
                    nome += " " + texto

# Exibindo os resultados
print(f"CPF: {cpf}")
print(f"Nome: {nome}")
print(f"Data de nascimento: {dataNasc}")
