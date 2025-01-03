from django.contrib import admin
from discord_service.models import dicordService


import requests


@admin.action(description="Send a message to Discord")
def DiscordHook(modeladmin, request, queryset):
    discord = queryset
    url = "https://discord.com/api/webhooks/1272685297158848635/HwsNz7bQ55Nn55d7YxjjickEkt6GmUaHU5oNgNwmZqBnidCpJtCmxSA0Ppp5xG_4LnEa"
    for obj in discord:

        data = {
            "content": obj.discordContent,
            "username": "Codaqui BOT",
        }

        data["embeds"] = [
            {
                "description": obj.discordDescription,
                "title": obj.discordTitle,
                "thumbnail": {
                    "url": "https://avatars.githubusercontent.com/u/82526241"
                },
                "image": {"url": ""},
            }
        ]
        result = requests.post(url, json=data)
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))


# Register your models here.
class dicordServiceAdmin(admin.ModelAdmin):

    list_display = ("user", "content", "title", "description")
    actions = [DiscordHook]

    def description(self, obj):
        return obj.discordDescription

    def content(self, obj):
        return obj.discordContent

    def title(self, obj):
        return obj.discordTitle

    description.short_description = "Description"
    content.short_description = "Content"
    title.short_description = "Title"


admin.site.register(dicordService, dicordServiceAdmin)
