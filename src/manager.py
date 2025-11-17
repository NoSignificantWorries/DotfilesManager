import json
import sys
import subprocess
import configparser
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


def pth(path: str) -> Optional[Path]:
    p = Path(path).expanduser().absolute()

    logging(f"Received path {path} -> {p}", Log.DEBUG)

    if not p.exists():
        raise FileNotFoundError("Path is not exists")
    return p


def load_python_config(configpath: str) -> dict[str, list[str]] | dict[str, dict[str, list[str]]]:
    configpath_obj = pth(configpath)

    if not configpath_obj.is_file():
        raise FileNotFoundError(f"Path {configpath_obj} is not a file")

    with open(str(configpath_obj), "r") as file:
        logging(f"Trying load config file {configpath_obj}...", Log.INFO)
        data = json.load(file)

    return data


def get_installed_packages(command: list[str]) -> list[str]:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    packages = result.stdout.strip().split('\n')
    return packages


def parse_packages_file(filepath: str) -> Optional[dict[str, dict[str, list[str] | None]]]:
    filepath_obj = pth(filepath)

    if not filepath_obj.is_file():
        raise FileNotFoundError(f"Path {filepath_obj} is not a file")

    logging(f"Trying load packages file {filepath_obj}...", Log.INFO)

    try:
        parser = configparser.ConfigParser()
        parser.read(str(filepath_obj))
    except configparser.DuplicateOptionError:
        raise configparser.ParsingError(f"Duplicated option found in the file {filepath_obj}")
    except configparser.DuplicateSectionError:
        raise configparser.ParsingError(f"Duplicated section found in the file {filepath_obj}")

    if len(parser.sections()) == 0:
        logging("This file is empty. There is nothung to do.", Log.WARN)
        return None

    result = {}

    for section in parser.sections():
        install = None
        commands = None
        logging(f"Parsing section '{section}'", Log.INFO)
        for key in parser[section]:
            if key == "install":
                install = parser[section][key].strip()
                if len(install) == 0:
                    install = None
                    logging("Empty option 'install' in the section. Ignoring", Log.WARN)
                else:
                    install = install.split("\n")
                    logging(f"Parsed 'installing' option ({len(install)} elements)", Log.DEBUG)
            elif key == "commands":
                commands = parser[section][key].strip()
                if len(commands) == 0:
                    commands = None
                    logging("Empty option 'commands' in the section. Ignoring", Log.WARN)
                else:
                    commands = commands.split("\n")
                    logging(f"Parsed 'commands' option ({len(commands)} elements)", Log.DEBUG)
            else:
                logging(f"Unsupported option in the section '{section}': '{key}'. It will be ignored.", Log.WARN)
                continue
        if install is None and commands is None:
            logging(f"Section '{section}' in the file {filepath_obj} is empty. Ignoring.", Log.WARN)
            continue

        result[section] = {
            "install": install,
            "commands": commands
        }

    return result


def parse_dotignore_file(filepath: str) -> Optional[dict[str, list[str] | bool]]:
    filepath_obj = pth(filepath)

    if not filepath_obj.is_file():
        raise FileNotFoundError(f"Path {filepath_obj} is not a file")

    content_table = {
        "ignore": []
    }

    changed = False
    with open(str(filepath_obj), "r") as file:
        lines = file.read().split("\n")

        for i, line in enumerate(lines):
            if not bool(line) or line.startswith("#"):
                continue

            line = line.strip()
            if line.startswith("@"):
                line = line[1:].strip()
                if line in content_table.keys():
                    logging(f"Dublicate option '{line}' in the {filepath_obj} file (line {i + 1}).", Log.WARN)
                else:
                    content_table[line] = True
                    changed = True
            else:
                if line in content_table["ignore"]:
                    logging(f"Dublicate pattern '{line}' in the {filepath_obj} file (line {i + 1}).", Log.WARN)
                else:
                    content_table["ignore"].append(line)
                    changed = True

    if not changed:
        logging(f"Dotignore file {filepath_obj} is empty.", Log.WARN)
        return None

    return content_table


def main() -> int:
    Log.level = 0

    try:
        config_table = load_python_config("~/Manager/example/config.json")
        print(config_table)
    except AttributeError:
        logging("Config file is not attribute 'config' table.", Log.ERROR)
        return 1
    except Exception as err:
        logging(str(err), Log.ERROR)
        return 1


    # print(get_installed_packages(config.base.get_installed))

    try:
        packages = parse_packages_file("~/Manager/example/packages.base.ini")
        print(packages)
    except Exception as err:
        logging(str(err), Log.ERROR)
        return 1

    try:
        ignored = parse_dotignore_file("~/Manager/example/.dotignore")
        print(ignored)
    except Exception as err:
        logging(str(err), Log.ERROR)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

