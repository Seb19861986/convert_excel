@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']  # Récupère le fichier uploadé
    if file and file.filename.endswith('.xlsx'):  # Vérifie que le fichier est un Excel
        # Sauvegarde du fichier temporairement
        temp_file_path = os.path.join('uploads', file.filename)
        file.save(temp_file_path)
        
        # Appel de la fonction de conversion pour générer le fichier JSON
        output_json_path = os.path.join('uploads', 'output.json')
        convert_excel_to_json(temp_file_path, output_json_path)
        
        # Renvoi du fichier JSON au client
        return send_file(output_json_path, as_attachment=True)
