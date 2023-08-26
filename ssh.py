import getpass
from fabric import Connection, Config


def init_ssh():

    global host, user, password

    print("Establishing SSH session, please provide connection details...")
    print("--------------------------------------------------------------")
    if host is None:
        host = input("Please enter the desired host address: ")
    if user is None:
        user = input("Please enter your username: ")
    if password is None:
        password = getpass.getpass("Please enter your password: ")
    config = Config(overrides={'sudo': {'password': password}})
    shell = Connection(host=host, user=user, connect_kwargs={
                       'password': password}, config=config)
    return shell
