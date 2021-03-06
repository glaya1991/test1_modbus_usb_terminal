#!/usr/bin/env python3

import sys
import string  # , keyboard
from os import terminal_size
import serial.tools.list_ports
import serial
import time
import os
import random
import threading

import crc16_modbus


# ----- Help function ----------------- #

def help_func():
    print('')
    print('-h - help')
    print('-b xxxx - set baudrate as xxxx bit/s: 115200, 57600, 38400, 19200, 9600 etc.')
    print('\t default: 115200 bit/s')
    print('-p xxxx - set port name as xxxx: /dev/tty* or COMxx')
    print('\t default: /dev/ttyUSB0')
    print('\t or: COM7')
    print('-n xxxx - set received data threshold as xxxx byte: 4, 8, 16 etc.')
    print('\t default: 4 byte')
    print('-m xxxx - set data mode as xxxx: hex, dec, sym(symbol)')
    print('\t default: hex')
    print('-t xxxx - set time delay')
    print('\t default: 0.1')
    print('')
    print('example: sudo /../../prog_serial.py -b 115200 -p /dev/ttyUSB0 -n 10 -m hex')
    print('example: ../../prog_serial.py -b 115200 -p COM7 -n 10 -m hex')
    print('')


# ----- Exit function ----------------- #

def exit_func():
    print("exit!")
    global global_ch_exit
    global_ch_exit = 1
    # quit()
    return


# ----- Info function ----------------- #

def info_func():
    global _port
    global _baudrate
    global N_TX
    global mode
    print("Port=", _port, ', baudrate=', _baudrate, ', N_TX=', N_TX, ', mode=', mode)
    return


# ----- Send/receive function: MODBUS --------- #
def modbus_func():
    '''
    in1=input(">> data TX: ")

    # linux
    #ser.write(in1.encode()) #linux

    # windows
    in2 = in1.split(' ')
    in3 = []
    for val in in2:
        in3.append(int(val, 16))
    ser.write(in3)
    '''

    flag_en = 1
    query = []
    func = 0
    addr = 0
    num = 0
    data0 = 0

    try:
        id = int(input("id (in hex!): "), 16)
        query.append(id)
    except Exception:
        print("Wrong id/n")
        return

    try:
        func = int(input("func (in hex!): "), 16)
    except Exception:
        print("Wrong func/n")
        return

    if (func == 3) or (func == 4):
        query.append(func)
        try:
            addr = int(input("addr (in dec!): "))
        except Exception:
            print("Wrong addr/n")
            return
        query.append(((addr) >> 8) & 0xFF)
        query.append(((addr)) & 0xFF)

        try:
            num = int(input("num (in dec!): "))
        except Exception:
            print("Wrong num/n")
            return
        query.append(((num) >> 8) & 0xFF)
        query.append(((num)) & 0xFF)

        query_size = 6
        res = crc16_modbus.CRC16(query, query_size)
        query.append(res >> 8)
        query.append(res & 0xFF)

    elif (func == 16):
        query.append(func)
        try:
            addr = int(input("addr (in dec!): "))
        except Exception:
            print("Wrong addr/n")
            return
        query.append(((addr) >> 8) & 0xFF)
        query.append(((addr)) & 0xFF)

        try:
            num = int(input("num (in dec!): "))
        except Exception:
            print("Wrong num/n")
            return
        query.append(((num) >> 8) & 0xFF)
        query.append(((num)) & 0xFF)
        count = num << 1
        query.append(count)

        try:
            data0 = int(input("data_ho[0] (in dec!): "))
        except Exception:
            print("Wrong data/n")
            return
        for i in range(count):
            # query.append(random.randint(1, 100))
            query.append((data0 + i) & 0xFF)
        query_size = 7 + count
        res = crc16_modbus.CRC16(query, query_size)
        query.append(res >> 8)
        query.append(res & 0xFF)
    else:
        print("No such func/n")
        return

    print(''.join('{:02X} '.format(val) for val in query))
    ser.write(query)

    # read old version -- now in thread
    # n = ser.in_waiting
    # delay_cnt = 0
    # while n==0 and delay_cnt<100:
    #     n = ser.in_waiting
    #     delay_cnt += 1
    #     time.sleep(tdelay)
    #
    # out = []
    # delay_cnt = 0
    # #print(n)
    # while(n!=0) and  delay_cnt<100:
    #     out.extend(ser.read(n))
    #     delay_cnt += 1
    #     time.sleep(tdelay)
    #     n = ser.in_waiting
    #     #print(n)
    #
    # n = len(out)
    # if n != 0:
    #     print("n={:d}: ".format(n), end=' ')
    #
    #     if mode == 'hex':
    #         for i in out:
    #             print("{:x}".format(i), end=' ')
    #
    #     elif mode == 'dec':
    #         for i in out:
    #             print("{:d}".format(i), end=' ')
    #
    #     else:
    #         print(out, end=' ')
    #
    #     res = crc16_modbus.CRC16(out, n-2)
    #     if (res == (out[-1]+out[-2]*256)):
    #         print("__OK__", end = ' ')
    #     else:
    #         print("__!!! FAIL !!!__", end = ' ')
    #
    #     print("")
    # else:
    #     print('Wrong request')

    return


def modbus_func2(id, func, addr, num, data0):
    '''
    in1=input(">> data TX: ")

    # linux
    #ser.write(in1.encode()) #linux

    # windows
    in2 = in1.split(' ')
    in3 = []
    for val in in2:
        in3.append(int(val, 16))
    ser.write(in3)
    '''
    flag_en = 1
    query = []

    query.append(id)
    if (func == 0x03) or (func == 0x04):
        query.append(func)
        query.append(((addr) >> 8) & 0xFF)
        query.append(((addr)) & 0xFF)
        query.append(((num) >> 8) & 0xFF)
        query.append(((num)) & 0xFF)
        query_size = 6
        res = crc16_modbus.CRC16(query, query_size)
        query.append(res >> 8)
        query.append(res & 0xFF)

    elif (func == 0x10):
        query.append(func)
        query.append(((addr) >> 8) & 0xFF)
        query.append(((addr)) & 0xFF)
        query.append(((num) >> 8) & 0xFF)
        query.append(((num)) & 0xFF)
        count = num << 1
        query.append(count)
        for i in range(count):
            # query.append(random.randint(1, 100))
            query.append((data0 + i) & 0xFF)
        query_size = 7 + count
        res = crc16_modbus.CRC16(query, query_size)
        query.append(res >> 8)
        query.append(res & 0xFF)
    else:
        flag_en = 0

    if (flag_en):
        print(''.join('{:02X} '.format(val) for val in query))
        ser.write(query)

        # read data old version^ now in thread
        # n = ser.in_waiting
        # delay_cnt = 0
        # while n == 0 and delay_cnt < 100:
        #     n = ser.in_waiting
        #     delay_cnt += 1
        #     time.sleep(tdelay)
        #
        # out = []
        # delay_cnt = 0
        # # print(n)
        # while (n != 0) and delay_cnt < 100:
        #     out.extend(ser.read(n))
        #     delay_cnt += 1
        #     time.sleep(tdelay)
        #     n = ser.in_waiting
        #     # print(n)
        #
        # n = len(out)
        # if n != 0:
        #     print("n={:d}: ".format(n), end=' ')
        #
        #     if mode == 'hex':
        #         for i in out:
        #             print("{:x}".format(i), end=' ')
        #
        #     elif mode == 'dec':
        #         for i in out:
        #             print("{:d}".format(i), end=' ')
        #
        #     else:
        #         print(out, end=' ')
        #
        #     if (n>2):
        #         res = crc16_modbus.CRC16(out, n - 2)
        #         if res == (out[-1] + out[-2] * 256):
        #             print("__OK__", end=' ')
        #         else:
        #             print("__!!! FAIL !!!__", end=' ')
        #
        #     print("")
    return

def recv_msg():
    n = ser.in_waiting
    delay_cnt = 0
    while n == 0 and delay_cnt < 10:
        n = ser.in_waiting
        delay_cnt += 1
        time.sleep(tdelay)

    out = []
    delay_cnt = 0
    # print(n)
    while (n != 0) and delay_cnt < 10:
        out.extend(ser.read(n))
        delay_cnt += 1
        time.sleep(tdelay)
        n = ser.in_waiting
        # print(n)

    char_pt = ord('.')
    n = len(out)
    if n != 0:
        print("n={:d}: ".format(n), end=' ')

        if mode == 'hex':
            for i in out:
                print("{:x}".format(i), end=' ')

        elif mode == 'dec':
            for i in out:
                print("{:d}".format(i), end=' ')

        elif mode == 'sym':
            for i in out:
                try:
                    if (i == 0xa) or (i == 0xd): i = char_pt  # doesn't work, if <14
                    print(chr(i), end='')
                except:
                    print('x', end=' ')

            print('\r\n', out, end=' ')

        else:
            print(out, end=' ')

    return out

def func_recv():
    while True:
        msg_recv = recv_msg()
        n = len(msg_recv)
        if (n > 2):
            res = crc16_modbus.CRC16(msg_recv, n - 2)
            if res == (msg_recv[-1] + msg_recv[-2] * 256):
                print("__OK__", end=' ')
            else:
                print("__!!! FAIL !!!__", end=' ')
        if(n>0):
            print("\r\n")

    return


# ------------------------------------- #
#        MAIN                           #
# ------------------------------------- #

# linux:
# _port = '/dev/ttyUSB0'

# Win
_port = 'COM7'
_baudrate = 115200
N_TX = 512
mode = 'hex'
dict_mode = {'1': 'hex', '2': 'dec', '3': 'sym'}

tdelay = 0.001
_wr_en = 0

# available com ports
comlist = serial.tools.list_ports.comports()
for port, desc, hwid in sorted(comlist):
    print("{}: {} [{}]".format(port, desc, hwid))

# ----- Set serial port parametrs ----- #

N_arg = len(sys.argv)
# print('Number of arguments:', N_arg, 'arguments.')
# print(sys.argv)

cnt = 0
if N_arg > 1:  # if program has arguments in command line
    for i in range(N_arg):
        if sys.argv[i] == '-b':
            try:
                _baudrate = int(sys.argv[i + 1])
                cnt += 1
            except Exception:
                print("Wrong Baudrate! Print -h for help!")
                exit()

        elif sys.argv[i] == '-p':
            try:
                _port = sys.argv[i + 1]
                cnt += 1
            except Exception:
                print("Wrong Port! Print -h for help!")
                exit()

        elif sys.argv[i] == '-n':
            try:
                N_TX = int(sys.argv[i + 1])
                cnt += 1
            except Exception:
                print("Wrong N_TX! Print -h for help!")
                exit()

        elif sys.argv[i] == '-m':
            try:
                mode = (sys.argv[i + 1])
                cnt += 1
                if ((mode in dict_mode.values()) == False):
                    print("Wrong mode! Print -h for help!")
                    exit()
            except Exception:
                print("Wrong mode!")
                exit()

        elif sys.argv[i] == '-t':
            try:
                tdelay = float(sys.argv[i + 1])
                cnt += 1
            except Exception:
                print("Wrong delay time!")
                exit()

        elif sys.argv[i] == '-w':
            try:
                _wr_en = int(sys.argv[i + 1])
                cnt += 1
            except Exception:
                print("Wrong wr_en!")
                exit()

        elif sys.argv[i] == '-h':
            help_func()
            exit()

        else:
            pass

    if (cnt > 1) and (cnt == ((N_arg - 1) >> 1)):
        print("Arguments commited")
    else:
        print("Arguments not commited"); exit()

else:  # if program has _no_ arguments in command line

    # !!!! UNCOMMENT ME  !!!!
    # input1 = input(">> Default settings? - yes=1, no=2, q=quit, h=help\n>>")  # /dev/ttyUSB0
    input1 = 1

    if (input1 == '2'):
        _port = input(">> Port: ")
        _baudrate = input(">> Baudrate: ")
        _N_TX = input(">> N_TX: ")
        try:
            N_TX = int(_N_TX)
        except Exception:
            print("Wrong! (default: N_TX=4)")
            N_TX = 4

    elif (input1 == 'q'):
        exit()

    elif (input1 == 'h'):
        help_func()
        exit()

    else:
        pass

    # !!!! UNCOMMENT ME  !!!!
    # in1 = input(">> Mode: HEX=1, DEC=2, SYMBOL=3, q=quit: ")
    in1 = 1

    mode = dict_mode.get(in1)
    if mode == None:
        mode = 'hex'
    if in1 == 'q':
        exit()


wr_en = _wr_en
# write rx data:
if wr_en == 1:
    t0 = time.localtime()
    date0 = '{:04d}{:02d}{:02d}'.format(t0.tm_year, t0.tm_mon, t0.tm_mday)
    time0 = '{:02d}:{:02d}:{:02d}'.format(t0.tm_hour, t0.tm_min, t0.tm_sec)
    filename = os.getcwd() + '/rxdata_' + date0 + '_' + time0 + '.txt'
    file1 = open(filename, 'w')
    print(filename, '\r\n')


print('!!! Exit - Ctrl+Shift+C !!!')

# ----- Open serial port -------------- #

try:
    ser = serial.Serial(
        port=_port,  # '/dev/ttyUSB0', 'COM1'
        baudrate=_baudrate,
        # parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
except Exception:
    print('No such port!')
    exit()

if (ser.isOpen() == True):
    print("Port is already opened!")
else:
    try:
        ser.open()
    except Exception:
        print('Cannot open port!')
        exit()
    print("Port is open!")

print(ser.name)
n = ser.in_waiting
out = ser.read(n)  # first read???


thread_recv = threading.Thread(target=func_recv)
thread_recv.start()


# ----- main loop --------------------- #

# test write/read
test_en = 0
if test_en:
    Nblocks = 32
    n_num = 8
    n_addr = int(Nblocks/n_num)
    for cnt in range(1):
        modbus_func2(0x7f, 0x03, 0, Nblocks, 0)

        for i in range(n_addr):  # addr
            modbus_func2(0x7f, 0x10, i*n_num, n_num, 0x30 + i * 0x10)

        for i in range(n_addr):  # addr
            modbus_func2(0x7f, 0x03, i*n_num, n_num, 0)

        modbus_func2(0x7f, 0x03, 0, Nblocks, 0)


test_en = 1
if test_en:
    Nblocks = 1
    while True:
        modbus_func2(0x7f, 0x03, 0, Nblocks, 0)
        time.sleep(0.5)
        input("press")

        # modbus_func2(0x7f, 0x03, 0, Nblocks*2, 0)
        # time.sleep(2)
        #
        # modbus_func2(0x7f, 0x03, 0, Nblocks*3, 0)
        # time.sleep(2)
        #
        # modbus_func2(0x7f, 0x03, 0, Nblocks*4, 0)
        # time.sleep(2)

# test write/read for 2 mcu
test_en = 0
if test_en:
    id1 = 0x7f
    id2 = 0x1a
    Nblocks = 32
    n_num = 8
    n_addr = int(Nblocks/n_num)

    for cnt in range(10):
        modbus_func2(id1, 0x03, 0, Nblocks, 0)
        modbus_func2(id2, 0x03, 0, Nblocks, 0)

        for i in range(n_addr):  # addr
            modbus_func2(id1, 0x10, i*n_num, n_num, 0x30 + i * 0x10)
            modbus_func2(id2, 0x10, i*n_num, n_num, 0x34 + i * 0x10)

        for i in range(n_addr):  # addr
            modbus_func2(id1, 0x03, i*n_num, n_num, 0)
            modbus_func2(id2, 0x03, i*n_num, n_num, 0)

        modbus_func2(id1, 0x03, 0, Nblocks, 0)
        modbus_func2(id2, 0x03, 0, Nblocks, 0)


global_ch_exit = 0  # flag exit: if 1 - exit programm!

while global_ch_exit == 0:
    modbus_func()

