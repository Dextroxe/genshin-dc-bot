import asyncio

import genshin


__cache = genshin.Cache(maxsize=256, ttl=60)


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
        data = await gs._GenshinBattleChronicleClient__get_genshin("dailyNote", uid, cache=False)
        if data['transformer']:
            break
        await asyncio.sleep(0.5)

    await __cache.set(uid, data)

    return data
