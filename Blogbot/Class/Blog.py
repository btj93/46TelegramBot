import requests
from PIL import Image
from multiprocessing import Pool
import io

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Dnt": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
}
sizeLimit = 18000000
percentage = 0.6


def resize(image):
    w, h = image.size
    resizedImage = image.resize((int(w * percentage), int(h * percentage)), Image.LANCZOS)
    newArr = io.BytesIO()
    resizedImage.save(newArr, format=image.format)
    return newArr.getvalue()


def work(url):
    if "null" not in url:
        try:
            with requests.get(url, headers=headers) as response:
                if response.status_code == 200:
                    if 'dcimg.awalker.jp' not in url:
                        # try:
                        #     image = Image.open(io.BytesIO(response.content))
                        #     w, h = image.size
                        #     if w * h > sizeLimit:
                        #         return resize(image)
                        # except:
                        return response.content
                    else:
                        with requests.get(url.replace('/v/', '/i/'), headers=headers,
                                          cookies=response.cookies) as response2:
                            if response2.status_code == 200:
                                # try:
                                #     image = Image.open(io.BytesIO(response2.content))
                                #     w, h = image.size
                                #     if w * h > sizeLimit:
                                #         return resize(image)
                                # except:
                                return response2.content
        except Exception as e:
            print(e)


class Blog:

    def __init__(self, title, name, url, imgUrlList):
        self.title = title
        self.name = name
        self.url = url
        self.imgUrlList = imgUrlList

    def __repr__(self):
        return f'{self.title} {self.name}\n{self.url}\nImages:{len(self.imgUrlList)}'

    async def getImgBlobs(self):
        with Pool() as pool:
            imgs = pool.map(work, self.imgUrlList)
            return [imgs[i:i + 10] for i in range(0, len(imgs), 10)]
