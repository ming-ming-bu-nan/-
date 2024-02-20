# coding=UTF-8
import os
import socket 
import time
import serial
import serial.tools.list_ports
from pathlib import Path
import chardet
import signal
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

#src file para
srcpath = 'src.bin'
dataIndex = 0
dataResidue = 0
dataIndexOld = 0
dataResidueOld = 0
startIndex = 0

#new file para
newFileIndex = 0
newDirName = ""
newFilePrefix = "recv"

#time para
localtime = 0

#uart para
curUart = ''
global ser

#eth
ipList = []
oneSendLen = 10240
serverAddr = '192.168.0.8'
serverPort = 777


def alarmHandle(para):
    print("........." + para)


def writeFileP(linkHnadle, srcData):
    global localtime,newDirName,newFileIndex
    global dataIndex, dataResidue, dataIndexOld, startIndex, dataResidueOld

    #create new file
    newFile = open(newDirName + '/' +  newFilePrefix + str(newFileIndex) + '.bin' , 'ab')

    while (dataIndex != 0) or (dataResidue != 0):
        if dataIndex != 0:
            linkHnadle.send(srcData[startIndex:startIndex + oneSendLen])

            reLen = oneSendLen
            reLenOld = 0
        
            while reLen != 0:

                #wait recv data
                buf = linkHnadle.recv(oneSendLen)

                #recv data save to file
                newFile.write(buf)

                #update need get data len
                reLen = reLen - len(buf)

                #data check
                # for i in range(0, len(buf)):
                #     if  srcData[startIndex + reLenOld + i] != buf[i]:
                #         print("cur data check fail", srcData[startIndex + i], buf[i])

                #         #create alarm
                #         scheduler = BlockingScheduler()
                #         scheduler.add_job(alarmHandle, "interval", args = ["data check fail"], seconds = 50)
                #         scheduler.start()

                reLenOld = reLenOld + len(buf)

            if reLenOld != oneSendLen:
                print("data recv fail, data len is: %d, recv len is : %d ",oneSendLen,len(buf))

                #create alarm
                scheduler = BlockingScheduler()
                scheduler.add_job(alarmHandle, "interval", args = ["data len error"], seconds = 50)
                scheduler.start()
                            
            startIndex = startIndex + oneSendLen
            dataIndex = dataIndex - 1

        else:
            #send residue file data
            linkHnadle.send(srcData[(dataIndexOld * oneSendLen):])

            reLen = dataResidue
            reLenOld = 0
        
            while reLen != 0:

                #wait recv data
                buf = linkHnadle.recv(oneSendLen)

                #recv data save to file
                newFile.write(buf)

                #update need get data len
                reLen = reLen - len(buf)

                #data check
                # for i in range(0, len(buf)):
                #     if  srcData[(dataIndexOld * oneSendLen) + reLenOld + i] != buf[i]:
                #         print("cur data check fail", srcData[startIndex + i], buf[i])

                #         #create alarm
                #         scheduler = BlockingScheduler()
                #         scheduler.add_job(alarmHandle, "interval", args = ["data check fail"], seconds = 50)
                #         scheduler.start()

                reLenOld = reLenOld + len(buf)

            if reLenOld != dataResidue:
                print("data recv fail, data len is: %d, recv len is : %d ",dataResidue,len(buf))

                #create alarm
                scheduler = BlockingScheduler()
                scheduler.add_job(alarmHandle, "interval", args = ["data len error"], seconds = 50)
                scheduler.start()

            dataResidue = 0

        #recv data save to file
        #newFile.write(buf)

    #close new file
    newFile.close()

    #updata global data
    startIndex = 0
    dataIndex = dataIndexOld
    dataResidue = dataResidueOld
    print("new file recv end")

    #close socket
    linkHnadle.close()


def writeFile(linkHnadle, srcData):
    global localtime,newDirName,newFileIndex
    global dataIndex, dataResidue, dataIndexOld, startIndex, dataResidueOld

    #create new file
    newFile = open(newDirName + '/' +  newFilePrefix + str(newFileIndex) + '.bin' , 'ab')

    while (dataIndex != 0) or (dataResidue != 0):
        if dataIndex != 0:
            linkHnadle.send(srcData[startIndex:startIndex + oneSendLen])

            startIndex = startIndex + oneSendLen
            dataIndex = dataIndex - 1
        else:
            #send residue file data
            linkHnadle.send(srcData[(dataIndexOld * oneSendLen):])

            dataResidue = 0

        #wait recv data
        buf = linkHnadle.recv(oneSendLen)

        #recv data save to file
        newFile.write(buf)

    #close new file
    newFile.close()
    startIndex = 0
    dataIndex = dataIndexOld
    dataResidue = dataResidueOld
    print("new file recv end")

    #close socket
    linkHnadle.close()


def checkFile():
    global srcpath, newDirName

    #create alarm
    scheduler = BackgroundScheduler()
    scheduler.add_job(alarmHandle, "interval", args = ["file checking"], seconds = 20)
    scheduler.start()

    #read src file
    file = open(srcpath,"rb")
    data = file.read()
    fileLen = len(data)

    #files = os.path.join(parent_path,"file_name")
    #newDirName = "2023_Sep_Wed_13_19_49_15"
    path = Path(newDirName + '/')
    files = [file.name for file in path.rglob("*.*")]

    print("file check start,all files num is :",len(files))

    #get start time
    startTime = time.time()

    for file_y in files:
        file_x = open(newDirName + '/' + file_y,"rb")

        data_x = file_x.read()
        if len(data_x) != fileLen:
            print(file_y)
            while(1):
                exit()

        for i in range(0, fileLen):
            if data_x[i] != data[i]:
                print("file check fail",file_y,i,)
                exit()

        file_x.close()

    #clode alarm print
    scheduler.shutdown()
    #scheduler.remove_all_jobs()

    #get end time
    endTime = time.time()

    print("file check success, one file data len is :", i ,"total time is :",endTime - startTime)


def uartReset(para):
    #uart check
    global curUart

    #get uart list
    # comList = list(serial.tools.list_ports.comports())

    # for port in comList:
    #     print(port.name)

    recvFlag = ""
    recvTime = 10

    try:  
       while(recvFlag != "ok"):
        if para.is_open:
            print("sys reset ......")
            para.write(b"\r")
            para.write(b"r app\r\n")

            for i in range(0, recvTime):
                data = para.readline()
                #char = 'ok'
                #if 'ok' in str(data)
                if chardet.detect(data)["encoding"] == "ascii":
                    data = data.decode('UTF-8').strip()
                    #print(data)
                    if data[1:] == "ok":
                        print("reset " + data)
                        recvFlag = data[1:]
                        break

            if recvFlag != "ok":
                print("sys reset fail")

                #create alarm
                # scheduler = BlockingScheduler()
                # scheduler.add_job(alarmHandle, "interval", args = ["sys reset fail"], seconds = 20)
                # scheduler.start()
    except:
        print("uart close")
        para.close()

def tcpHandle(para, para1):
    global oneSendLen, newFileIndex
    global localtime, newDirName
    global dataIndex, dataResidue, dataIndexOld, dataResidueOld
    global serverAddr, serverPort, curUart

    #test uart
    curUart = str(para1)
    
    hostName = socket.gethostname()
    print("wait server ready ......")

    #get all net card info
    while(1):
        addr_infos = socket.getaddrinfo(hostName, None)

        #get all ip info
        for addr in addr_infos:
            ipList.append(addr[4][0])

        if serverAddr in ipList:
            print("server is open")
            break

    #create socket
    handleSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    handleSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True)

    #bind socket to net card
    handleSocket.bind((serverAddr,serverPort))

    #listen server
    handleSocket.listen(128)

    #create new dir
    localtime = time.asctime(time.localtime(time.time()))
    newDirName = localtime[20:24] + '_' + localtime[4:7] + '_' + localtime[0:3] + '_' + localtime[8:10] + '_' + localtime[11:13] + '_' + localtime[14:16] + '_' + localtime[17:19] + '_' + str(para)
    os.mkdir(str(newDirName))

    #open src file
    file = open(srcpath,"rb")
    data = file.read()
    fileLen = len(data)

    #file subpackage
    dataIndex = fileLen // oneSendLen
    dataResidue = fileLen % oneSendLen
    dataIndexOld = dataIndex
    dataResidueOld = dataResidue

    #update file index
    newFileIndex = 0

    print("src file len:",fileLen)

    #get com num
    #port_list = []
    #port_lists = list(serial.tools.list_ports.comports())
    #for port in port_lists:
    #    port_list.append(port.devive)
    #print(port_list)

    #create uart
    ser = serial.Serial(curUart, 115200,timeout = 2)
    ser.bytesize = 8
    ser.stopbits = 1
    ser.parity = serial.PARITY_NONE

    for i in range(0, para):
        print("\r\n--------------wait a new link-------------")

        #accept a new link
        newSocket, clientAddr = handleSocket.accept()
        print(f"Connected by {clientAddr}")

        #file handle
        newFileIndex = newFileIndex + 1
        print("cur file num is :",newFileIndex)
        #writeFile(newSocket, data)
        writeFileP(newSocket, data)

        #uart reset
        uartReset(ser)
    
    #close uart
    ser.close()

    #recv file check
    checkFile()

    #server socket close
    handleSocket.close()

    print("server socket close")

def signal_handler(signal, frame):
    print("app exit")

    sys.exit(0)

if __name__ == '__main__':
    #reg exit signal handle
    signal.signal(signal.SIGINT, signal_handler)

    #uart test
    #uartReset()

    #only check file
    #checkFile()

    #enter test uart
    para2 = input("please enter the test uart: ")

    while True:
        #get user in str
        para = input("please enter the test num: ")

        if para.isdigit():
            #wait tcp link
            tcpHandle(int(para), para2)
