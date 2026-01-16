# bd2ap1/signals.py
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from .mongo_logger import log_action


@receiver(user_logged_in)
def audit_login(sender, user, request, **kwargs):
    """Grava no Mongo quando o login é bem sucedido"""
    # Tenta pegar o IP do utilizador
    ip = request.META.get('REMOTE_ADDR')

    log_action(
        user=user,
        action='LOGIN',
        target_model='Auth',
        target_id=user.id,
        details={'ip_address': ip, 'status': 'Success'}
    )


@receiver(user_logged_out)
def audit_logout(sender, user, request, **kwargs):
    """Grava no Mongo quando faz logout"""
    if user:  # Às vezes o user pode vir None se a sessão expirou
        log_action(
            user=user,
            action='LOGOUT',
            target_model='Auth',
            target_id=user.id,
            details={'status': 'Success'}
        )


@receiver(user_login_failed)
def audit_login_fail(sender, credentials, request, **kwargs):
    """Grava tentativas falhadas (Importante para Segurança!)"""
    # Nota: Aqui não temos 'user' objeto porque o login falhou
    # Mas temos as credenciais que ele tentou usar
    ip = request.META.get('REMOTE_ADDR')
    username_attempt = credentials.get('username', 'unknown')

    # Precisamos de um objeto 'fake' ou None para o nosso logger

    # Gravação manual direta ou adaptar o log_action para lidar com user=None
    from .mongo_logger import collection, datetime

    if collection is not None:
        log_entry = {
            'username': username_attempt,
            'action': 'LOGIN_FAILED',
            'target_model': 'Auth',
            'target_id': None,
            'timestamp': datetime.datetime.now(),
            'details': {'ip_address': ip, 'reason': 'Bad Credentials'}
        }
        try:
            collection.insert_one(log_entry)
            print(f"⚠️ Tentativa de login falhada registada: {username_attempt}")
        except:
            pass

@receiver(post_save, sender=User)
def audit_user_creation(sender, instance, created, **kwargs):
    """Grava no Mongo quando um novo utilizador é criado (Registo)"""
    if created:
        from .mongo_logger import log_action
        # Nota: 'user=instance' porque o próprio user é o alvo e o autor neste contexto inicial
        # Ou podes passar user=None se quiseres considerar criação anónima
        log_action(
            user=instance,
            action='USER_REGISTER',
            target_model='Auth',
            target_id=instance.id,
            details={'username': instance.username, 'is_superuser': instance.is_superuser}
        )