# Verificando se o usuário 'ArtumosGOC' é membro da organização
#❌ 403 Forbidden: Token sem permissão suficiente.

#📩 Verificando convites pendentes na organização
#❌ 403 Forbidden: Token sem permissão suficiente.

# caso isso aconteça, é necessário verificar se o token de acesso tem as permissões corretas para acessar os recursos da organização 
# provavelmente é um problema de permissão do github app
# Para isso, é necessário verificar as permissões do token de acesso no GitHub App e garantir que ele tenha acesso aos recursos necessários, como repositórios, issues, membros e convites.

# SCRIPT: CRIADO PARA TESTAR O ACESSO A REPOSITÓRIOS, ISSUES, MEMBROS E CONVITES DE UM USUÁRIO NA ORGANIZAÇÃO DO GITHUB
# usar dentro do container docker!!!

from django.core.management.base import BaseCommand
import requests
from codaqui.settings import GITHUB_ORGANIZATION, GITHUB_REPOSITORY
from github_service.auth import generate_access_token

class Command(BaseCommand):
    help = "Verifica autenticação GitHub e testa acesso a repositório, issues, membro e convites."

    def add_arguments(self, parser):
        parser.add_argument(
            '--username', '-U',
            type=str,
            help='GitHub username para testar membership (ex: \'endersonmenezes\')',
            default='' 
        )

    def handle(self, *args, **options):
        github_username = options['username']
        token = generate_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }
        
        if not github_username:
            self.stdout.write(self.style.ERROR("❌ Erro: Você deve fornecer um GitHub username com --username."))
            return

        self.stdout.write(f"🔑 Usando token de acesso para o usuário: {github_username}")
        
        repo_url = f"https://api.github.com/repos/{GITHUB_ORGANIZATION}/{GITHUB_REPOSITORY}"
        repo_response = requests.get(repo_url, headers=headers)

        self.stdout.write(f"\n🔎 Verificando acesso ao repositório [{GITHUB_ORGANIZATION}/{GITHUB_REPOSITORY}]")
        self._check_response(repo_response)

        issues_url = f"https://api.github.com/repos/{GITHUB_ORGANIZATION}/{GITHUB_REPOSITORY}/issues"
        issues_response = requests.get(issues_url, headers=headers)

        self.stdout.write("\n📝 Testando listagem de issues")
        self._check_response(issues_response)

        if issues_response.status_code == 200:
            issues = issues_response.json()
            total = len(issues)

            self.stdout.write(f"→ Total de issues retornadas: {total}")

            if total > 0:
                self.stdout.write("📋 Títulos das issues:")
                for issue in issues:
                    number = issue.get("number", "Sem número")
                    title = issue.get("title", "Sem título")

                    self.stdout.write(f" - Issue #{number}: {title}")

        membership_url = f"https://api.github.com/orgs/{GITHUB_ORGANIZATION}/memberships/{github_username}"
        membership_response = requests.get(membership_url, headers=headers)

        self.stdout.write(f"\n👥 Verificando se o usuário '{github_username}' é membro da organização")
        self._check_response(membership_response)

        invitations_url = f"https://api.github.com/orgs/{GITHUB_ORGANIZATION}/invitations"
        invitations_response = requests.get(invitations_url, headers=headers)

        self.stdout.write("\n📩 Verificando convites pendentes na organização")
        self._check_response(invitations_response)

        self.stdout.write("\n✅ Fim dos testes.")

    def _check_response(self, response):
        status = response.status_code
        if status == 200:
            self.stdout.write(self.style.SUCCESS("✅ Sucesso!"))
        elif status == 401:
            self.stdout.write(self.style.ERROR("❌ 401 Unauthorized: Token inválido ou expirado."))
        elif status == 403:
            self.stdout.write(self.style.ERROR("❌ 403 Forbidden: Token sem permissão suficiente."))
        elif status == 404:
            self.stdout.write(self.style.WARNING("⚠️ 404 Not Found: Endpoint ou usuário inexistente."))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Status inesperado: {status}"))
            try:
                self.stdout.write(response.text)
            except Exception:
                pass

# Endpoint: https://docs.github.com/en/rest/reference/orgs