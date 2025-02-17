from flask import Flask, request
import pandas as pd
import os
import requests
import base64
from dotenv import load_dotenv

# Charger les variables d'environnement depuis un fichier .env
load_dotenv()

github_token = os.getenv("GITHUB_TOKEN")

# Fonction de conversion Excel vers JSON
def convert_excel_to_json(file_path, output_json_path):
    excel_data = pd.ExcelFile(file_path)
    df = excel_data.parse(excel_data.sheet_names[0])
    df.columns = df.columns.str.strip()

    # Exemple de groupes de colonnes à concaténer
    column_groups = {
        "Competence": ['Compétence / responsabilité'],
        "EntiteFocus": ['Entité(s) en focus (contexte)'],
        # Ajouter d'autres groupes selon ton script
    }

    for new_column, columns in column_groups.items():
        df[new_column] = df[columns].apply(lambda x: ' - '.join(x.dropna().astype(str)), axis=1)

    columns_to_drop = sum(column_groups.values(), [])
    df_cleaned = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    json_data = df_cleaned.to_json(orient='records', lines=False, force_ascii=False)

    with open(output_json_path, 'w', encoding='utf-8') as f:
        f.write(json_data)

# Fonction pour envoyer le fichier JSON sur GitHub
def upload_to_github(json_file_path, github_repo, github_token, path_in_repo):
    # Lire le fichier JSON et le convertir en base64
    with open(json_file_path, 'rb') as file:
        content = base64.b64encode(file.read()).decode()

    # URL pour l'API GitHub
    api_url = f"https://github.com/Seb19861986/competences_locales/blob/main/DataTest.json"

    # Préparer les données pour l'API
    data = {
        "message": "Mise à jour du fichier JSON",
        "content": content,
        "branch": "main"  # Si tu utilises une branche différente, remplace "main" par le nom de ta branche
    }

    # Faire la requête PUT à l'API GitHub
    response = requests.put(
        api_url,
        json=data,
        headers={"Authorization": f"token {github_token}"}
    )

    if response.status_code == 201:
        return "Le fichier a été téléchargé avec succès sur GitHub."
    else:
        return f"Erreur lors du téléchargement sur GitHub: {response.json()}"

@app.route('/')
def upload_form():
    return '''
        <html><body>
        <h2>Upload Excel File</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" />
            <input type="submit" value="Upload File" />
        </form>
        </body></html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and file.filename.endswith('.xlsx'):
        try:
            # Créer le dossier uploads si nécessaire
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            
            # Sauvegarder le fichier temporairement
            temp_file_path = os.path.join('uploads', file.filename)
            file.save(temp_file_path)

            # Convertir le fichier Excel en JSON
            output_json_path = os.path.join('uploads', file.filename.replace('.xlsx', '.json'))
            convert_excel_to_json(temp_file_path, output_json_path)

            # Configuration de GitHub
            github_repo = "Seb19861986/competences_locales"  # Remplace par ton utilisateur et ton dépôt
            github_token = os.getenv("GITHUB_TOKEN")  # Assure-toi que le token est dans un fichier .env
            path_in_repo = "DataTest.json"  # Remplace par le chemin du fichier dans le dépôt

            # Appeler la fonction pour envoyer le fichier JSON sur GitHub
            upload_status = upload_to_github(output_json_path, github_repo, github_token, path_in_repo)

            return upload_status
        except Exception as e:
            return f"Une erreur est survenue: {str(e)}", 500
    return "Invalid file format. Please upload an Excel file.", 400

if __name__ == "__main__":
    # Utiliser le port fourni par Render ou 5000 par défaut
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
