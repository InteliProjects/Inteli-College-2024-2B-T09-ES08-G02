import boto3
import os
import json
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

load_dotenv()

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN")
        )
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")
        
    def upload_file(self, file, key, content_type=None):
        try:
            if isinstance(file, dict):
                file_data = json.dumps(file).encode('utf-8')  
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file_data,
                    ContentType=content_type or "application/json"
                )
            else:  # Para arquivos normais
                self.s3_client.upload_fileobj(file, self.bucket_name, key)
            
            return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
        except (BotoCoreError, ClientError) as e:
            print(f"Erro ao fazer upload: {e}")
            return None
