import os.path
import json
import logging

from case_insensitive_dict import CaseInsensitiveDict

from auto_print.auto_print_execute import (
    PRINTER_CONFIG_PATH,
    install_ghostscript,
    config_logger,
    get_default_printer,
    get_printer_list,
)
from typing import Any


def input_choice(description: str, input_list: list[str], default: str):
    if not input_list:
        raise ValueError(
            "The list of possible inputs need to be defined and have a minimum length of one."
        )
    if not description:
        raise ValueError("The text should be defined.")
    if default not in input_list:
        raise ValueError(
            "The default input needs to be in the list of allowed choices."
        )
    possible_inputs = input_list[:]
    while True:
        print(description)
        print(f'Options: {", ".join(possible_inputs)}')
        text_in = input(f"Choose [{default}]:").strip()
        if not text_in:
            text_in = default
        text_in = next((e for e in input_list if e.lower() == text_in.lower()), "")
        if text_in:
            return text_in


def bool_decision(description: str, default: bool) -> bool:
    return (
        input_choice(description, ["yes", "y", "no", "n"], "yes" if default else "no")[
            0
        ]
        == "y"
    )


def print_element(name: str, config_element: dict[str, Any], index: int | None):
    printer = config_element.get("printer", get_default_printer())
    printing = config_element.get("print", False)
    suffix = config_element.get("suffix", None)
    prefix = config_element.get("prefix", None)

    if index is None:
        next_str = "    "
    else:
        next_str = f"{index + 1:>2}. "
    next_str += f'Prio config with name "{name}" is '
    if printing:
        next_str += f'printed on "{printer}"'
    else:
        next_str += "not printed."
    print(next_str)
    if suffix or prefix:
        next_str = "    Action is taken on all files "
        if prefix:
            next_str += f'starting with "{prefix}"'
            if suffix:
                next_str += " and "
        if suffix:
            next_str += f'ending with "{suffix}"'
        print(next_str)
    else:
        print("    This is executed for every file.")
    print(
        f"    The file should {'not ' if not config_element.get('show', True) else ''}be shown"
        f" and {'not be ' if not config_element.get('print', False) else ''}printed.\n"
        f"    The section is {'active' if config_element['active'] else 'inactive'}. "
    )


def print_config(config_object: CaseInsensitiveDict[str, dict]) -> None:
    print("The current config works as follows:")
    print()
    if config_object is None:
        print("No config found!")
        print()

        return

    for count, (name, config_element) in enumerate(config_object.items()):
        print_element(name, config_element, count)
        print()


def load_config() -> CaseInsensitiveDict[str, dict[str, Any]]:
    if not os.path.exists(PRINTER_CONFIG_PATH):
        return CaseInsensitiveDict[str, dict](data={})
    with open(PRINTER_CONFIG_PATH) as file:
        try:
            return CaseInsensitiveDict[str, dict](data=json.load(file))
        except FileNotFoundError:
            return CaseInsensitiveDict[str, dict](data={})


def save_config(config: CaseInsensitiveDict[str, dict[str, Any]]) -> None:
    with open(PRINTER_CONFIG_PATH, "w") as file:
        json.dump(dict(config), file)


def check_ghostscript():
    try:
        import ghostscript  # noqa: F401
    except RuntimeError as err:
        logging.error(err)
        install_ghostscript()


def add_section(config_object: CaseInsensitiveDict[str, dict[str, Any]]):
    print("Add a new section:")

    name: str
    config_element: dict[str, Any] = {}
    while True:
        name = ""
        while not name:
            name = input("Name:").strip()
            if name in config_object:
                print(
                    f'The name "{name}" is already in use. Choose another name that is not in use!'
                )
                name = ""

        # prefix
        print(
            "Filter by the start of a file.\n"
            'Something like "test_str" to filter all files who start with with "test_str"\n'
            "Can be empty if no filter of this type should be used!"
        )

        config_element["prefix"] = input("Type prefix:").strip()
        if config_element["prefix"] == "":
            del config_element["prefix"]

        # suffix
        print(
            "Filter by the end of a file.\n"
            'Something like "t_file.pdf" to filter all pdfs files who end with "t_file"\n'
            "Can be empty if no filter of this type should be used!"
        )
        print("If nothing is typed in no suffix will be defined.")
        config_element["suffix"] = input("Type suffix:").strip()
        if config_element["suffix"] == "":
            del config_element["suffix"]

        # optional print
        config_element["print"] = bool_decision(
            "Should the filtered file be printed automatically?",
            config_element.get("print", True),
        )

        if config_element["print"]:
            config_element["printer"] = input_choice(
                "Please choose a printer to use:",
                get_printer_list(),
                get_default_printer(),
            )
        else:
            del config_element["printer"]

        # show
        config_element["show"] = bool_decision(
            "Should the file be shown by the system default?",
            config_element.get("show", False),
        )

        # activate
        config_element["active"] = bool_decision(
            "Should the new section be activated?",
            config_element.get("active", True),
        )

        # show
        print()
        print_element(name, config_element, None)

        # check
        if bool_decision("Is the above section correct?", True):

            break
        print("Please make changes as needed.")


if __name__ == "__main__":
    config_logger()
    check_ghostscript()
    print("Welcome to the auto_print config generator!")
    print()

    config = load_config()
    print_config(config)

    while True:
        action = input_choice(
            "What actions should be taken?:",
            ["save", "s", "close", "c", "add", "a", "delete", "d", "show", "change"],
            "close",
        )

        print(f"Action: {action}")
        if action in ["s", "save"]:
            save_config(config)
            print("Config saved!")
        elif action in ["add", "a"]:
            add_section(config)
            print("add".upper())
        elif action in ["delete", "d"]:
            print("delete".upper())
        elif action in ["show"]:
            print()
            print_config(config)
        elif action in ["change"]:
            print("change".upper())
        elif action in ["close", "c"]:
            if load_config() == config:
                break
            if bool_decision(
                "There are unsaved changes. Please confirm with y/n if you want to close anyway[n]:",
                True,
            ):
                break
