from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        # чтобы сигналы из signals.py зарегистрировались
        import accounts.signals
