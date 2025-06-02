from django.contrib.admin.apps import AdminConfig

class CodaquiAdminConfig(AdminConfig):
    default_site = "codaqui.admin.CodaquiAdminSite"