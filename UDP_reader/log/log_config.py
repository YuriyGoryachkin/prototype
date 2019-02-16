import sys
import logging

# import functools
""" Переделать под один логер """

"""  Логирование сервера """

log_server = logging.getLogger("Messenger_Geekbrains_Server")
log_server.setLevel(logging.DEBUG)

format_log_fh = logging.Formatter("%(levelname)-10s %(asctime)s - %(message)s")
format_log_sh = logging.Formatter('%(message)s')

sh_log_server = logging.StreamHandler(sys.stdout)
sh_log_server.setLevel(logging.DEBUG)
sh_log_server.setFormatter(format_log_sh)

fh_log_server = logging.FileHandler("log/server.log")
fh_log_server.setLevel(logging.INFO)
fh_log_server.setFormatter(format_log_fh)

log_server.addHandler(sh_log_server)
log_server.addHandler(fh_log_server)

""" Логирование клиента """

log_client = logging.getLogger("Messenger_Geekbrains_Client")
log_client.setLevel(logging.DEBUG)

sh_log_client = logging.StreamHandler(sys.stdout)
sh_log_client.setLevel(logging.DEBUG)
sh_log_client.setFormatter(format_log_sh)

fh_log_client = logging.FileHandler("log/client.log")
fh_log_client.setLevel(logging.INFO)
fh_log_client.setFormatter(format_log_fh)

log_client.addHandler(sh_log_client)
log_client.addHandler(fh_log_client)

NAME_LOGGER = 'Messenger'
logger = logging.getLogger(NAME_LOGGER)


def setup_logger(level=logging.INFO):
    """ Настройка логирования """
    format_logger_fh = logging.Formatter("%(levelname)-10s %(asctime)s - %(message)s")
    format_logger_sh = logging.Formatter('%(message)s')

    fh_logger = logging.FileHandler('log/mess')
    fh_logger.setLevel(level)
    fh_logger.setFormatter(format_logger_fh)

    sh_logger = logging.StreamHandler(sys.stdout)
    sh_logger.setLevel(logging.DEBUG)
    sh_logger.setFormatter(format_logger_sh)
    logger.addHandler(sh_logger)
    logger.addHandler(fh_logger)


def log(source):
    def deco_func(func):
        def wrapper(*args, **kwargs):
            fn_ret = func(*args, **kwargs)
            print('[{}]: {}({}, {})\nreturn: {}'.format(source, func.__name__, args, kwargs, fn_ret))
            return fn_ret

        return wrapper

    return deco_func
