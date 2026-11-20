from flask import Flask, render_template

# Шаблон лежит в томе ./storage → /storage, а не в /templates
app = Flask(__name__, template_folder='/storage')


# Клиент ходит на https://localhost/ (корень).
@app.route('/')
def hello_world():
    # Без source_app шаблон давал «Hello World from !»
    return render_template('index.html', source_app='app2')


if __name__ == '__main__':
    # user www не биндит порты <1024
    app.run(debug=True, host='0.0.0.0', port=8080)
