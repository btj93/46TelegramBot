import requests
from pyquery import PyQuery as pq
import asyncio
from Blogbot.Class import Blog


async def Nogi(pages=1):
    result = []
    for i in range(pages):
        with requests.get(f'http://blog.nogizaka46.com/?p={i + 1}', headers=Blog.headers) as response:
            if response.status_code == 200:
                for item in pq(response.content)('div.right2').find('h1.clearfix').items():
                    title = item('a[href]').text()
                    name = item('span.author').text()
                    url = item('a[href]').attr('href')
                    imgUrlList = []
                    with requests.get(url, headers=Blog.headers) as response2:
                        if response2.status_code == 200:
                            for img in pq(response2.content)('div.entrybody').find('img[src]').items():
                                if img.closest('a[href]') and img.closest('a[href]').attr('href') != '' and 'http' in img.closest('a[href]').attr('href'):
                                    imgUrlList.append(img.closest('a[href]').attr('href'))
                                elif img.attr('src') != '' and not img.closest('div.comments') and 'http' in img.attr('src'):
                                    imgUrlList.append(img.attr('src'))
                            result.append(Blog.Blog(title, name, url, imgUrlList))
    return reversed(result)



async def Keya(pages=1):
    result = []
    for i in range(pages):
        with requests.get(f'https://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&page={i}&cd=member',
                          headers=Blog.headers) as response:
            if response.status_code == 200:
                d = pq(response.content)('div.box-main')
                for item in d.find('article').items():
                    imgUrlList = []
                    for i in item('div.box-article').find('img[src]').items():
                        if i.attr('src') != '':
                            imgUrlList.append(i.attr('src'))
                    result.append(Blog.Blog(item('h3 > a').text(), item('p.name').text().replace(' ', ''),
                                            'https://www.keyakizaka46.com' + item('h3 > a').attr('href'), imgUrlList))
    return reversed(result)


async def Hina(pages=1):
    result = []
    for i in range(pages):
        with requests.get(f'https://www.hinatazaka46.com/s/official/diary/member/list?ima=0000&page={i}&cd=member',
                          headers=Blog.headers) as response:
            if response.status_code == 200:
                d = pq(response.content)('div.l-maincontents--blog')
                for item in d.find('div.p-blog-article').items():
                    imgUrlList = []
                    for i in item('div.c-blog-article__text').find('img[src]').items():
                        if i.attr('src') != '':
                            imgUrlList.append(i.attr('src'))
                    result.append(Blog.Blog(item('div.c-blog-article__title').text(),
                                            item('div.c-blog-article__name').text().replace(' ', ''),
                                            'https://www.hinatazaka46.com' + item('a.c-button-blog-detail').attr(
                                                'href'), imgUrlList))
    return reversed(result)


async def Saku(pages=1):
    result = []
    for i in range(pages):
        with requests.get(f'https://sakurazaka46.com/s/s46/diary/blog/list?ima=0450&page={i}&cd=blog',
                          headers=Blog.headers) as response:
            if response.status_code == 200:
                d = pq(response.content)('ul.com-blog-part')
                for item in d.find('li.box').items():
                    title = item('h3.title').text()
                    name = item('p.name').text().replace(' ', '')
                    url = 'https://sakurazaka46.com' + item('a[href]').attr('href').split('?')[0] + '?ima=0000&cd=blog'
                    imgUrlList = []
                    with requests.get(url, headers=Blog.headers) as response2:
                        if response2.status_code == 200:
                            for i in pq(response2.content)('div.box-article').find('img[src]').items():
                                if i.attr('src') != '' and "null" not in i.attr('src'):
                                    imgUrlList.append('https://sakurazaka46.com' + i.attr('src'))
                            result.append(Blog.Blog(title=title, name=name,
                                            url=url, imgUrlList=imgUrlList))
    return reversed(result)


if __name__ == '__main__':
    task = asyncio.run(Nogi(3))
    for x in task:
        print(x)
    task = asyncio.run(Keya())
    for x in task:
        print(x)
    task = asyncio.run(Hina())
    for x in task:
        print(x)
    task = asyncio.run(Saku(1))
    for x in task:
        print(x)
