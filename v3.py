import datetime
import queue
import threading
import requests
import logging
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
warnings.filterwarnings("ignore")

# D:/PycharmProjects/selectSeat
logging.basicConfig(filename='../LOG/' + __name__ + '.log',
                    format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', level=logging.ERROR, filemode='a',
                    datefmt='%Y-%m-%d %I:%M:%S %p')

headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Connection': 'close'
   }

r = threading.Lock()
q = queue.Queue()

testseat = []
# testseat = []

select_url = "https://10.21.95.57/ClientWeb/pro/ajax/reserve.aspx"
login_url = "https://10.21.95.57/ClientWeb/pro/ajax/login.aspx"
time1 = datetime.datetime.now() + datetime.timedelta(days=1)
tom = time1.strftime("%Y-%m-%d")
end = time1.strftime("%Y-%m-%d") + " 22:00"
week = time1.strftime('%w')
begin = tom + " 08:00"
startTime = begin.split()[-1].split(':')[0] + begin.split()[-1].split(':')[1]
endTime = end.split()[-1].split(':')[0] + end.split()[-1].split(':')[1]

def killseat(id,devId):
    login_data = {
        'id': id,
        'pwd': id,
        'act': 'login'
    }
    param = {
        'dialogid': '',
        'dev_id': devId,
        'lab_id': '',
        'kind_id': '',
        'room_id': '',
        'type': 'dev',
        'prop': '',
        'test_id': '',
        'term': '',
        'number': '',
        'classkind': '',
        'test_name': '',
        'start': begin,
        'end': end,
        'start_time': startTime,
        'end_time': endTime,
        'up_file': '',
        'memo': '',
        'act': 'set_resv',
    }
    session = requests.Session()
    r1 = session.post(login_url, headers=headers, data=login_data, verify=False)
    r.acquire()
    r2 = session.get(select_url, headers=headers, params=param, verify=False)
    r.release()
    q.put(login_data['id'] + r2.text + str(datetime.datetime.now()))
    session.close()

def killTime():
    Time = datetime.datetime.now()
    killtime = datetime.datetime.strptime(Time.strftime("%Y-%m-%d") + " 12:00:00.000", "%Y-%m-%d %H:%M:%S.%f")
    killtime_ms = int(time.mktime(killtime.timetuple()) * 1000.0 + killtime.microsecond / 1000)
    return killtime_ms

def localTime():
    return int(round(time.time() * 1000))

def init(seat,id):
    threads = []
    for devid in seat:
        threads.append(threading.Thread(target=killseat, args=(id, devid)))
    return threads

def runkillseat(testseat,id):
    count = 0
    print(id + ' ----------------------------程序开始执行-----------------------------')
    while True:
        if (localTime() - killTime() > 20000):
            print("{}一共抢座{}次".format(id,str(count)))
            print(id + ' ----------------------------程序执行结束-----------------------------')
            quit()
        elif (0 <= (localTime() - killTime())):
            threadpool = init(testseat,id)
            for t in threadpool:
                try:
                    t.start()
                except Exception as e:
                    logging.exception(e)
                    pass
                continue
            for _ in range(len(testseat)):
                print(q.get())
            count += 1
        elif ((killTime() - localTime()) > 30000):
            print(id + " 预约时间未到，等待中。。。。。")
            time.sleep(20)
        else:
            print(id + " 预约时间未到，等待中。。。。。")
            time.sleep(0.05)

if __name__ == '__main__':
    time1 = time.time()
    _processes = []
    _process = multiprocessing.Process(target=runkillseat, args=(testseat,""))
    _process.start()
    _processes.append(_process)
    _process = multiprocessing.Process(target=runkillseat, args=(testseat, ""))
    _process.start()
    _processes.append(_process)
    # _process = multiprocessing.Process(target=runkillseat, args=(testseat, ""))
    # _process.start()
    # _processes.append(_process)
    # _process = multiprocessing.Process(target=runkillseat, args=(testseat, ""))
    # _process.start()
    # _processes.append(_process)
    _process = multiprocessing.Process(target=runkillseat, args=(testseat, ""))
    _process.start()
    _processes.append(_process)
    for _process in _processes:
        _process.join()
    time2 = time.time()
    print("time consume {} s".format(time2 - time1))
