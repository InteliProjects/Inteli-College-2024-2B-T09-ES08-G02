import unittest
from run import app
from dotenv import load_dotenv
import os
import sys
from datetime import datetime


load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

class TestCreateUser(unittest.TestCase):
    def setUp(self):
        """Configuração necessária antes de cada teste"""
        #test_client simula requisições para o Flask
        self.app = app.test_client()
        self.app.testing = True

    def test_create_user_sucess(self,):
        """Teste de criação de usuário - Sucesso""" 
        print("-------------------------------------------")
        print("Teste: test_create_user_success rodando...")

        #Maneira para criar um username diferente sempre (username é único)
        data_atual = datetime.now()
        data_formatada = data_atual.strftime("%Y-%m-%d_%H-%M-%S")
        nome = f"teste+{data_formatada}"

        #Dados validos
        data = {
            "username":nome,
            "password":"12345",
            "project":["Teste"],
            "name":"Teste teste teste"
        }

        #Envio da requisição
        response = self.app.post('/user', json=data)

        #Verificações do teste
        self.assertEqual(response.status_code, 201)
        print("Teste test_create_user_success passou com sucesso!")

    def test_create_user_failed(self):
        """Teste de criação de usuário - Erro""" 
        print("-------------------------------------------")
        print("Teste: test_create_user_failed rodando...")

        #Dados Inválidos - Username "macedo" já existe no banco
        data = {
            "username":"macedo",
            "password":"1",
            "project":["Inteli"],
            "name":"Luigi Otávio"
        }

        #Envio da requisição
        response = self.app.post('/user', json=data)

        #Verificações do teste
        self.assertEqual(response.status_code, 400)
        print("Teste test_create_user_failed passou com sucesso!")

    def test_get_all_user(self):
        """Teste de listagem de usuários - Ok""" 
        print("-------------------------------------------")
        print("Teste: test_get_all_user rodando...")

        response = self.app.get('user')

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()