import asyncio
import io

from PIL import Image as Img
from aiohttp import ClientSession
from aiosocksy.connector import ProxyConnector, ProxyClientRequest
from filetype import guess_mime

from util.initializer import setting


class Session(object):
    def __init__(self, header: str | dict, proxy: bool = False):
        self.session = None
        if isinstance(header, dict):
            self.header = header
        else:
            self.header = {"User-Agent": f"AldotaiBot/1.0 {header}"}
        if proxy:
            self.proxy = setting["proxy"]
        else:
            self.proxy = None

    def pack(self):
        return (
            {
                "connector": ProxyConnector(
                    keepalive_timeout=True,
                    enable_cleanup_closed=True,
                    use_dns_cache=True,
                ),
                "request_class": ProxyClientRequest,
            }
            if self.proxy is not None
            else {}
        )

    async def get_json(self, url: str):
        async with ClientSession(**self.pack()) as session:
            async with session.get(url, headers=self.header, proxy=self.proxy) as resp:
                return await resp.json(content_type=None)

    async def download_file(self, url: str, save: str):
        result = await self.get_image(url)
        with open(save, mode="wb") as f:
            f.write(result["data_bytes"])
            f.close()

    async def get_image(self, url: str) -> dict:
        if url.startswith("file:"):
            return {"url": url}
        async with ClientSession(**self.pack()) as session:
            async with session.get(url, headers=self.header, proxy=self.proxy) as resp:
                data_byte = await resp.content.read()
                mime = guess_mime(data_byte[:261])
                if mime == "image/gif":
                    return {"data_bytes": data_byte}
                if round(resp.content_length / 1024) > 512:
                    foo = Img.open(io.BytesIO(data_byte))
                    if foo.width > foo.height:
                        foo.thumbnail(
                            (round(foo.width / 5 * 3), round(foo.width / 5 * 3))
                        )
                    else:
                        foo.thumbnail(
                            (round(foo.height / 5 * 3), round(foo.height / 5 * 3))
                        )
                    img_byte_arr = io.BytesIO()
                    foo.save(img_byte_arr, format="PNG", optimize=True, quality=85)
                    img_byte_arr = img_byte_arr.getvalue()
                    return {"data_bytes": img_byte_arr}
                return {"data_bytes": data_byte}


if __name__ == "__main__":

    async def main():
        # print(f"started main at {time.strftime('%X')}")
        obj = Session("test")
        await asyncio.gather(
            await asyncio.to_thread(
                obj.get_image, "https://img-home.csdnimg.cn/images/20201124032511.png"
            ),
            asyncio.sleep(1),
        )
        # print(f"finished main at {time.strftime('%X')}")

    asyncio.run(main())
