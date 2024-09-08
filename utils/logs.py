import aiohttp, discord, json, time


with open("webhook.json") as f:
    webhooks = json.load(f)


async def get_api(api):
    """ Helps to get api """
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as response:
            try:
                response.raise_for_status()
            except Exception:
                return False
            else:
                return await response.json()


async def send_log(type: str, message: str, model: str = "default"):
    """ Advance logging system """
    if type not in ["success", "error", "info", "warning"]:
        raise ValueError("The entered type unknown enter valid type")
    if model not in webhooks:
        raise ValueError("The entered model unknown enter valid model")

    text = str(message).replace("*", "").replace("`", "")
    print(f"[{type.capitalize()}] {text}")

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhooks.get(model), session=session)
        await webhook.send(f"**[{type.capitalize()}]** <t:{round(time.time())}:f> {message}")