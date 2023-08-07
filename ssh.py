import getpass
from fabric import Connection, Config


def init_ssh():

    print("Establishing SSH session, please provide connection details...")
    print("--------------------------------------------------------------")
    host = input("Please enter the desired host address: ")
    user = input("Please enter your username: ")
    password = getpass.getpass("Please enter your password: ")
    config = Config(overrides={'sudo': {'password': password}})
    shell = Connection(host=host, user=user, connect_kwargs={
                       'password': password}, config=config)
    return shell
