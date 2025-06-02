from django.contrib import admin

class CodaquiAdminSite(admin.AdminSite):
    site_header = "Painel de Administração da Codaqui"
    site_title = "Codaqui Administração"
    index_title = "Seja bem vindo a Codaqui"