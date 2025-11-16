from pathlib import Path
import importlib.util
import subprocess

def load_python_config(config_path):
    config_path = Path(config_path).expanduser().absolute()
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    module_name = f"config_{config_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, config_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    
    return config_module


def get_installed_packages(command):
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    packages = result.stdout.strip().split('\n')
    return packages


def main() -> None:
    config = load_python_config("~/Manager/example/config.py").config

    print(config.base.installer)
    print(get_installed_packages(config.base.get_installed))


if __name__ == "__main__":
    main()

