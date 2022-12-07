import os.path
import json
import logging
import webbrowser

from case_insensitive_dict import CaseInsensitiveDict

from auto_print.auto_print_execute import (
    PRINTER_CONFIG_PATH,
    install_ghostscript,
    configure_logger,
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
        next_str = "    Config"
    else:
        next_str = f"{index + 1:>2}. Prio config"
    next_str += f' section with name "{name}" '
    if printing:
        next_str += f'prints on "{printer}"'
    else:
        next_str += "does not print."
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


def print_configuration(config_object: CaseInsensitiveDict[str, dict]) -> None:
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


def save_config(config_object: CaseInsensitiveDict[str, dict[str, Any]]) -> None:
    with open(PRINTER_CONFIG_PATH, "w") as file:
        json.dump(dict(config_object), file)
    print("Config saved!")


def check_ghostscript():
    try:
        import ghostscript  # noqa: F401
    except RuntimeError as err:
        logging.error(err)
        install_ghostscript()


def edit_section(
    name: str, config_element: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    while True:
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
            return name, config_element
        print("Please make changes as needed.")


def create_section(
    config_object: CaseInsensitiveDict[str, dict[str, Any]]
) -> tuple[str, dict[str, Any]]:
    config_element: dict[str, Any] = {}
    name = ""
    while not name:
        name = input("Name:").strip()
        if name in config_object:
            print(
                f'The name "{name}" is already in use. Choose another name that is not in use!'
            )
            name = ""
        if name.lower() in ["cancel", "c"]:
            print(f'The name "{name}" is not valid. Please choose again!')
            name = ""
    return edit_section(name, config_element)


def insert_section(
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
    name_to_add: str,
    section_to_add: dict[str, Any],
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    for insert_pos, (name, section) in enumerate(config_object.items()):
        print(f"Insert Position {insert_pos} ->")
        print_element(name, section, None)
    end_pos = len(config_object.keys())
    print(f"Insert Position {end_pos} ->")
    print()

    insert_str: str = input_choice(
        "Please choose where to add the section or choose cancel to cancel this action:",
        ["start"] + [str(n) for n in range(end_pos + 1)] + ["end", "cancel", "c"],
        "end",
    )
    if insert_str == "end":
        insert_str = str(end_pos)
    elif insert_str == "start":
        insert_str = "0"
    elif insert_str in ["cancel", "c"]:
        print_configuration(config_object)
        return config_object

    key_list = list(config_object.keys())

    key_list.insert(int(insert_str), name_to_add)
    config_object[name_to_add] = section_to_add
    config_object = CaseInsensitiveDict[str, dict[str, Any]](
        {name: config_object[name] for name in key_list}
    )
    print_configuration(config_object)
    return config_object


def add_section(
    config_object: CaseInsensitiveDict[str, dict[str, Any]]
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    print("Add a new section:")
    new_name, new_section = create_section(config_object)
    return insert_section(config_object, new_name, new_section)


def delete_section(
    config_object: CaseInsensitiveDict[str, dict[str, Any]]
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Deletes a specified section.

    Args:
        config_object: A configurations object.

    Returns:
        The newly generated/edited config_object.
    """
    if not config_object:
        print("There are no section to delete.")
        return config_object
    print_configuration(config_object)
    delete_object = input_choice(
        "Chose what section to delete or to cancel the operation!",
        list(config_object.keys()) + ["cancel", "c"],
        "cancel",
    )
    if delete_object in ["cancel", "c"]:
        print("Cancel delete object!")
        return config_object

    print(f'Deleting section "{delete_object}"')
    config_object = CaseInsensitiveDict[str, dict[str, Any]](
        {
            name: section
            for name, section in config_object.items()
            if name != delete_object
        }
    )
    print_configuration(config_object)
    return config_object


def change_section_position(
    config_object: CaseInsensitiveDict[str, dict[str, Any]]
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Changes the filter order.

    Args:
        config_object: A configurations object.

    Returns:
        The newly generated/edited config_object.
    """
    section_names = list(config_object.keys())
    if not section_names:
        print("There is no section to edit.")
        return config_object

    name_of_section = input_choice(
        "Choose the section to edit:",
        section_names,
        section_names[0],
    )
    temp_config = CaseInsensitiveDict[str, dict](
        data={
            k: v
            for k, v in config_object.items()
            if name_of_section.lower() != k.lower()
        }
    )
    return insert_section(temp_config, name_of_section, config_object[name_of_section])


def edit_section_command(
    config_object: CaseInsensitiveDict[str, dict[str, Any]]
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Edits a section in the configuration.

    Args:
        config_object: A configurations object.

    Returns:
        The newly generated/edited config_object.
    """

    section_names = list(config_object.keys())
    if not section_names:
        print("There is no section to edit.")
        return config_object

    choice = input_choice(
        "Choose the section to edit:",
        section_names,
        section_names[0],
    )

    print()
    print("Redefine the following section section\n")
    print_element(choice, config_object[choice], None)

    _, config_object[choice] = edit_section(choice, config_object[choice])
    return config_object


def show_help():
    webbrowser.open("file://" + os.path.realpath("README.html"))
    print("Opening the browser to show the help files!")


def generate_list_of_available_commands(
    config_object: CaseInsensitiveDict[str, dict[str, Any]]
) -> list[str]:
    """Checks to config for operations that would make sense and generates a list of possible commands accordingly.

    Args:
        config_object: A configurations object.

    Returns:
        The generates list fo possible commands.
    """
    options = ["save", "s", "close", "c", "add", "a"]
    if config_object:
        options += ["repair", "r", "delete", "d"]
    options += ["show"]
    if config_object and len(config_object.keys()) > 1:
        options.append("change")
    if config_object:
        options += ["edit", "e"]
    options += ["help", "h"]
    return options


def repair_config(
    config_object: CaseInsensitiveDict[str, dict[str, Any]]
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Repair the configuration file.

    Args:
        config_object: A configurations object.

    Returns:
        The generates list fo possible commands.
    """
    printer_list = get_printer_list()
    error_found = False

    for key, section in config_object.items():
        if "printer" not in section:
            continue
        if section["printer"] not in printer_list:
            error_found = True
            print(
                "The printer in the following sections was not found. Please clarify the printer!\n"
            )
            print_element(key, section, None)
            print()
            printer = input_choice(
                "Please select a new valid printer.",
                printer_list,
                get_default_printer(),
            )
            section["printer"] = printer

    if not error_found:
        print("No error found. Configuration file looks good.")
    return config_object


if __name__ == "__main__":
    configure_logger()
    check_ghostscript()

    print("Welcome to the auto_print config generator!")
    print()

    config = load_config()
    print_configuration(config)

    while True:
        action = input_choice(
            "What actions should be taken?:",
            generate_list_of_available_commands(config),
            "close",
        )

        print(f"Action: {action}")
        if action in ["s", "save"]:
            save_config(config)
        elif action in ["add", "a"]:
            config = add_section(config)
        elif action in ["delete", "d"]:
            config = delete_section(config)
        elif action in ["repair", "r"]:
            config = repair_config(config)
        elif action in ["show"]:
            print()
            print_configuration(config)
        elif action in ["change"]:
            config = change_section_position(config)
        elif action in ["edit", "e"]:
            config = edit_section_command(config)

        elif action in ["close", "c"]:
            if load_config() == config:
                break
            if bool_decision(
                "There are unsaved changes. Please confirm with y/n if you want to close anyway[n]:",
                True,
            ):
                break
        elif action in ["help", "h"]:
            show_help()
