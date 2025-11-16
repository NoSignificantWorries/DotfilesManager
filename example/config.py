from types import SimpleNamespace as Table

config = Table(
    base=Table(
        installer=["sudo", "pacman", "-S"],
        flags=["--noconfirm"],
        updater=["sudo", "pacman", "-Suuy"],
        get_installed=["pacman", "-Qqe"],
        clear_cache=["sudo pacman -Scc"],
        clear_hanging=["sudo", "pacman", "-Rns", "$(pacman", "-Qdtq)"]
    ),
    main=Table(
        installer=["sudo", "paru", "-S"],
        flags=["--noconfirm"],
        updater=["sudo", "paru", "-Suuy"],
        get_installed=["paru", "-Qqe"],
        clear_cache=["sudo", "paru", "-Scc"],
        clear_hanging=["sudo", "paru", "-Rns", "$(paru", "-Qdtq)"]
    ),
)

