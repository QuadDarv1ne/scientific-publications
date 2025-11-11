from flask import Flask, render_template, jsonify
import heliopy

app = Flask(__name__)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница анализа
@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

# Страница визуализации
@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

# Страница API и документации
@app.route('/api-docs')
def api_docs():
    return render_template('api.html')

# Страница "О проекте"
@app.route('/about')
def about():
    return render_template('about.html')

# API-информация
@app.route('/api/info')
def info():
    return jsonify({
        'name': 'HelioPy',
        'description': 'Библиотека для анализа солнечной активности и космической погоды',
        'version': '0.1.0'
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
