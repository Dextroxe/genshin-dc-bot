import asyncio

import genshin
from data.game.characters import characters_map
from common.logging import logger

__cache = genshin.Cache(maxsize=256, ttl=10)

def getCharacterName(character: genshin.models.BaseCharacter) -> str:
    chinese_name = None
    if (id := str(character.id)) in characters_map:
        chinese_name = characters_map[id].get('name')
    return chinese_name if chinese_name != None else character.name

__server_dict = {'os_usa': 'US', 'os_euro': 'Europea', 'os_asia': 'Asia', 'os_cht': 'Taiwan, Hong Kong and Macau',
     '1': 'Sky Island', '2': 'Sky Island', '5': 'World Tree', '6': 'America', '7': 'Europea', '8': 'Asia', '9': 'Taiwan, Hong Kong and Macau'}
def getServerName(key: str) -> str:
    return __server_dict.get(key)

async def get_notes(gs: genshin.Client, uid: int) -> dict:
    # The reason we have this utility method to get notes instead of using client.get_genshin_notes
    # is because the API sometimes returns empty teapot/transformer data.
    # One way to deal with this is to retry (max 5 times) until we see transformer data. Through
    # observation, teapot data is also available when transformer data is available.
    data = await __cache.get(uid)

    if data:
        return data

    # Call API with retries
    for _ in range(5):
        logger.info(f"Getting real-time notes for {uid}")
        data = await gs._request_genshin_record("dailyNote", uid, cache=False)
        if data['transformer']:
            break
        await asyncio.sleep(0.5)

    await __cache.set(uid, data)

    return data


