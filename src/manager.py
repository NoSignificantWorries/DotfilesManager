import sys
import subprocess
import configparser
from typing import Optional






def get_installed_packages(command: list[str]) -> list[str]:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    packages = result.stdout.strip().split('\n')
    return packages


def parse_packages_file(filepath: str, config: dict) -> Optional[dict[str, dict[str, list[str] | None]]]:
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

    if "settings" in parser.sections():
        pass
    else:
        logging(f"Can't found 'settings' section in the file {filepath_obj}. Using default: '{config["default"]}'", Log.WARN)

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
        packages = parse_packages_file("~/Manager/example/packages/base.ini", config_table)
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

