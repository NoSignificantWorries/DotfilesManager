import sys
import json
from typing import Optional
from pathlib import Path


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


class Log:
    DEBUG = (0, f"{Colors.GREEN}[DEBUG]{Colors.RESET}")
    INFO = (1, f"{Colors.BLUE}[INFO]{Colors.RESET}")
    WARN = (2, f"{Colors.YELLOW}[WARN]{Colors.RESET}")
    ERROR = (3, f"{Colors.RED}[ERROR]{Colors.RESET}")
    level = 0


def logging(msg: str, log: tuple[int, str]) -> None:
    log_level, log_marker = log
    if log_level >= Log.level:
        print(f"{log_marker}: {msg}", file=sys.stderr)


def error_handler(err_match=None, default_return=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                err_type = type(err).__name__
                if err_match and err_type in err_match:
                    logging(err_match[err_type], Log.ERROR)
                else:
                    logging(f"Unexpected error in function '{func.__name__}': {err_type} - {err}", Log.ERROR)
                return default_return
        return wrapper
    return decorator


def pth(path: str, check_file: Optional[bool] = None) -> Optional[Path]:
    path_ob = Path(path).expanduser().absolute()

    logging(f"Received path {path} -> {path_ob}", Log.DEBUG)

    if not path_ob.exists():
        raise FileNotFoundError(f"Path '{path_ob}' is not exists")
    if check_file is None:
        return path_ob
    if check_file and not path_ob.is_file():
        raise FileNotFoundError(f"Path '{path_ob}' is not a file")
    elif not check_file and not path_ob.is_dir():
        raise FileNotFoundError(f"Path '{path_ob}' is not a dir")
    return path_ob


@error_handler()
def load_packages_config(configpath: str):
    configpath_obj = pth(configpath, True)
    with open(str(configpath_obj), "r") as file:
        logging(f"Trying load config file {configpath_obj}...", Log.INFO)
        data = json.load(file)
    return data


if __name__ == "__main__":
    config_table = load_packages_config("~/Manager/example/config.json")

