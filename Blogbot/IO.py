import json
from filelock import FileLock
from pathlib import Path

blogfilename = '/path/Blogbot/blog.json'
showroomfilename = '/path/Blogbot/showroom.json'
progressfilename = '/path/Blogbot/blogProgress.txt'
lock = FileLock(blogfilename + '.lock')


def readData(filename):
    with open(filename, 'r', encoding="utf-8") as fp:
        return json.load(fp)


def writeData(data, filename):
    with open(filename, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)


def addData(group, member, id):
    data = readData(blogfilename)
    l = False
    if member == '*':
        for m, ids in data[group].items():
            if str(id) not in ids:
                data[group][m].append(str(id))
                sorted(data[group][m], key=lambda i: int(i))
                l = True
    else:
        if str(id) not in data[group][member]:
            data[group][member].append(str(id))
            sorted(data[group][member], key=lambda i: int(i))
            l = True
    writeData(data, blogfilename)
    if l:
        return True
    else:
        return False


def deleteData(group, member, id):
    data = readData(blogfilename)
    l = False
    if member == '*':
        for m, ids in data[group].items():
            if str(id) in ids:
                data[group][m].remove(str(id))
                sorted(data[group][m], key=lambda i: int(i))
                l = True
    else:
        if str(id) in data[group][member]:
            data[group][member].remove(str(id))
            sorted(data[group][member], key=lambda i: int(i))
            l = True
    writeData(data, blogfilename)
    if l:
        return True
    else:
        return False


def getBlogProgress():
    file = Path(progressfilename)
    file.touch(exist_ok=True)
    return file.read_text()


def appendBlogProgress(url):
    with open(progressfilename, 'a') as fp:
        print(url, file=fp)


if __name__ == '__main__':
    addData('乃木坂46', '樋口日奈', 396277982)
    deleteData('日向坂46', '丹生明里', 396277982)
