import os
import pyautogui
import time
import psutil
from images_analysis import extracted_info, missing_info

def single_process_cpu_usage(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                process = psutil.Process(proc.info['pid'])
                cpu_usage = process.cpu_percent(interval=0.1)
                return cpu_usage
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return -1

def system_ready():
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory_usage = psutil.virtual_memory().percent
    print(f"CPU Usage: {cpu_usage}% // Memory usage: {memory_usage}")
    return cpu_usage < 70 and memory_usage < 70

def sys_processes_ok():
    while not single_process_cpu_usage("name_of_the_process") < 3 or not system_ready():
        time.sleep(0.5)

def wait_and_press(key, times=1):
    sys_processes_ok()
    pyautogui.press(key, presses=times)

def wait_and_typewrite(text, interval=0.03):
    sys_processes_ok()
    pyautogui.typewrite(text, interval=interval)

def find_image(guidance_image_name):
    while True:
        try:
            sys_processes_ok()
            pyautogui.locateOnScreen(image=(os.path.join(guidance_images_dir, guidance_image_name)), confidence=0.8)
            print(f"Imagem encontrada em '{pyautogui.position()}'.")
            break
        except pyautogui.ImageNotFoundException:
            print(f"Aguardando a imagem '{guidance_image_name}' ser encontrada...")
            time.sleep(1)

def find_and_dragTo(guidance_image_name):
    counter = 0
    while True:
        try:
            sys_processes_ok()
            if (guidance_image_name == "new_employee.png") and counter > 5:
                pyautogui.dragTo(pyautogui.locateOnScreen(image=(os.path.join(guidance_images_dir, "new_employee_dotted.png")), confidence=0.8))
            else:
                pyautogui.dragTo(pyautogui.locateOnScreen(image=(os.path.join(guidance_images_dir, guidance_image_name)), confidence=0.8))
            print(f"Imagem encontrada em '{pyautogui.position()}'.")
            time.sleep(1)
            pyautogui.click()
            break
        except pyautogui.ImageNotFoundException:
            counter += 1
            print(f"Aguardando a imagem '{guidance_image_name}' ser encontrada...")
            time.sleep(1)

def click_and_write(person=str, info=str):
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.typewrite(extracted_info_sample[person][info])


guidance_images_dir = r'directory\of\images\to\guide\your\program\untill\it\starts\writing'

find_and_dragTo("employee_registration_command.png")
find_image("employee_registration.png")
find_and_dragTo("new_employee.png")
find_image("initial_page.png")

extracted_info_sample = {
    'self': {
        'name': "",
        'cpf': "",
        'birth': "",
        'rg': "",
        'nis_responsible': "",
        'nis_number': "",
        'passport_number': "",
        'gender': "",
        'passport_authority': "",
        'passport_issuance_date': "",
        'passport_expiration_date': "",
        'e_social': "",
        'electoral_zone': "",
        'electoral_section': "",
        'electoral_title': "",
        'ethnicity': "",
        'address': "",
        'postal_code': "",
        'father': "",
        'mother': "",
        'enterprise_name': "",
        'enterprise_cnpj': "",
        'enterprise_sector': "",
        'enterprise_function': ""
    },
    'child_1': {
        'name': "",
        'birth': "",
        'father': "",
        'mother': "",
        'NIS': ""
    },
    'child_2': {
        'name': "",
        'birth': "",
        'father': "",
        'mother': "",
        'NIS': ""
    }
}


# Self name
wait_and_press('tab', 2)
wait_and_typewrite(extracted_info_sample['self']['name'])
# Self CPF
wait_and_press('tab', 2)
wait_and_typewrite(extracted_info_sample['self']['cpf'])
# Self PIS/NIS
wait_and_press('tab')
wait_and_typewrite(extracted_info_sample['self']['nis_number'])
# Enterprise identification
wait_and_press('tab', 2)
wait_and_press('F2')
wait_and_press('Enter')
# Self enterprise function
wait_and_press('tab')
wait_and_press('F2')
wait_and_typewrite(extracted_info_sample['self']['enterprise_function'])
wait_and_press('Enter')
# Enterprise department
wait_and_press('tab', 2)
wait_and_press('F2')
wait_and_typewrite('G') # Change letter 'G' to the correct identification
wait_and_press('Enter')
# Center of cost
wait_and_press('tab')
wait_and_press('F2')
wait_and_typewrite('CENTRO DE CUSTO ')
wait_and_typewrite(extracted_info_sample['self']['enterprise_sector'])
wait_and_press('Enter')
# Sindicate
wait_and_press('tab')
wait_and_press('F2')
wait_and_typewrite('...') # Find a way to get the sindicate
wait_and_press('Enter')
# Employee admission date
wait_and_press('tab')
wait_and_typewrite('date') # Find a way to get the date od admission. Format: "DDMMYYYY"
wait_and_press('Enter')
# Contractual informations
wait_and_press('tab', 2)
    # Depending on the type of hire, loop 'for' to reach one of the positions listed
    # contract_category = []
    # wait_and_press('downarrow', contract_category[category])
    # wait_and_press('Enter')
    
    # Depending on the type of hire, loop 'for' to reach one of the positions listed
    # employment_relationship = []
    # wait_and_press('downarrow', employment_relationship[category])
    # wait_and_press('Enter')
