import os
import argparse
from timeit import default_timer as timer
from datetime import timedelta
from random import randbytes
import random
import string
import threading
import time

parser = argparse.ArgumentParser(description='Test files')
parser.add_argument('--folder', default='test', help='Folder where test should happen')
parser.add_argument('--repetitions', default='100', help='Repetitions of simple file test')
parser.add_argument('--bigfilesize', default='1000000', help='Size of bigfile test')

args = parser.parse_args()

def generate_random_file_name(N):
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits + "[](){}.-,", k=N))



def test_threaded_big_write(context, thread_no, iterations, test_folder, write_bytes):
    for iteration_no in range(0, iterations):
        test_file_1 = os.path.join(test_folder, "big_file_{}_{}.data".format(thread_no, iteration_no))
        print(f"Testing: {test_file_1}. Writing {write_bytes} bytes...")
        if os.path.isfile(test_file_1):
            os.remove(test_file_1)

        bytes_written = 0

        bytes_at_once = random.randint(0, 20000)

        while(bytes_written < write_bytes):
            with open(test_file_1, "ab") as f1:
                test_message = randbytes(min(bytes_at_once, write_bytes - bytes_written))
                bytes_written += f1.write(test_message)

        total_bytes_read = 0

        print(f"Testing: {test_file_1}. Reading {write_bytes} bytes...")

        with open(test_file_1, "rb") as f1:
            while True:
                bytes_read = f1.read(bytes_at_once)
                if len(bytes_read) == 0:
                    break
                total_bytes_read += len(bytes_read)

        if total_bytes_read != write_bytes:
            raise Exception(f"Bytes read not equal to bytes written. write_bytes: {write_bytes}, read_bytes: {total_bytes_read}")

        print(f"Finished thread {thread_no}")
        #os.remove(test_file_1)


def test_threaded_write(test_folder, threads_count, iterations, byte_size):
    data = "test"
    context = {}
    context["bytes_written"] = 0
    thread_list = []

    for thread_no in range(threads_count):
        t = threading.Thread(target=test_threaded_big_write, args=(context, thread_no, iterations, test_folder, byte_size))
        thread_list.append(t)
        t.start()
    for thread in thread_list:
        thread.join()


def test_simple_write(test_folder):
    test_file_1 = os.path.join(test_folder, generate_random_file_name(random.randint(5, 20)))
    test_message = randbytes(10000)

    with open(test_file_1, "wb") as f1:
        f1.write(test_message)

    with open(test_file_1, "rb") as f2:
        test_cmp = f2.read()
        if (test_message != test_cmp):
            raise Exception("test_simple_write failed")

    os.remove(test_file_1)

def test_big_write(test_folder, write_bytes):
    test_file_1 = os.path.join(test_folder, "big_file.data")
    if os.path.isfile(test_file_1):
        os.remove(test_file_1)

    bytes_written = 0

    bytes_at_once = 10000

    while(bytes_written < write_bytes):
        with open(test_file_1, "ab") as f1:
            test_message = randbytes(min(bytes_at_once, write_bytes - bytes_written))
            bytes_written += f1.write(test_message)

    total_bytes_read = 0

    with open(test_file_1, "rb") as f1:
        while True:
            bytes_read = f1.read(bytes_at_once)
            if len(bytes_read) == 0:
                break
            total_bytes_read += len(bytes_read)

    if total_bytes_read != write_bytes:
        raise Exception(f"Bytes read not equal to bytes written. write_bytes: {write_bytes}, read_bytes: {total_bytes_read}")

    os.remove(test_file_1)

test_folder = args.folder
if not os.path.isdir(test_folder):
    os.mkdir(test_folder)
if not os.path.isdir(test_folder):
    print(f"Directory {test_folder} does not exist")

test_threaded_write(args.folder, 10, int(args.repetitions), int(args.bigfilesize))

if 0:

    test_folder = args.folder
    if not os.path.isdir(test_folder):
        os.mkdir(test_folder)
    if not os.path.isdir(test_folder):
        print(f"Directory {test_folder} does not exist")

    print(f"Testing {test_folder} directory...")


    try:
        start = timer()
        for i in range(0, int(args.repetitions)):
            test_simple_write(test_folder)
        end = timer()
        diff = timedelta(seconds=end-start)
        print(f"test_simple_write completed: {diff}")
    except Exception as ex:
        print(f"test_simple_write failed: {ex}")


    try:
        start = timer()
        test_big_write(test_folder, int(args.bigfilesize))
        end = timer()
        diff = timedelta(seconds=end-start)
        print(f"test_big_write completed: {diff}")
    except Exception as ex:
        print(f"test_big_write failed: {ex}")


