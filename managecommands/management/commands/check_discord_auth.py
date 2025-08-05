import requests
from django.core.management.base import BaseCommand, CommandError
from codaqui.settings import DISCORD_API_ENDPOINT, DISCORD_TOKEN

class Command(BaseCommand):
    help = "Verifica se o bot do Discord está autenticado corretamente na API do Discord."

    def handle(self, *args, **options):
        url = f"{DISCORD_API_ENDPOINT}/users/@me"
        headers = {
            "Authorization": f"Bot {DISCORD_TOKEN}"
        }

        self.stdout.write("Testando autenticação na API do Discord...")

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            self.stdout.write(self.style.SUCCESS("Autenticação Discord: OK"))
            self.stdout.write(f"Bot Username: {data.get('username')}#{data.get('discriminator')}")
            self.stdout.write(f"Bot ID: {data.get('id')}")
        elif response.status_code == 401:
            raise CommandError("Unauthorized (401): Token inválido ou expirado.")
        else:
            raise CommandError(f"Erro inesperado: {response.status_code} - {response.text}")