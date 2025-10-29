from flask import Flask, request, render_template, send_file, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename
from model import get_res

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Допустимые расширения файлов
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_text_file(input_path, output_path):
    """
    Метод parse - обрабатывает текстовый файл и создает выходной файл
    В данном примере: преобразует текст в верхний регистр и добавляет статистику
    """
    get_res(input_path, output_path)
    return True, None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Обработка загрузки файла"""
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не выбран'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Сохраняем загруженный файл
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"input_{filename}")
            file.save(input_path)
            
            # Создаем выходной файл
            output_filename = f"processed_{filename}"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            # Обрабатываем файл методом parse
            success, error = parse_text_file(input_path, output_path)
            
            if not success:
                return jsonify({'error': f'Ошибка обработки: {error}'}), 500
            
            # Возвращаем информацию о сгенерированном файле
            return jsonify({
                'message': 'Файл успешно обработан',
                'output_file': output_filename,
                'download_url': f'/download/{output_filename}'
            })
            
        except Exception as e:
            return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500
        finally:
            # Удаляем временный входной файл
            if os.path.exists(input_path):
                os.remove(input_path)
    else:
        return jsonify({'error': 'Недопустимый тип файла'}), 400

@app.route('/download/<filename>')
def download_file(filename):
    """Скачивание обработанного файла"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Файл не найден'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    except Exception as e:
        return jsonify({'error': f'Ошибка загрузки: {str(e)}'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Очистка временных файлов"""
    try:
        temp_dir = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(temp_dir):
            if filename.startswith('processed_'):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        return jsonify({'message': 'Временные файлы очищены'})
    except Exception as e:
        return jsonify({'error': f'Ошибка очистки: {str(e)}'}), 500

if __name__ == '__main__':
    # Создаем папку для шаблонов если её нет
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    app.run(debug=True, host='127.0.0.1', port=5000)