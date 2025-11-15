# Don't Remove Credit Tg - @RS_WONER
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@RS_WONER
# Ask Doubt on telegram @RS_WONER

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

class Bot(Client):

    def __init__(self):
        super().__init__(
            "rssaverestricted",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        print(f'Bot Started Powered By @RS_WONER')
        print(f'Bot Username: @{me.username}')
        print(f'Bot ID: {me.id}')

    async def stop(self, *args):
        await super().stop()
        print('Bot Stopped Bye')

if __name__ == "__main__":
    Bot().run()