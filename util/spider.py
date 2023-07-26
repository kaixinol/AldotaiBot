import io

from aiohttp import ClientSession
from aiosocksy.connector import ProxyClientRequest, ProxyConnector
from filetype import guess_mime
from PIL import Image as Img

from util.initializer import setting


class Session(object):
    def __init__(self, header: str | dict, proxy: bool = False):
        self.session = None
        if isinstance(header, dict):
            self.header = header
        else:
            self.header = {"User-Agent": f"{setting['name']}/1.0 {header}"}
        if not proxy or setting["proxy"] is None:
            self.proxy = None
        else:
            self.proxy = setting["proxy"]
    def pack(self):
        return (
            {
                "connector": ProxyConnector(
                    keepalive_timeout=True,
                    enable_cleanup_closed=True,
                    use_dns_cache=True,
                ),
                "request_class": ProxyClientRequest,
                "cookies": None
            }
            if self.proxy is not None
            else {"cookies": None}
        )

    async def get_json(self, url: str, cookie=None):
        async with ClientSession(**{**self.pack(), "cookies": cookie}) as session:
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
                if round(resp.content_length / 1024) > 1024:
                    foo = Img.open(io.BytesIO(data_byte))
                    if foo.width > 2000 or foo.height > 2000:
                        foo.thumbnail((1000, 1000))
                    else:
                        if foo.width > foo.height:
                            foo.thumbnail((round(foo.width / 2), round(foo.width / 2)))
                        else:
                            foo.thumbnail(
                                (round(foo.height / 2), round(foo.height / 2))
                            )
                    img_byte_arr = io.BytesIO()
                    foo.save(img_byte_arr, format="PNG", optimize=True, quality=85)
                    img_byte_arr = img_byte_arr.getvalue()
                    return {"data_bytes": img_byte_arr}
                return {"data_bytes": data_byte}

    async def get_cookie(self, url, kw: dict = None):
        async with ClientSession(headers=self.header) as session:
            async with session.post(url, data=kw) as resp:
                return resp.cookies

    async def post(self, url, kw: dict = None, cookie=None):
        async with ClientSession(headers=self.header, cookies=cookie) as session:
            async with session.post(url, data=kw) as resp:
                return await resp.json()
