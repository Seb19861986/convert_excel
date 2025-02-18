from flask import Flask, request, send_file
import pandas as pd
import os

app = Flask(__name__)

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

@app.route('/')
def upload_form():
    # Flask va chercher le fichier 'index.html' dans le dossier 'templates'
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and file.filename.endswith('.xlsx'):
        # Créer le dossier uploads si nécessaire
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        
        # Sauvegarder le fichier temporairement
        temp_file_path = os.path.join('uploads', file.filename)
        file.save(temp_file_path)

        # Convertir le fichier Excel en JSON
        output_json_path = os.path.join('uploads', file.filename.replace('.xlsx', '.json'))
        convert_excel_to_json(temp_file_path, output_json_path)

        # Retourner le fichier JSON comme réponse
        return send_file(output_json_path, as_attachment=True)
    return "Invalid file format. Please upload an Excel file."

if __name__ == "__main__":
    # Utiliser le port fourni par Render ou 5000 par défaut
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
