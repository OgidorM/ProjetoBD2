# bd2ap1/mongo_logger.py
import datetime
import os
from django.conf import settings
from pymongo import MongoClient

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('MONGO_DB_NAME', 'cinema_audit_db')

try:
    if not MONGO_URI:
        raise ValueError("MONGO_URI não encontrada no ficheiro .env")

    client = MongoClient(MONGO_URI)

    db = client[DB_NAME]
    collection = db['logs_acoes']
    print("✅ Conectado ao MongoDB Atlas com sucesso!")
except Exception as e:
    print(f"Erro ao conectar ao MongoDB: {e}")
    collection = None


def log_action(user, action, target_model, target_id, details=None):
    if collection is None:
        return

        # Tratamento para quando o user é None (ex: Login Falhado)
    if user:
        username = user.username if user.is_authenticated else 'Anonymous'
        user_id = user.id
    else:
        username = details.get('username_attempt', 'Unknown') if details else 'Unknown'
        user_id = None

    log_entry = {
        'username': username,
        'user_id': user_id,
        'action': action,
        'target_model': target_model,
        'target_id': target_id,
        'timestamp': datetime.datetime.now(),
        'details': details or {}
    }

    try:
        collection.insert_one(log_entry)
        # print(f"Log enviado para Atlas: {action}") # Descomenta se quiseres ver no terminal
    except Exception as e:
        print(f"❌ Erro ao enviar log para Atlas: {e}")