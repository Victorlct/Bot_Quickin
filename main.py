from flask import Flask, render_template, request, redirect, url_for
from backend import obter_token_e_job_id, obter_vaga_detalhada, obter_id_usuario, obter_todos_stages

app = Flask(__name__)

token = None  # Variável global para armazenar o token
id_usuario = None

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    global token  # Indicando que queremos usar a variável global token
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        hashtag_desejada = request.form['hashtag']

        # Obter o token e o job_id
        token, job_id = obter_token_e_job_id(email, senha, hashtag_desejada)
        
        # Obter o ID do usuário
        id_usuario = obter_id_usuario(token)
        
        # Obter os detalhes da vaga
        vaga_detalhada = obter_vaga_detalhada(id_usuario, job_id, token)
        
        # Obter todos os stages da vaga
        stages = obter_todos_stages(token, id_usuario)

        # Redirecionar para a página de informações da vaga
        return redirect(url_for('infosVaga', vaga=str(vaga_detalhada), stages=str(stages)))

@app.route('/infosVaga/<vaga>/<stages>')
def infosVaga(vaga, stages):
    # Converter as strings para objetos Python
    vaga = eval(vaga)
    stages = eval(stages)

    # Organizar as informações da vaga
    nome = vaga.get('title', 'Nome não disponível')
    local = vaga.get('region', 'Local não disponível')
    salario_maximo = vaga.get('remuneration_max', 'Salário máximo não disponível')
    salario_minimo = vaga.get('remuneration', 'Salário mínimo não disponível')
    outras_informacoes = vaga.get('status', 'Outras informações não disponíveis')

    # Organizar os stages para o select
    options_stages = [(stage['_id'], stage['name']) for stage in stages]

    return render_template('infosVaga.html', nome=nome, local=local, salario_maximo=salario_maximo,
                           salario_minimo=salario_minimo, outras_informacoes=outras_informacoes,
                           options_stages=options_stages)

if __name__ == '__main__':
    app.run(debug=True)
