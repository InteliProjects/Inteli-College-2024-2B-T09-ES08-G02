import unittest
from io import BytesIO
from run import app
from dotenv import load_dotenv
from app.services.s3_service import S3Service
import json

load_dotenv()

s3_service = S3Service()

class TestUploadToAWS(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_upload_file_success(self):
        print("-------------------------------------------")
        print("Teste: test_upload_file_success rodando...")

        # Cria um arquivo .txt para upload
        data = {
            "key":"test_file.txt",
            "content": "{\"data\": \"Exemplo de conteúdo JSON\"}",
            "username":"macedo",
            "password":"1",
            "project":"Inteli" 
        }

        response = self.app.post('/upload', 
                                    data=json.dumps(data), 
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertIn('url', response_json)

    def test_upload_file_filed(self):
        print("-------------------------------------------")
        print("Teste: test_upload_file_filed rodando...")

        # Cria um arquivo .txt para upload
        data = {
            "key":"test_file.txt",
            "content": "{\"data\": \"Exemplo de conteúdo JSON\"}",
            "username":"macedo",
            "password":"1",
            "project":"Brasil" #Brasil não está nos projetos do user "macedo"
        }

        response = self.app.post('/upload', 
                                    data=json.dumps(data), 
                                    content_type='application/json')
        
        response_json = json.loads(response.data)
        self.assertIn(response.status_code, [400, 401, 403, 500])
        self.assertIn('error', response_json)

    def test_upload_log_success(self):
        print("-------------------------------------------")
        print("Teste: test_upload_log_success rodando...")

        response = self.app.post('/send-log')
        response_json = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response_json)

if __name__ == '__main__':
    unittest.main()