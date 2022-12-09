import asyncio
import io
import time

from filetype import guess_mime
from PIL import Image as Img
from aiohttp import ClientSession


class Session(object):
    def __init__(self, header: str | dict):
        self.session = None
        if isinstance(header, dict):
            self.header = header
        else:
            self.header = {"User-Agent": f"AldotaiBot/1.0 {header}"}

    async def get_json(self, url: str):
        async with ClientSession() as session:
            async with session.get(url, headers=self.header) as resp:
                return await resp.json()

    async def download_file(self, url: str, save: str):
        result = await self.get_image(url)
        with open(save, mode="wb") as f:
            f.write(result["data_bytes"])
            f.close()

    async def get_image(self, url: str) -> dict:
        if url.startswith("file:"):
            return {"url": url}
        async with ClientSession() as session:
            async with session.get(url, headers=self.header) as resp:
                data_byte = await resp.content.read()
                mime = guess_mime(data_byte[:261])
                if mime == "image/gif":
                    return {"data_bytes": data_byte}
                else:
                    if round(resp.content_length / 1024) > 512:
                        foo = Img.open(io.BytesIO(data_byte))
                        foo.thumbnail((600, 600))
                        img_byte_arr = io.BytesIO()
                        foo.save(img_byte_arr, format="PNG", optimize=True, quality=60)
                        img_byte_arr = img_byte_arr.getvalue()
                        return {"data_bytes": img_byte_arr}
                    else:
                        return {"data_bytes": data_byte}


if __name__ == "__main__":

    async def main():
        print(f"started main at {time.strftime('%X')}")
        obj = Session("test")
        await asyncio.gather(
            await asyncio.to_thread(
                obj.get_image, "https://img-home.csdnimg.cn/images/20201124032511.png"
            ),
            asyncio.sleep(1),
        )
        print(f"finished main at {time.strftime('%X')}")

    asyncio.run(main())
