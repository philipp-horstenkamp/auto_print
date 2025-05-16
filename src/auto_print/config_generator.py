"""
Configuration generator for the module.
"""

import argparse
import os.path
import webbrowser
from typing import Any

from case_insensitive_dict import CaseInsensitiveDict

from auto_print.utils import (
    PRINTER_CONFIG_PATH,
    check_ghostscript,
    configure_logger,
    get_default_printer,
    get_printer_list,
    load_config_file,
    save_config_file,
)


def get_parser():
    """
    Create an argument parser for the auto_print_config_generator module.
    This function is used for documentation purposes only.

    Returns:
        argparse.ArgumentParser: The argument parser
    """
    parser = argparse.ArgumentParser(
        description="Interactive configuration generator for auto-print. "
        "This tool helps you create and manage printer configurations."
    )
    return parser


def input_choice(description: str, input_list: list[str], default: str):
    """Checks an input against a list of possible inputs and norms the input.

    Args:
        description: The description that should be made with the input.
        input_list: A list of possible inputs.
        default: The default value for the input.

    Returns:
        The choice made.
    """
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
        print(f"Options: {', '.join(possible_inputs)}")
        text_in = input(f"Choose [{default}]:").strip()
        if not text_in:
            text_in = default
        text_in = next((e for e in input_list if e.lower() == text_in.lower()), "")
        if text_in:
            return text_in


def bool_decision(description: str, default: bool) -> bool:
    """Tooling to interpret a yes/no decision.

    Args:
        description: The description for the decision.
        default: The default value.

    Returns:
        True or false depending on user input.
    """
    return (
        input_choice(description, ["yes", "y", "no", "n"], "yes" if default else "no")[
            0
        ]
        == "y"
    )


def print_element(name: str, config_element: dict[str, Any], index: int | None) -> None:
    """Print a printer configuration.

    Args:
        name: The name of the printer configuration section.
        config_element: The complete section of the printer configuration.
        index: The index of the section. Can be None if a section should not be printed with index.
    """
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
    """Print the complete configuration.

    Args:
        config_object: A auto-print configuration object.
    """
    print("The current config works as follows:\n")
    if config_object is None:
        print("No config found!\n")
        return

    for count, (name, config_element) in enumerate(config_object.items()):
        print_element(name, config_element, count)
        print()


def load_config() -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Loads the configuration."""
    config_data = load_config_file()
    return CaseInsensitiveDict[str, dict](data=config_data)


def save_config(config_object: CaseInsensitiveDict[str, dict[str, Any]]) -> None:
    """Saves the configuration."""
    save_config_file(config_object.__dict__)


def configure_prefix(config_element: dict[str, Any]) -> None:
    """Configure the prefix filter for a section.

    Args:
        config_element: The section configuration to update.
    """
    print(
        "Filter by the start of a file.\n"
        'Something like "test_str" to filter all files who start with with "test_str"\n'
        "Can be empty if no filter of this type should be used!"
    )

    config_element["prefix"] = input("Type prefix:").strip()
    if config_element["prefix"] == "":
        del config_element["prefix"]


def configure_suffix(config_element: dict[str, Any]) -> None:
    """Configure the suffix filter for a section.

    Args:
        config_element: The section configuration to update.
    """
    print(
        "Filter by the end of a file.\n"
        'Something like "t_file.pdf" to filter all pdfs files who end with "t_file"\n'
        "Can be empty if no filter of this type should be used!"
    )
    print("If nothing is typed in no suffix will be defined.")
    config_element["suffix"] = input("Type suffix:").strip()
    if config_element["suffix"] == "":
        del config_element["suffix"]


def configure_print_settings(config_element: dict[str, Any]) -> None:
    """Configure the print settings for a section.

    Args:
        config_element: The section configuration to update.
    """
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
        config_element["printer"] = get_default_printer()


def configure_display_settings(config_element: dict[str, Any]) -> None:
    """Configure the display settings for a section.

    Args:
        config_element: The section configuration to update.
    """
    config_element["show"] = bool_decision(
        "Should the file be shown by the system default?",
        config_element.get("show", False),
    )


def configure_activation(config_element: dict[str, Any]) -> None:
    """Configure whether the section is active.

    Args:
        config_element: The section configuration to update.
    """
    config_element["active"] = bool_decision(
        "Should the new section be activated?",
        config_element.get("active", True),
    )


def edit_section(
    name: str, config_element: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    """Reconfiguration for a printer configuration.

    Args:
        name: The name of the section that should be reconfigured.
        config_element: The complete auto-print configuration.

    Returns:
        The new section of the auto-print configuration.
    """
    while True:
        # Configure each part of the section
        configure_prefix(config_element)
        configure_suffix(config_element)
        configure_print_settings(config_element)
        configure_display_settings(config_element)
        configure_activation(config_element)

        # Show the configuration
        print()
        print_element(name, config_element, None)

        # Check if the configuration is correct
        if bool_decision("Is the above section correct?", True):
            return name, config_element
        print("Please make changes as needed.")


def create_section(
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """Create a new printer configuration.

    Args:
        config_object: The complete auto-printer configuration.

    Returns:
        The new auto-printer configuration.
    """
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


def display_insert_positions(config_object: CaseInsensitiveDict[str, dict[str, Any]]) -> int:
    """Display all possible insert positions for a new section.

    Args:
        config_object: The current configuration object.

    Returns:
        The end position (number of sections).
    """
    for insert_pos, (name, section) in enumerate(config_object.items()):
        print(f"Insert Position {insert_pos} ->")
        print_element(name, section, None)
    end_pos = len(config_object.keys())
    print(f"Insert Position {end_pos} ->")
    print()
    return end_pos


def get_insert_position(end_pos: int) -> str:
    """Get the position where to insert the new section.

    Args:
        end_pos: The end position (number of sections).

    Returns:
        The position as a string, or "cancel" to cancel the operation.
    """
    insert_str: str = input_choice(
        "Please choose where to add the section or choose cancel to cancel this action:",
        ["start"] + [str(n) for n in range(end_pos + 1)] + ["end", "cancel", "c"],
        "end",
    )
    if insert_str == "end":
        return str(end_pos)
    elif insert_str == "start":
        return "0"
    return insert_str


def insert_section(
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
    name_to_add: str,
    section_to_add: dict[str, Any],
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Insert a section at a specified place into the order of printers.

    Args:
        config_object: The printer configuration that should be added to the full configuration.
        name_to_add: The name under wich the section should be added.
        section_to_add: The section to add.

    Returns:
        The new completed section.
    """
    end_pos = display_insert_positions(config_object)
    insert_str = get_insert_position(end_pos)

    if insert_str in ["cancel", "c"]:
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
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Add a new configuration to a printer.

    Args:
        config_object: The printer configuration where a section should be added.

    Returns:
        The new configuration.
    """
    print("Add a new printer configuration:")
    new_name, new_section = create_section(config_object)
    return insert_section(config_object, new_name, new_section)


def delete_section(
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Deletes a specified section.

    Args:
        config_object: A configuration object.

    Returns:
        The newly generated/edited config_object.
    """
    if not config_object:
        print("There are no section to delete.")
        return config_object
    print_configuration(config_object)
    delete_object = input_choice(
        "Chose what section to delete or to cancel the operation!",
        [*list(config_object.keys()), "cancel", "c"],
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
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Changes the filter order.

    Args:
        config_object: A configuration object.

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
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Edits a section in the configuration.

    Args:
        config_object: A configuration object.

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
    """Displays the help file in the browser."""
    webbrowser.open("file://" + os.path.realpath("README.html"))
    print("Opening the browser to show the help files!")


def generate_list_of_available_commands(
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> list[str]:
    """Checks to config for operations that would make sense and generates a list of possible commands accordingly.

    Args:
        config_object: A configuration object.

    Returns:
        The generated list of possible commands.
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
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Repair the configuration file.

    Args:
        config_object: A configuration object.

    Returns:
        The generated list of possible commands.
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


def handle_action(action: str, config: CaseInsensitiveDict[str, dict[str, Any]]) -> tuple[CaseInsensitiveDict[str, dict[str, Any]], bool]:
    """Handle a user action.

    Args:
        action: The action to handle.
        config: The current configuration.

    Returns:
        A tuple containing the updated configuration and a boolean indicating whether to exit the program.
    """
    print(f"Action: {action}")
    exit_program = False

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
            exit_program = True
        elif bool_decision(
            "There are unsaved changes. Please confirm with y/n if you want to close anyway[n]:",
            True,
        ):
            exit_program = True
    elif action in ["help", "h"]:
        show_help()

    return config, exit_program


def main() -> None:
    """Main function for the configuration generator."""
    configure_logger()
    check_ghostscript()

    print("Welcome to the auto_print config generator!")
    print()

    config = load_config()
    print_configuration(config)

    while True:
        action = input_choice(
            "What workflows should be taken?:",
            generate_list_of_available_commands(config),
            "close",
        )

        config, exit_program = handle_action(action, config)
        if exit_program:
            break


if __name__ == "__main__":
    main()
