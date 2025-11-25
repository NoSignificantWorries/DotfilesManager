import json
import tomllib
import fnmatch
from pathlib import Path
from typing import Optional


def pth(path: str, not_exists_err: bool = True) -> Optional[Path]:
    path_obj = Path(path)
    if path.startswith("~"):
        path_obj = path_obj.expanduser()
    else:
        path_obj = path_obj.absolute()

    if not path_obj.exists():
        if not_exists_err:
            raise FileNotFoundError(f"Not found file '{path_obj}'")
        else:
            return None

    return path_obj


def open_path_handler(func):
    def wrapper(*args, **kwargs):
        kwargs_copy = kwargs.copy()

        if isinstance(kwargs["path"], str):
            kwargs_copy["path"] = pth(kwargs["path"])

        return func(*args, **kwargs_copy)
    return wrapper


@open_path_handler
def load_toml(*, path: str | Path):
    with open(path, "rb") as file:
        return tomllib.load(file)


@open_path_handler
def load_json(*, path: str | Path):
    with open(path, "r") as file:
        return json.load(file)


@open_path_handler
def load_text(*, path: str | Path):
    with open(path, "r") as file:
        return file.readlines()


def parse_lines(*, content: list[str], handler: dict, ignore: Optional[str] = None) -> dict:
    result = {}

    for line in content:
        line = line.strip()
        if not line:
            continue
        if ignore and line.startswith(ignore):
            continue
        for (name, handle) in handler.items():
            h = handle(line)
            if not h:
                continue
            if name in result.keys():
                result[name].append(h)
            else:
                result[name] = [h]
            break

    return result


@open_path_handler
def open_and_parse_text(*, path: str | Path, handler: dict, ignore: Optional[str] = None) -> dict:
    return parse_lines(content=load_text(path=path),
                       handler=handler,
                       ignore=ignore)


@open_path_handler
def parse_dirs_recursive(*, path: str | Path, config: dict) -> list[dict[str, str]]:
    links = []
    for file in path.iterdir():
        if match_patterns(string=file.name, patterns=ALWAYS_IGNORE):
            continue
        if file.name.startswith("."):
            continue
        if file.is_file():
            links.append({"from": str(file), "to": ""})
        if file.is_dir():
            links += parse_dirs_recursive(path=file, config=config)

    return links


def match_patterns(*, string: str, patterns: list[str]) -> bool:
    matches = [fnmatch.fnmatch(string, pattern) for pattern in patterns]
    return any(matches)


def main() -> None:
    toml_packages = load_toml(path="example/packages/base.toml")
    packages_config = load_json(path="example/packages/config.json")
    print(packages_config)

    links_config = load_json(path="example/links-config.json")

    print(links_config)

    path_list_handler = {
        "links": (lambda line: (lambda: print("ignoring")) if pth(line, False) is None else pth(line))
    }
    print(open_and_parse_text(path="example/packages/others", handler=path_list_handler, ignore="#"))

    dotignore_handler = {
        "flags": (lambda line: line[1:].strip() if line.startswith("@") else None),
        "patterns": (lambda line: line)
    }
    print(open_and_parse_text(path="example/.dotignore", handler=dotignore_handler, ignore="#"))

    # with open("res.json", "w") as file:
    #     res_parsing = parse_dirs_recursive(path="~/Hyprdots_main")
    #     json.dump(res_parsing, file, indent=2)


if __name__ == "__main__":
    main()

