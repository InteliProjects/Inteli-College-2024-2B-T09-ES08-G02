from flask import Flask, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.services.s3_service import S3Service
from dotenv import load_dotenv
from app.models.db import SessionLocal
from app.services.user import create_user_service
from app.models.user import User
import bcrypt
import sys
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import requests
from app.models.db import db
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:099403bo@mysql_container:3306/ipt_los_tigres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o SQLAlchemy com a aplicação
db.init_app(app)

# Inicializa o Flask-Migrate com a aplicação e o db
migrate = Migrate(app, db)

s3_service = S3Service()

# Configuração de logs
log_handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=5)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log_handler.setFormatter(formatter)

# Adiciona o handler ao logger principal do Flask
app.logger.setLevel(logging.INFO)  
app.logger.addHandler(log_handler)

#Rota de verificação do Back
@app.route('/', methods=['GET'])
def test_endpoint():
    return 'It s working'    

#Rota de envio de arquivos/json para a S3
@app.route('/upload', methods=['POST'])
def upload_file_or_json():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    project = data.get("project")

    client_ip = request.remote_addr 

    if not username or not password:
        status_code = 400
        log_message = f"IP: {client_ip} - Requisição inválida: username ou password ausente. Dados recebidos: {data} - Status: {status_code}"
        app.logger.warning(log_message)
        requests.post("http://localhost:5000/send-log")
        return jsonify({"error": "Username and password are required"}), status_code

    session = SessionLocal()

    try:
        user = session.query(User).filter(User.username == username).first()

        if not user:
            status_code = 401
            log_message = f"IP: {client_ip} - Tentativa de login falhada: Usuário {username} não encontrado. - Status: {status_code}"
            app.logger.warning(log_message)
            requests.post("http://localhost:5000/send-log")
            return jsonify({"error": "Invalid username or password"}), status_code

        if not user.password:
            status_code = 400
            log_message = f"IP: {client_ip} - Erro: Senha não encontrada para o usuário {username}. - Status: {status_code}"
            app.logger.error(log_message)
            requests.post("http://localhost:5000/send-log")
            return jsonify({"error": "Password not found for user"}), status_code

        if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            status_code = 401
            log_message = f"IP: {client_ip} - Tentativa de login falhada: Senha inválida para o usuário {username}. - Status: {status_code}"
            app.logger.warning(log_message)
            requests.post("http://localhost:5000/send-log")
            return jsonify({"error": "Invalid username or password"}), status_code

        if project not in user.project:
            status_code = 403
            log_message = f"IP: {client_ip} - Usuário {username} tentou fazer upload sem permissão no projeto. - Status: {status_code}"
            app.logger.warning(log_message)
            requests.post("http://localhost:5000/send-log")
            return jsonify({"error": "Você não tem permissão para realizar o upload nesse projeto"}), status_code

        if request.is_json:
            json_data = request.get_json()

            if "key" not in json_data or "content" not in json_data:
                status_code = 400
                log_message = f"IP: {client_ip} - Requisição JSON inválida pelo usuário {username}. Dados: {json_data} - Status: {status_code}"
                app.logger.warning(log_message)
                requests.post("http://localhost:5000/send-log")
                return jsonify({"error": "JSON deve conter KEY e CONTENT"}), status_code

            key = json_data["key"]
            content = json_data["content"]

            try:
                s3_service.s3_client.put_object(
                    Bucket=s3_service.bucket_name,
                    Key=key,
                    Body=content,
                    ContentType="application/json"
                )
                file_url = f"https://{s3_service.bucket_name}.s3.amazonaws.com/{key}"
                status_code = 200
                log_message = f"IP: {client_ip} - Upload JSON bem-sucedido pelo usuário {username}. URL: {file_url} - Status: {status_code}"
                app.logger.info(log_message)
                requests.post("http://localhost:5000/send-log")
                return jsonify({"message": "Upload JSON bem-sucedido!", "url": file_url}), status_code
            except Exception as e:
                status_code = 500
                log_message = f"IP: {client_ip} - Erro ao fazer upload JSON pelo usuário {username}. Erro: {e} - Status: {status_code}"
                app.logger.error(log_message)
                requests.post("http://localhost:5000/send-log")
                return jsonify({"error": "Falha no upload do JSON"}), status_code

        elif 'file' in request.files:
            file = request.files['file']
            key = file.filename

            try:
                s3_service.s3_client.upload_fileobj(file, s3_service.bucket_name, key)
                file_url = f"https://{s3_service.bucket_name}.s3.amazonaws.com/{key}"
                status_code = 200
                log_message = f"IP: {client_ip} - Upload de arquivo bem-sucedido pelo usuário {username}. Arquivo: {key}, URL: {file_url} - Status: {status_code}"
                app.logger.info(log_message)
                requests.post("http://localhost:5000/send-log")
                return jsonify({"message": "Upload de arquivo bem-sucedido!", "url": file_url}), status_code
            except Exception as e:
                status_code = 500
                log_message = f"IP: {client_ip} - Erro ao fazer upload do arquivo pelo usuário {username}. Erro: {e} - Status: {status_code}"
                app.logger.error(log_message)
                requests.post("http://localhost:5000/send-log")
                return jsonify({"error": "Falha no upload do arquivo"}), status_code

        else:
            status_code = 400
            log_message = f"IP: {client_ip} - Requisição inválida pelo usuário {username}: Nenhum arquivo ou JSON enviado. - Status: {status_code}"
            app.logger.warning(log_message)
            requests.post("http://localhost:5000/send-log")
            return jsonify({"error": "Nenhum arquivo ou JSON enviado"}), status_code

    finally:
        session.close()

#Rota de GET ALL de usuários
@app.route('/user', methods=['GET'])
def all_user():
    session = SessionLocal()
    try:
        users = session.query(User).all()

        user_data = []
        for user in users:
            user_data.append({
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "project": user.project 
            })
        
        return jsonify(user_data)

    except SQLAlchemyError as e:
        print(f"Erro ao buscar usuários: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

#Rota de criação de usuários
@app.route("/user", methods=['POST'])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    project = data.get("project")
    name = data.get("name")

    if not username or not password or not project or not name:
        return jsonify({"error": "Existem dados nulos na criação do usuário."}), 400

    session = SessionLocal()
    try:
        response, status = create_user_service(session, username, password, project, name)
        return jsonify(response), status
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# Endpoint para enviar logs para o S3
@app.route('/send-log', methods=['POST'])
def send_log_to_s3():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        with open('app.log', 'r') as log_file:
            log_content = log_file.read()

        log_filename = f"app_logs_{timestamp}.txt"

        s3_service.s3_client.put_object(
            Bucket="ipt-los-tigres-logs-system",  
            Key=f'logs/{log_filename}', 
            Body=log_content,
            ContentType='text/plain'
        )

        return jsonify({"message": "Logs enviados para o S3 com sucesso!"}), 200

    except Exception as e:
        app.logger.error(f"Erro ao enviar logs para o S3: {str(e)}")
        return jsonify({"error": "Erro ao enviar logs para o S3"}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
