import pandas as pd
import os
import pyautogui
import time


time.sleep(3)
pyautogui.dragTo(x=180, y=90)
time.sleep(0.5)
pyautogui.click(x=180, y=90)
while True:
    try:
        pyautogui.locateOnScreen(image='images/cadastro_empregados.png', confidence=0.6)
        print("Janela aberta.")
        break
    except pyautogui.ImageNotFoundException:
        print("Aguardando a janela ser aberta...")
        time.sleep(1)
pyautogui.dragTo(x=350, y=690)
time.sleep(0.5)
pyautogui.click(x=350, y=690)