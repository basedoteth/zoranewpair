import asyncio
from web3 import Web3
from telegram import Bot
from telegram.constants import ParseMode

# === CONFIG ===
WSS_RPC = "wss://7777777.rpc.thirdweb.com/9c81b72b9202b01b2df1f51492eda1d1"
TELEGRAM_TOKEN = "8064321992:AAHf55jbtHBKYzAfiv66f3BDXtZZam0Tlug"
TELEGRAM_CHAT_ID = "@zoracreatorcoins"
FACTORY_ADDRESS = "0x777777751622c0d3258f214F9DF38E35BF45baF3"

# === CoinCreated Event ABI ===
FACTORY_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "coin", "type": "address"},
            {"indexed": False, "internalType": "address", "name": "pool", "type": "address"},
            {"indexed": False, "internalType": "address", "name": "caller", "type": "address"},
            {"indexed": False, "internalType": "address", "name": "payoutRecipient", "type": "address"},
            {"indexed": False, "internalType": "address", "name": "platformReferrer", "type": "address"},
            {"indexed": False, "internalType": "address", "name": "currency", "type": "address"},
            {"indexed": False, "internalType": "string", "name": "name", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "symbol", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "uri", "type": "string"},
            {"indexed": False, "internalType": "uint8", "name": "version", "type": "uint8"}
        ],
        "name": "CoinCreated",
        "type": "event"
    }
]

# === TELEGRAM BOT INSTANCE ===
bot = Bot(token=TELEGRAM_TOKEN)

async def main():
    w3 = Web3(Web3.WebsocketProvider(WSS_RPC))
    print("🔌 Connected to Zora:", w3.isConnected())

    factory = w3.eth.contract(address=FACTORY_ADDRESS, abi=FACTORY_ABI)
    event_signature_hash = w3.keccak(text="CoinCreated(address,address,address,address,address,address,string,string,string,uint8)").hex()

    # Subscribe to CoinCreated logs from the factory
    subscription = w3.eth.filter({
        "address": FACTORY_ADDRESS,
        "topics": [event_signature_hash]
    })

    print("📡 Listening for CoinCreated events...")

    while True:
        try:
            for event in subscription.get_new_entries():
                decoded = factory.events.CoinCreated().processLog(event)

                coin_addr = decoded["args"]["coin"]
                name = decoded["args"]["name"]
                symbol = decoded["args"]["symbol"]

                zora_link = f"https://zora.co/coins/{coin_addr}"
                msg = (
                    f"🆕 *New Creator Coin on Zora!*\n\n"
                    f"*Name:* {name} ({symbol})\n"
                    f"*Address:* `{coin_addr}`\n"
                    f"[🔗 View on Zora ↗️]({zora_link})"
                )

                print(f"📢 Creator coin deployed: {name} ({symbol})")
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode=ParseMode.MARKDOWN)

            await asyncio.sleep(2)

        except Exception as e:
            print("⚠️ Error:", e)
            await asyncio.sleep(5)

# === ENTRY POINT ===
if __name__ == "__main__":
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Zora Creator bot is live!", parse_mode=ParseMode.MARKDOWN)
    asyncio.run(main())
    
