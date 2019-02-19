import os
import pickle
import sys

import fs
from fs import open_fs

import tornado.ioloop
import tornado.web

db = []


def buildDB(root, path='', orig_path=''):
    print(root, path)

    for obj in root.listdir(path):
        if obj[-4:] == '.zip':
            try:
                zip_fs = open_fs('zip://' + root.desc(obj))
                buildDB(zip_fs, orig_path=orig_path+'/'+obj)

            except fs.errors.ResourceNotFound:
                temp_file = 'C:/Windows/Temp/romcolview_' + obj
                temp_file = temp_file.replace('!', '_')

                with open(temp_file, 'wb') as f:
                    root.download(path + '/' + obj, f)

                buildDB(
                    open_fs('zip://' + temp_file),
                    orig_path=orig_path+'/'+obj
                )

                os.remove(temp_file)

        elif root.getdetails(path + '/' + obj).is_dir:
            new_path = path + '/' + obj
            buildDB(root, path=new_path, orig_path=orig_path)

        else:
            print('file found:', obj)

            full_path = orig_path + path + '/' + obj
            db.append(full_path)


class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render('index.html')


def makeApp():
    return tornado.web.Application([
        (r'/', MainHandler)
    ])


if __name__ == '__main__':
    if len(sys.argv) > 2:
        if sys.argv[1] == '-b':  # Build
            root = open_fs(sys.argv[2])

            buildDB(root, orig_path=sys.argv[2])
            pickle.dump(db, open('db', 'wb'))

    # app = makeApp()
    # app.listen(3000)
    # tornado.ioloop.IOLoop.current().start()
