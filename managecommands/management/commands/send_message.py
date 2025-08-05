import requests
from django.core.management.base import BaseCommand, CommandError
from codaqui.settings import DISCORD_API_ENDPOINT, DISCORD_TOKEN

class Command(BaseCommand):
    help = "Send a message to a Discord channel using the bot token."

    def add_arguments(self, parser):
        parser.add_argument(
            '--provider','-p',
            type=str,
            choices=["discord", "slack"],
            help="Provider to send the message to. Currently only 'discord' is supported."
        )
        parser.add_argument(
            '--channel_id','-c', 
            type=str, 
            help="Discord channel ID where the message will be sent"
        )
        parser.add_argument(
            '--message','-m', 
            type=str, 
            help="Message content to send"
        )

    def handle(self, *args, **options):
        if str(options['provider']).upper() == "discord".upper():
            channel_id = options['channel_id']
            message = options['message']

            url = f"{DISCORD_API_ENDPOINT}/channels/{channel_id}/messages"
            headers = {
                "Authorization": f"Bot {DISCORD_TOKEN}",
                "Content-Type": "application/json"
            }
            json_data = {
                "content": message
            }

            self.stdout.write(f"Sending message to channel {channel_id}...")

            response = requests.post(url, headers=headers, json=json_data)

            if response.status_code in (200, 201):
                self.stdout.write(self.style.SUCCESS("Message sent successfully!"))
                self.stdout.write(str(response.json()))
            else:
                raise CommandError(f"Failed to send message: {response.status_code} - {response.text}")

        elif str(options['provider']).upper() == "slack".upper():
            raise CommandError("Slack support is not implemented yet.")
        else:
            raise CommandError("Invalid provider specified. Use 'discord' or 'slack'.")
                
