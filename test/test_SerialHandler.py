import asyncio
import helper_test
import multiprocessing

from time import sleep
from resources_local import SerialHandler

sh = SerialHandler()


def process_serial_worker(iterations, qSerialFrom, qSerialTo):
    print('start process_serial_worker')
    for i in range(iterations, 0, -1):
        _msg_to_ser = qSerialTo.get()
        sh.write(_msg_to_ser)
        sh.read()
        if sh.data != '':
            qSerialFrom.put(sh.data)
        sleep(1)


def process_server(iterations, qSerialFrom, qSerialTo):
    print('start process_server')
    for i in range(iterations, 0, -1):
        qSerialTo.put(str(i))
        _msg_from_serial = qSerialFrom.get()
        print('read ' + _msg_from_serial)
        sleep(1)


def test_processes():
    print('test processes')
    qSerialTo = multiprocessing.Queue()
    qSerialFrom = multiprocessing.Queue()
    pW = multiprocessing.Process(target=process_serial_worker, args=(3, qSerialFrom, qSerialTo))
    pS = multiprocessing.Process(target=process_server, args=(3, qSerialFrom, qSerialTo))

    pW.start()
    pS.start()

    pW.join()
    pS.join()


async def async_write(iterations):
    for i in range(iterations, 0, -1):
        sh.write(str(i))
        print('write ' + str(i))
        sh.read()
        sleep(1)


async def async_read(iterations):
    for i in range(iterations, 0, -1):
        print('read ' + sh.data)
        sleep(1)


def test_async():
    iterations = 3
    asyncio.get_event_loop().run_until_complete(async_write(iterations))
    asyncio.get_event_loop().run_until_complete(async_read(iterations))


def test_write_read():
    print('test_write_read')
    t = 'c128,128'
    print('write ' + t)
    sh.write(t)
    sleep(1)
    sh.read()
    print(sh.data)
    sleep(1)
    print("write c0,0")
    sh.write("c0,0")
    asyncio.run(sh.read_async())
    print(sh.data)


if __name__ == '__main__':
    test_processes()
    #test_async()
    #test_write_read()
    print('done')