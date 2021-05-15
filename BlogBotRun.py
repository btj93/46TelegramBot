import Blogbot.main as main
import asyncio


def run():
    with main.lock.acquire(30):
        asyncio.run(main.main())


if __name__ == '__main__':
    run()
