from urllib.parse import parse_qs, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

def obter_token_e_job_id(email, senha, hashtag_desejada):
    # Configurações do Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--enable-logging=stderr")
    options.add_argument("--log-level=0")

    # Inicialização do ChromeDriver com as opções configuradas
    driver = webdriver.Chrome(options=options)
    driver.get("https://app.quickin.io/")
    wait = WebDriverWait(driver, 10)

    # Preencher informações de login
    input_email = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div/div/div/form/div[1]/div[1]/input')))
    input_email.send_keys(email)
    input_senha = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div/div/div/form/div[1]/div[2]/input')
    input_senha.send_keys(senha)

    # Clicar no botão de login
    botao_login = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div/div/div/form/div[2]/div/button')
    botao_login.click()

    # Clicar na vaga com a hashtag informada
    xpath_hashtag = f'//span[contains(text(), "{hashtag_desejada}")]'
    hashtag_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath_hashtag)))
    hashtag_element.click()

    # Extrair o job_id da URL
    url = driver.current_url
    parsed_url = urlparse(url)
    fragment = parsed_url.fragment
    job_id = fragment.split("/")[-1]

    # Esperar um curto intervalo para garantir que a página seja totalmente carregada
    time.sleep(2)

    # Extrair o token do cookie
    token = driver.execute_script("""
        function obterTokenDoCookie() {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.startsWith('access_token=')) {
                    return cookie.substring('access_token='.length);
                }
            }
            return null;
        }

        return obterTokenDoCookie();
    """)

    # Fechar o navegador
    driver.quit()

    return token, job_id

def obter_vaga_detalhada(idusuario, jobid, token):
    # URL da API para obter os detalhes da vaga
    url = f"https://api.quickin.io/accounts/{idusuario}/jobs/{jobid}"

    # Cabeçalhos da requisição com o token de autorização
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        # Fazer a chamada GET para obter os detalhes da vaga
        response = requests.get(url, headers=headers)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            # Retornar os detalhes da vaga em formato JSON
            return response.json()
        else:
            print(f"Erro ao obter os detalhes da vaga: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Erro ao obter os detalhes da vaga: {str(e)}")
        return None

def obter_todos_stages(token, id_usuario):
    # URL da API para listar os estágios
    url = f"https://api.quickin.io/accounts/{id_usuario}/stages"

    # Cabeçalhos da requisição com o token de autorização
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        # Fazer a chamada GET para obter os estágios
        response = requests.get(url, headers=headers)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            # Converter a resposta para JSON
            resposta_json = response.json()

            # Lista para armazenar os estágios com seus IDs
            stages = []

            # Adicionar cada estágio à lista
            for stage in resposta_json:
                stage_info = {
                    "name": stage.get("name"),
                    "_id": stage.get("_id")
                }
                stages.append(stage_info)

            return stages
        else:
            print(f"Erro ao obter os estágios: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Erro ao obter os estágios: {str(e)}")
        return None

def obter_id_usuario(token):
    # URL da API para obter informações do usuário
    url = "https://api.quickin.io/accounts"

    # Cabeçalhos da requisição com o token de autorização
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        # Fazer a chamada GET para obter informações do usuário
        response = requests.get(url, headers=headers)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            # Converter a resposta para JSON e retornar o ID do usuário
            resposta_json = response.json()
            id_usuario = resposta_json[0]["_id"]
            return id_usuario
        else:
            print(f"Erro ao obter ID do usuário: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Erro ao obter ID do usuário: {str(e)}")
        return None

def obter_stage_id(token, job_id, IdUsuario):
    # URL base da API para listar candidatos
    url_base = f"https://api.quickin.io/accounts/{IdUsuario}/candidates/board-start"

    # Parâmetros da requisição
    params = {
        "status": "qualified",
        "job_id": job_id,
        "limit": 1000  # Alterado para 1000
    }

    # Cabeçalhos da requisição com o token de autorização
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        # Fazer a chamada GET para listar os candidatos com os parâmetros fornecidos
        response = requests.get(url_base, headers=headers, params=params)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            # Converter a resposta para JSON
            resposta_json = response.json()

            if resposta_json:
                stage_id = resposta_json[0]['stage_id']
                return stage_id
            else:
                print("Resposta vazia ou formato inesperado.")
        else:
            print(f"Erro ao obter stage_id: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Erro ao obter stage_id: {str(e)}")
        return None

def listar_todos_candidatos(token, stage_id, job_id, IdUsuario):
    # URL base da API para listar candidatos por stage
    url_base = f"https://api.quickin.io/accounts/{IdUsuario}/candidates/board-stage"

    # Lista para armazenar todos os candidatos
    todos_candidatos = []

    # Parâmetros iniciais da requisição
    params = {
        "status": "qualified",
        "job_id": job_id,
        "limit": 30,  # Limite inicial
        "skip": 0,  # Começar com o primeiro registro
        "stage_id": stage_id  # Utilizar o stage_id fornecido
    }

    # Cabeçalhos da requisição com o token de autorização
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        while True:
            # Fazer a chamada GET para listar os candidatos com os parâmetros fornecidos
            response = requests.get(url_base, headers=headers, params=params)

            # Verificar se a requisição foi bem-sucedida
            if response.status_code == 200:
                # Converter a resposta para JSON
                resposta_json = response.json()
                
                # Verificar se há candidatos na resposta
                if 'docs' in resposta_json:
                    # Adicionar os candidatos à lista de todos os candidatos
                    todos_candidatos.extend(resposta_json['docs'])
                else:
                    print("Erro: Nenhum candidato encontrado na resposta.")
                    break
                
                # Verificar se há mais registros disponíveis
                if not resposta_json.get('has_more', False):
                    # Todos os registros foram recuperados
                    break
                
                # Atualizar o parâmetro de paginação para obter o próximo conjunto de registros
                params['skip'] += params['limit']
            else:
                print(f"Erro ao listar candidatos: {response.status_code} - {response.text}")
                break

        return todos_candidatos

    except Exception as e:
        print(f"Erro ao listar candidatos: {str(e)}")
        return None

def obter_detalhes_candidato(token, candidato_id, IdUsuario):
    # URL base da API para obter os detalhes de um candidato
    url_base = f"https://api.quickin.io/accounts/{IdUsuario}/candidates/{candidato_id}"

    # Cabeçalhos da requisição com o token de autorização
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        # Fazer a chamada GET para obter os detalhes do candidato com o ID fornecido
        response = requests.get(url_base, headers=headers)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            # Converter a resposta para JSON e retornar os detalhes do candidato
            detalhes_candidato = response.json()
            return detalhes_candidato
        else:
            print(f"Erro ao obter detalhes do candidato {candidato_id}: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Erro ao obter detalhes do candidato {candidato_id}: {str(e)}")
        return None

def obter_candidatos_com_salario_acima(candidatos, token, pretensao_salarial, id_stage_destino, IdUsuario, nome_motivo_desqualificacao, nome_stage_desejado):
    candidatos_processados = 0
    candidatos_movidos = 0
    candidatos_desqualificados = 0

    for candidato in candidatos:
        candidato_id = candidato["_id"]
        detalhes_candidato = obter_detalhes_candidato(token, candidato_id)
        if detalhes_candidato:
            source = detalhes_candidato.get("source_id", [])
            salario = detalhes_candidato.get("salary", None)
            
            if source.get("name") == "Catho" or source.get("name") == "Catho api":
                if mover_candidato_para_stage(token, IdUsuario, candidato["placements"][0]["_id"], id_stage_destino):
                    print(f"Candidato {candidato['name']} movido para o estágio '{nome_stage_desejado}'.")
                    candidatos_movidos += 1
                else:
                    print(f"Falha ao mover candidato {candidato['name']} para o estágio '{nome_stage_desejado}'.")
            elif salario is not None and salario > pretensao_salarial:
                id_motivo_desqualificacao = obter_id_motivo_desqualificacao(token, IdUsuario, nome_motivo_desqualificacao)
                if id_motivo_desqualificacao:
                    if desqualificar_candidato(token, IdUsuario, candidato["placements"][0]["_id"], id_motivo_desqualificacao):
                        print(f"Candidato {candidato['name']} desqualificado.")
                        candidatos_desqualificados += 1
                    else:
                        print(f"Falha ao desqualificar candidato {candidato['name']}.")
                else:
                    print("Não foi possível obter o ID do motivo de desqualificação.")
            else:
                print(f"Candidato {candidato['name']} não atende aos critérios para movimentação ou desqualificação.")
            candidatos_processados += 1
        else:
            print(f"Falha ao obter detalhes do candidato {candidato_id}.")

    print(f"Total de candidatos processados: {candidatos_processados}")
    print(f"Total de candidatos movidos para o estágio '{nome_stage_desejado}': {candidatos_movidos}")
    print(f"Total de candidatos desqualificados por pretensão salarial acima: {candidatos_desqualificados}")

def mover_candidato_para_stage(token, id_usuario, id_placement, id_stage_destino):
    # URL da API para mover o candidato entre estágios
    url = f"https://api.quickin.io/accounts/{id_usuario}/placements/{id_placement}/move"

    # Payload da requisição
    payload = {
        "_id": id_placement,
        "stage_id": id_stage_destino
    }

    # Cabeçalhos da requisição com o token de autorização e o tipo de conteúdo
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Fazer a chamada PUT para mover o candidato para o estágio desejado
        response = requests.put(url, headers=headers, json=payload)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            print("Candidato movido com sucesso para o novo estágio.")
            return True
        else:
            print(f"Erro ao mover o candidato para o novo estágio: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Erro ao mover o candidato para o novo estágio: {str(e)}")
        return False

def obter_id_motivo_desqualificacao(token, id_usuario, nome_motivo_desqualificacao):
    # URL da API para obter os motivos de desqualificação
    url = f"https://api.quickin.io/accounts/{id_usuario}/disqualify-reasons?sort=name&limit=2000"

    # Cabeçalhos da requisição com o token de autorização
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        # Fazer a chamada GET para obter os motivos de desqualificação
        response = requests.get(url, headers=headers)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            # Converter a resposta para JSON
            motivos_desqualificacao = response.json()

            # Procurar pelo motivo de desqualificação com o nome desejado
            for motivo in motivos_desqualificacao:
                if motivo.get("name") == nome_motivo_desqualificacao:
                    return motivo.get("_id")

            print(f"Erro: Não foi encontrado um motivo de desqualificação com o nome '{nome_motivo_desqualificacao}'.")
            return None
        else:
            print(f"Erro ao obter os motivos de desqualificação: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Erro ao obter os motivos de desqualificação: {str(e)}")
        return None

def desqualificar_candidato(token, id_usuario, id_placement, id_motivo_desqualificacao):
    # URL da API para desqualificar o candidato
    url = f"https://api.quickin.io/accounts/{id_usuario}/placements/{id_placement}/disqualify"

    # Payload da requisição
    payload = {
        "_id": id_placement,
        "disqualify_reason_id": id_motivo_desqualificacao
    }

    # Cabeçalhos da requisição com o token de autorização e o tipo de conteúdo
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Fazer a chamada PUT para desqualificar o candidato
        response = requests.put(url, headers=headers, json=payload)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            print("Candidato desqualificado com sucesso.")
            return True
        else:
            print(f"Erro ao desqualificar o candidato: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Erro ao desqualificar o candidato: {str(e)}")
        return False
