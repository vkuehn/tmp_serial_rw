import codecs
import helper_test
import multiprocessing

from resources_local import SerialHandler
from time import sleep

sh = SerialHandler()


def dummy(iterations=3):
    for i in range(iterations, 0, -1):
        print(i)
        sh.read()
        print(sh.data)
        sleep(1)


def test_read():
    print('test read')
    pD = multiprocessing.Process(target=dummy(), args=(3,))
    pD.start()
    pD.join()


def test_write():
    print('test_write')
    t = 'c128,128'
    sh.write(t)
    sh.read()
    print(sh.data)
    sleep(3)
    sh.write("c0,0")
    sh.read()
    print(sh.data)


if __name__ == '__main__':
    test_read()
    test_write()
    print('done')