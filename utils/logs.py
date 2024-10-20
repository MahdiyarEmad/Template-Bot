import aiohttp, discord, json, time, asyncio


with open("config.json") as f:
    webhooks = json.load(f)


async def send_log(type: str, message: str, model: str = "default", *, limit: int = 2000):
    """ Advance logging system """
    if type not in ["success", "error", "info", "warning", "debug"]:
        raise ValueError("The entered type unknown enter valid type")
    if model not in webhooks:
        raise ValueError("The entered model unknown enter valid model")

    model = "debug" if type == "debug" else model

    text = str(message).replace("*", "").replace("`", "")
    print(f"[{type.capitalize()}] {text}")

    content = f"**[{type.capitalize()}]** <t:{round(time.time())}:f> {str(message)}"

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhooks.get(model), session=session)
        for slice in [(content[i:i+limit]) for i in range(0, len(content), limit)]:
            await webhook.send(slice)
            await asyncio.sleep(1)


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