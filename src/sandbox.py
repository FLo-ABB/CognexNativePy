# This file is used to test the Cognex communication
from utils import open_socket, close_socket, login_to_cognex_system
from commands.file_and_job import load_file, get_file
from commands.execution_and_online import set_online, get_online


def load_job_if_not_current(job_name: str) -> None:
    if get_file() != job_name:
        if get_online() == 1:
            set_online(0)
        load_file(job_name)
        set_online(1)


def set_system_online() -> None:
    if get_online() == 0:
        set_online(1)


def main():
    s = open_socket('192.168.103.2')
    login_to_cognex_system(s, 'admin', '')
    load_job_if_not_current('job1.job')
    set_system_online()
    close_socket(s)


if __name__ == '__main__':
    main()
