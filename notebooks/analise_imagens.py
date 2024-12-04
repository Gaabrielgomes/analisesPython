import os
import tkinter
import json
import google.generativeai as genai
from dotenv import load_dotenv
import PIL.Image

# Carregar variáveis de ambiente
dotenv_path = r'C:\Users\Gabriel\Desktop\analises_escritorio\.env'
load_dotenv(dotenv_path=dotenv_path)

# Configuração da API
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Erro ao configurar a API: {e}")
    exit()

# Configurações de segurança para a API
safety_settings = [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "HIGH"}]
model = genai.GenerativeModel(model_name="gemini-1.5-flash", safety_settings=safety_settings)

# Carregar prompts do arquivo JSON
try:
    with open('../prompt_cases.json', 'r', encoding='utf-8') as file:
        prompts = json.load(file)
except Exception as Error:
    print(f"Error loading 'prompt_cases.json': {Error}")
    exit()

# Diretórios de imagens
images_directory = r'C:\Users\Gabriel\Desktop\analises_escritorio\import\images'
resized_directory = r'C:\Users\Gabriel\Desktop\analises_escritorio\import\resized_images'


# Criar diretório de imagens redimensionadas se não existir
os.makedirs(resized_directory, exist_ok=True)

for archive in os.listdir(resized_directory):
    os.remove(os.path.join(resized_directory, archive))

root = tkinter.Tk()
screen_width = root.winfo_width()
screen_height = root.winfo_height()
root.destroy()

# Inicializar variáveis
extracted_info = {
    'self': {
        'name': "",
        'cpf': "",
        'birth': "",
        'rg': "",
        'passport_number': "",
        'gender': "",
        'passport_authority': "",
        'issuance_date': "",
        'expiration_date': "",
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
    }
}
extracted_info.clear()

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
            case _ if any(keyword in image_name_lower for keyword in ["certidão", "certidao"]) and any(
                keyword in image_name_lower for keyword in ["filho", "filha"]):
                prompt = prompts["children"]["child_birth_certificate"]
                cases = 10
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
                    extracted_info['self']['cpf'] = lines[1].replace("CPF: ", "").strip() if len(lines) > 1 else ""
                    extracted_info['self']['birth'] = lines[2].replace("Birth: ", "").strip() if len(lines) > 2 else ""

                case _ if cases == 2:
                    extracted_info['self']['rg'] = lines[0].replace("RG: ", "").strip() if len(lines) > 0 else ""

                case _ if cases == 3:
                    extracted_info['self']['passport_number'] = lines[0].replace("Passport: ", "").strip() if len(lines) > 0 else ""
                    extracted_info['self']['gender'] = lines[1].replace("Gender: ", "").strip() if len(lines) > 1 else ""
                    extracted_info['self']['passport_authority'] = lines[2].replace("Authority: ", "").strip() if len(lines) > 2 else ""
                    extracted_info['self']['issuance_date'] = lines[3].replace("Issuance Date: ", "").strip() if len(lines) > 3 else ""
                    extracted_info['self']['expiration_date'] = lines[4].replace("Expiration Date: ", "").strip() if len(lines) > 4 else ""

                case _ if cases == 4:
                    extracted_info['self']['e_social'] = lines[0].replace("E-SOCIAL: ", "").strip() if len(lines) > 0 else ""

                case _ if cases == 5:
                    extracted_info['self']['electoral_zone'] = lines[0].replace("Zone: ", "").strip() if len(lines) > 0 else ""
                    extracted_info['self']['electoral_section'] = lines[1].replace("Section: ", "").strip() if len(lines) > 1 else ""
                    extracted_info['self']['electoral_title'] = lines[2].replace("Voter Registration: ", "").strip() if len(lines) > 2 else ""

                case _ if cases == 6:
                    extracted_info['self']['ethnicity'] = lines[0].replace("Race/ethnicity: ", "").strip() if len(lines) > 0 else ""

                case _ if cases == 7:
                    extracted_info['self']['address'] = lines[0].replace("Address: ", "").strip() if len(lines) > 0 else ""
                    extracted_info['self']['postal_code'] = lines[1].replace("Postal Code Number: ", "").strip() if len(lines) > 1 else ""

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

                case _ if cases == 0:
                    print("Não foi possível identificar a imagem ou obter dados da imagem analisada.")

    except (IOError, PIL.UnidentifiedImageError) as e:
        print(f"Error opening image {image_path}: {e}")
        continue


if extracted_info:
    missing_info = []
    print("\n" + "~" * 23)
    print("Extracted informations:")
    print("~" * 50)
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
    print("~" * 50)

    if missing_info:
        print("\n" + "-" * 20)
        print("Missing information:")
        print("-" * 30)
        for info in missing_info:
            print(info)
        print("-" * 30)

else:
    print("No informations could be extracted...")
