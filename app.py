from flask import Flask, request
import pandas as pd
import os
import requests
import base64

app = Flask(__name__)

# Remplacer par ton vrai token GitHub ici
GITHUB_TOKEN = "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"  # Insère ici ton nouveau token GitHub

# Fonction de conversion Excel vers JSON
def convert_excel_to_json(file_path, output_json_path):
    excel_data = pd.ExcelFile(file_path)
    df = excel_data.parse(excel_data.sheet_names[0])
    df.columns = df.columns.str.strip()

    column_groups = {
        "Competence": ['Compétence / responsabilité'],
        "EntiteFocus": ['Entité(s) en focus (contexte)'],
    }

    for new_column, columns in column_groups.items():
        df[new_column] = df[columns].apply(lambda x: ' - '.join(x.dropna().astype(str)), axis=1)

    columns_to_drop = sum(column_groups.values(), [])
    df_cleaned = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    json_data = df_cleaned.to_json(orient='records', lines=False, force_ascii=False)

    with open(output_json_path, 'w', encoding='utf-8') as f:
        f.write(json_data)

# Fonction pour envoyer le fichier JSON sur GitHub
def upload_to_github(json_file_path, github_repo, path_in_repo):
    with open(json_file_path, 'rb') as file:
        content = base64.b64encode(file.read()).decode()

    api_url = f"https://api.github.com/repos/{github_repo}/contents/{path_in_repo}"

    data = {
        "message": "Mise à jour du fichier JSON",
        "content": content,
        "branch": "main"  # Si tu utilises une autre branche, remplace "main" par le nom de ta branche
    }

    response = requests.put(
        api_url,
        json=data,
        headers={"Authorization": f"token {GITHUB_TOKEN}"}  # Utilisation directe du token dans l'en-tête
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
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            
            temp_file_path = os.path.join('uploads', file.filename)
            file.save(temp_file_path)

            output_json_path = os.path.join('uploads', file.filename.replace('.xlsx', '.json'))
            convert_excel_to_json(temp_file_path, output_json_path)

            github_repo = "Seb19861986/competences_locales"  # Remplace par ton utilisateur et ton dépôt
            path_in_repo = "DataTest.json"  # Remplace par le chemin du fichier dans le dépôt

            upload_status = upload_to_github(output_json_path, github_repo, path_in_repo)

            return upload_status
        except Exception as e:
            return f"Une erreur est survenue: {str(e)}", 500
    return "Invalid file format. Please upload an Excel file.", 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
