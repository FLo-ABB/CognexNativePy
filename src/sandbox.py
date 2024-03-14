# This file is used to test the Cognex communication
from utils import open_socket, close_socket, log_cognex
from file_and_job import load_file
from execution_and_online import set_online, get_online


def main():
    s = open_socket('192.168.103.2')
    log_cognex(s, 'admin', '')
    if get_online() == 1:
        set_online(0)
    load_file('item1.job')
    close_socket(s)
