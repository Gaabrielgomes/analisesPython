import os
import re
import tkinter
import json
import google.generativeai as genai
from dotenv import load_dotenv
import PIL.Image
import requests
from difflib import SequenceMatcher


def get_address_by_zip(zip_code):
    zip_code = ''.join(filter(str.isdigit, zip_code))
    
    if len(zip_code) != 8:
        return None
    
    url = f"https://viacep.com.br/ws/{zip_code}/json/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "erro" in data:
            return None
        
        return {
            "street": data.get("logradouro", ""),
            "neighborhood": data.get("bairro", ""),
            "city": data.get("localidade", ""),
            "state": data.get("uf", "")
        }
    except requests.exceptions.RequestException:
        return None

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def correct_address_by_zip(zip_code, image_address, minimum_similarity=0.8, max_iterations=200):

    zip_code = ''.join(filter(str.isdigit, zip_code))
    
    iteration_count = 0

    while len(zip_code) == 8 and iteration_count < max_iterations:

        API_address = get_address_by_zip(zip_code)
        
        if API_address:

            API_address = f"{API_address['street']} {API_address['neighborhood']} {API_address['city']} {API_address['state']}".upper()
            image_address = image_address.upper()
            
            if similarity(API_address, image_address) >= minimum_similarity:
                return {
                    "correct_zip_code": zip_code,
                    "correct_address": API_address
                }
        
        print(f"Testing match zip code '{zip_code}'")
        zip_code = str(int(zip_code) + 1).zfill(8)
        iteration_count += 1
    
    return "Could not find a matching address."


# Load environment variables
dotenv_path = r'C:\Users\Gabriel\Desktop\analises_escritorio\.env'
load_dotenv(dotenv_path=dotenv_path)

# API configurations
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Erro ao configurar a API: {e}")
    exit()

# API safety config
safety_settings = [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "HIGH"}]
model = genai.GenerativeModel(model_name="gemini-1.5-flash", safety_settings=safety_settings)

try:
    with open('../prompt_cases.json', 'r', encoding='utf-8') as file:
        prompts = json.load(file)
except Exception as Error:
    print(f"Error loading 'prompt_cases.json': {Error}")
    exit()

# Images directories
images_directory = r'C:\Users\Gabriel\Desktop\analises_escritorio\import\images'
resized_directory = r'C:\Users\Gabriel\Desktop\analises_escritorio\import\resized_images'

# If resized_directory does not exist, create it
os.makedirs(resized_directory, exist_ok=True)

for archive in os.listdir(resized_directory):
    os.remove(os.path.join(resized_directory, archive))

root = tkinter.Tk()
screen_width = root.winfo_width()
screen_height = root.winfo_height()
root.destroy()

# Initial variables
extracted_info = {
    'self': {
        'name': "",
        'cpf': "",
        'birth': "",
        'rg': "",
        "nis_responsible": "",
        "nis_number": "",
        'nis_expedition': "",
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
        'enterprise_function': "",
        'work_card_number': "",
        'work_card_serie': "",
        'work_card_expedition': "",
        'work_card_federal_unity': "",
        'bank_agency': "",
        'bank_account': "",
        'bank_identification': "",
        'admission_date': "",
        'contract_category': "",
        'employment_relationship': "",
        'contract_duration': "",
        'contract_experience': "",
        'salary': "",
        'horary_type': "",
        'journey_type': "",
        'bus_card_number': "",
        'month_hours': "",
        'week_hours': "",
        'day_hours': "",
        'fgts_date': "",
        'fgts_account': "",
        'fgts_account_base': "",
        'payment_type': "",
        'syndicalized': "",
        'aso_date': "",
        'aso_type': "",
        'aso_result': "",
        'aso_expiration_date': "",
        'aso_doctor': "",
        'aso_responsible_doctor': "",
        'exam_date': "",
        'exam_code': "",
        'exam_order': "",
        'exam_results': ""
    }
}

for image_name in os.listdir(images_directory):

    if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
        print(f"Skipping unsupported file extension: {image_name}")
        continue

    image_path = os.path.join(images_directory, image_name)

    try:
        image = PIL.Image.open(image_path)

        if image.width > image.height:
            img_resize_size = (screen_width, screen_height)
        else:
            img_resize_size = (screen_height, screen_width)

        image.resize(size=img_resize_size, resample=PIL.Image.Resampling.LANCZOS)
        image.save(fp=(resized_directory + f"\\{image_name}"))

        image_resized_path = resized_directory + f"\\{image_name}"

        image_name_lower = image_name.lower()
        prompt = ""
        
        cases = 0
        match True:
            case _ if "cpf" in image_name_lower:
                prompt = prompts["self"]["cpf"]
                cases = 1

            case _ if "rg" in image_name_lower:
                prompt = prompts["self"]["rg"]
                cases = 2

            case _ if "passaporte" in image_name_lower:
                prompt = prompts["self"]["passport"]
                cases = 3

            case _ if "social" in image_name_lower:
                prompt = prompts["self"]["social"]
                cases = 4

            case _ if any(keyword in image_name_lower for keyword in ["titulo", "título"]):
                prompt = prompts["self"]["title"]
                cases = 5

            case _ if any(keyword in image_name_lower for keyword in ["étnico", "autodeclaração", "racial"]):
                prompt = prompts["self"]["ethnical"]
                cases = 6

            case _ if any(keyword in image_name_lower for keyword in ["resid", "residencia", "residência"]):
                prompt = prompts["self"]["address"]
                cases = 7

            case _ if any(keyword in image_name_lower for keyword in ["certidão", "certidao"]) and not any(
                keyword in image_name_lower for keyword in ["filho", "filha"]):
                prompt = prompts["self"]["birth"]
                cases = 8

            case _ if any(keyword in image_name_lower for keyword in ["aso", "admicional", "exame"]):
                prompt = prompts["self"]["admission"]
                cases = 9

            case _ if any(keyword in image_name_lower for keyword in ["nis", "pis"]):
                prompt = prompts["self"]["NIS"]
                cases = 10

            case _ if any(keyword in image_name_lower for keyword in ["banco", "bancario", "bancário", "conta"]):
                prompt = prompts["self"]["bank"]
                cases = 11

            case _ if any(keyword in image_name_lower for keyword in ["certidão", "certidao"]) and any(
                keyword in image_name_lower for keyword in ["filho", "filha"]):
                prompt = prompts["children"]["child_birth_certificate"]
                cases = 12
            case _:
                print(f"image: {image_resized_path} X (No prompt could be generated.)")
                continue

        print(f"image: {image_resized_path}", end="")

        response = ""
        if prompt != "":
            try:
                response = model.generate_content({
                    'role': 'user',
                    'parts': [genai.upload_file(image_resized_path, mime_type=f"image/{image.format}"), prompt]
                })
                print(" ✓")
            except Exception as error:
                print(f" X\nError: {error}")
                continue
        else:
            print(f" X (Response could not be generated.)")

        if response != "":
            text_content = response.text
            lines = text_content.splitlines()
            print(text_content)

            if 'self' not in extracted_info:
                extracted_info['self'] = {}
            
            match True:
                case _ if cases == 1:
                    extracted_info['self']['name'] = lines[0].replace("Name: ", "").strip() if len(lines) > 0 else ""
                    extracted_info['self']['cpf'] = re.sub(r"[.\-]", "", lines[1].replace("CPF: ", "").strip()) if len(lines) > 1 else ""
                    extracted_info['self']['birth'] = lines[2].replace("Birth: ", "").strip() if len(lines) > 2 else ""

                case _ if cases == 2:
                    extracted_info['self']['rg'] = lines[0].replace("RG: ", "").strip() if len(lines) > 0 else ""
                    if len(lines) > 1:
                        extracted_info['self']['cpf'] = re.sub(r"[.\-]", "", lines[1].replace("CPF: ", "").strip()) if len(lines) > 1 else ""

                case _ if cases == 3:
                    extracted_info['self']['passport_number'] = lines[0].replace("Passport: ", "").strip() if len(lines) > 0 else ""
                    extracted_info['self']['gender'] = lines[1].replace("Gender: ", "").strip() if len(lines) > 1 else ""
                    extracted_info['self']['passport_authority'] = lines[2].replace("Authority: ", "").strip() if len(lines) > 2 else ""
                    extracted_info['self']['passport_issuance_date'] = lines[3].replace("Issuance Date: ", "").strip() if len(lines) > 3 else ""
                    extracted_info['self']['passport_expiration_date'] = lines[4].replace("Expiration Date: ", "").strip() if len(lines) > 4 else ""

                case _ if cases == 4:
                    extracted_info['self']['e_social'] = lines[0].replace("E-SOCIAL: ", "").strip() if len(lines) > 0 else ""

                case _ if cases == 5:
                    extracted_info['self']['electoral_zone'] = lines[0].replace("Zone: ", "").strip() if len(lines) > 0 else ""
                    if len(extracted_info['self']['electoral_zone']) > 3:
                        extracted_info['self']['electoral_zone'] = extracted_info['self']['electoral_zone'][1:]
                    extracted_info['self']['electoral_section'] = lines[1].replace("Section: ", "").strip() if len(lines) > 1 else ""
                    extracted_info['self']['electoral_title'] = lines[2].replace("Voter Registration: ", "").strip() if len(lines) > 2 else ""

                case _ if cases == 6:
                    extracted_info['self']['ethnicity'] = lines[0].replace("Race/ethnicity: ", "").strip() if len(lines) > 0 else ""

                case _ if cases == 7:
                    extracted_info['self']['address'] = lines[0].replace("Address: ", "").strip() if len(lines) > 0 else ""
                    extracted_info['self']['zip_code'] = lines[1].replace("Zip Number: ", "").strip() if len(lines) > 1 else ""
                    result = correct_address_by_zip(extracted_info['self']['zip_code'], extracted_info['self']['address'])
                    extracted_info['self']['address'] = result["correct_address"]
                    extracted_info['self']['zip_code'] = result["correct_zip_code"]

                case _ if cases == 8:
                    extracted_info['self']['name'] = lines[0].replace("Name: ", "").strip() if len(lines) > 0 else ""
                    extracted_info['self']['birth'] = lines[1].replace("Birth: ", "").strip() if len(lines) > 1 else ""
                    extracted_info['self']['father'] = lines[2].replace("Father: ", "").strip() if len(lines) > 2 else ""
                    extracted_info['self']['mother'] = lines[3].replace("Mother: ", "").strip() if len(lines) > 3 else ""

                case _ if cases == 9:
                    extracted_info['self']['enterprise_name'] = lines[0].replace("Enterprise name: ", "").strip() if len(lines) > 0 else ""
                    extracted_info['self']['enterprise_cnpj'] = lines[1].replace("Enterprise CNPJ: ", "").strip() if len(lines) > 1 else ""
                    extracted_info['self']['enterprise_sector'] = lines[2].replace("Sector: ", "").strip() if len(lines) > 2 else ""
                    extracted_info['self']['enterprise_function'] = lines[3].replace("Function: ", "").strip() if len(lines) > 3 else ""

                case _ if cases == 10:
                    extracted_info['self']['nis_responsible'] = lines[0].replace("Responsible: ", "").strip() if len(lines) > 0 else ""
                    extracted_info['self']['nis_number'] = lines[1].replace("Responsible's NIS: ", "").strip() if len(lines) > 1 else ""
                    extracted_info['self']['nis_expedition'] = lines[2].replace("Date of expedition: ", "").strip() if len(lines) > 2 else ""
                    
                    index = 3
                    child_count = (len(lines) - 3) // 2

                    for i in range(1, child_count + 1):
                        child_key = f'child_{i}'
                        if child_key not in extracted_info:
                            extracted_info[child_key] = {}
                        extracted_info[child_key]['name'] = lines[index].replace("Name of dependent: ", "").strip() if index < len(lines) else ""
                        extracted_info[child_key]['NIS'] = lines[index + 1].replace("NIS of dependent: ", "").strip() if index + 1 < len(lines) else ""
                        index += 2

                case _ if cases == 11:
                    extracted_info['self']['bank_agency'] = lines[0].replace("Agency: ", "").strip() if len(lines) > 0 else ""
                    extracted_info['self']['bank_account'] = lines[1].replace("Account: ", "").strip() if len(lines) > 1 else ""
                    extracted_info['self']['bank_identification'] = lines[2].replace("Bank: ", "").strip() if len(lines) > 2 else ""

                case _ if cases == 12:
                    child_data = {
                        "name": lines[0].replace("Name: ", "").strip() if len(lines) > 0 else "",
                        "birth": lines[1].replace("Birth: ", "").strip() if len(lines) > 1 else "",
                        "father": lines[2].replace("Father: ", "").strip() if len(lines) > 2 else "",
                        "mother": lines[3].replace("Mother: ", "").strip() if len(lines) > 3 else ""
                    }

                    for i in range(1, 10):
                        child_key = f"child_{i}"
                        if child_key not in extracted_info:
                            extracted_info[child_key] = child_data
                            break
                        else:
                            if child_data['name'] == extracted_info[child_key]['name']:
                                extracted_info[child_key].items = child_data

                case _ if cases == 0:
                    print("Could not identify the image or obtain data from the analyzed image.")

    except (IOError, PIL.UnidentifiedImageError) as e:
        print(f"Error opening image {image_path}: {e}")
        continue

if extracted_info:
    missing_info = []
    print("\n" + "~" * 23)
    print("Extracted informations:")
    print("~" * 100)
    for key, value in extracted_info.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                if sub_value == "":
                    missing_info.append(f"{key}: '{sub_key}'") 
                else:
                    print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")
    print("~" * 100)

    if missing_info:
        print("\n" + "-" * 20)
        print("Missing information:")
        print("-" * 35)
        for info in missing_info:
            print(info)
        print("-" * 35)

else:
    print("No informations could be extracted...")
