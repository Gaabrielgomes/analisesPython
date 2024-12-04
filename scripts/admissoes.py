import pandas as pd
import os
import pyautogui
import time

guidance_images_dir = r'C:\Users\Gabriel\Desktop\analises_escritorio\import\guidance_images'

time.sleep(3)
pyautogui.dragTo(x=180, y=90)
time.sleep(0.5)
pyautogui.click(x=180, y=90)
while True:
    try:
        pyautogui.locateOnScreen(image=(os.path.join(guidance_images_dir, "cadastro_empregados.png")), confidence=0.6)
        print("Janela aberta.")
        break
    except pyautogui.ImageNotFoundException:
        print("Aguardando a janela ser aberta...")
        time.sleep(1)
pyautogui.dragTo(x=350, y=690)
time.sleep(0.5)
pyautogui.click(x=350, y=690)
