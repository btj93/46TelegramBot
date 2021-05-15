import asyncio
from Blogbot.IO import readData, getBlogProgress, appendBlogProgress, blogfilename, progressfilename
import telebot
import Blogbot.Scraper as Scraper
import Blogbot.telegram as telegram
import filelock

lock = filelock.FileLock(progressfilename + '.lock')


async def main():
    telegram.send_text(telegram.logchat_id, 'Start seaching Blogs')
    print('Start seaching Blogs')
    tasks = [
        (asyncio.create_task(Scraper.Nogi(2)), '乃木坂46'),
        # (asyncio.create_task(Scraper.Keya()), "欅坂46"),
        (asyncio.create_task(Scraper.Saku()), "櫻坂46"),
        (asyncio.create_task(Scraper.Hina()), '日向坂46')
    ]
    for task, group in tasks:
        for blog in await task:
            if blog.url not in getBlogProgress():
                blobs = asyncio.create_task(blog.getImgBlobs())
                print(blog.title, blog.name, blog.url)
                telegram.send_text(telegram.logchat_id, blog, disable_web_page_preview=True)
                if blog.name != "運営スタッフ":
                    # telegram.send_text(telegram.logchat_id, f'#{blog.name} 「{blog.title}」\n\n{blog.url}',
                    #                       disable_web_page_preview=True)
                    # for batch in await blobs:
                    #     telegram.send_media_group(telegram.logchat_id, list(map(lambda p: telebot.types.InputMediaPhoto(p), batch)))
                    for user in readData(blogfilename)[group][blog.name]:
                        telegram.send_text(user, f'#{blog.name} 「{blog.title}」\n\n{blog.url}',
                                          disable_web_page_preview=True)
                        for batch in await blobs:
                            telegram.send_media_group(user, list(map(lambda p: telebot.types.InputMediaPhoto(p), batch)))
                        telegram.send_text(telegram.logchat_id, f'sent #{blog.name} 「{blog.title}」\n\n{blog.url} to {user}',
                                          disable_web_page_preview=True)
                appendBlogProgress(blog.url)
    telegram.send_text(telegram.logchat_id, 'Finish seaching Blogs')
    print('Finish seaching Blogs')


if __name__ == '__main__':
    with lock.acquire(5):
        asyncio.run(main())
    # asyncio.run(test())
