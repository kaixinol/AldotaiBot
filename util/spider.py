import asyncio
import io
import time
from asyncio import get_event_loop
from typing import Coroutine, Any

from PIL import Image as Img
from aiohttp import ClientSession


class Session(object):
    def __init__(self):
        self.session = None
        self.header = None

    def init(self, header: str | dict):
        if isinstance(header, dict):
            self.header = header
        else:
            self.header = {f"User-Agent": "AldotaiBot/1.0 {header}"}

    async def get_json(self, url: str):
        async with ClientSession() as session:
            async with session.get(url, headers=self.header) as resp:
                return await resp.json()

    async def download_file(self, url: str, save: str):
        async with ClientSession() as session:
            async with session.get(url, headers=self.header) as resp:
                with open(save, mode="wb") as f:
                    f.write(await resp.read())
                    f.close()

    async def get_image(self, url: str):
        async with ClientSession() as session:
            async with session.get(url, headers=self.header) as resp:
                if resp.content_type == "image/gif":
                    return {"url": url}
                else:
                    if round(resp.content_length / 1024**2) >= 1:
                        foo = Img.open(io.BytesIO(await resp.read()))
                        foo.thumbnail((600, 600))
                        img_byte_arr = io.BytesIO()
                        foo.save(img_byte_arr, format="PNG", optimize=True, quality=60)
                        img_byte_arr = img_byte_arr.getvalue()
                        return {"data_bytes": img_byte_arr}
                    else:
                        return {"data_bytes": await resp.read()}


if __name__ == "__main__":

    async def main():
        print(f"started main at {time.strftime('%X')}")
        obj = Session()
        obj.init("test")
        await asyncio.gather(
            await asyncio.to_thread(
                obj.get_image, "https://img-home.csdnimg.cn/images/20201124032511.png"
            ),
            asyncio.sleep(1),
        )
        print(f"finished main at {time.strftime('%X')}")

    asyncio.run(main())
