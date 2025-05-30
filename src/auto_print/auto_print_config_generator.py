"""Configuration generator for the auto-print module."""

import argparse
import json
import webbrowser
from pathlib import Path
from typing import Any

from case_insensitive_dict import CaseInsensitiveDict

from auto_print.auto_print_execute import (
    PRINTER_CONFIG_PATH,
    check_ghostscript,
    configure_logger,
    get_default_printer,
    get_printer_list,
)


class InputValidationError(ValueError):
    """Error raised when input validation fails."""

    EMPTY_INPUT_LIST = "Empty input list"
    MISSING_DESCRIPTION = "Missing description"
    DEFAULT_NOT_IN_CHOICES = "Default not in choices"
    INVALID_INPUT_LIST = "The list of possible inputs need to be defined and have a minimum length of one."


def get_parser():
    """Create an argument parser for the auto_print_config_generator module.

    This function is used for documentation purposes only.

    Returns:
        argparse.ArgumentParser: The argument parser
    """
    return argparse.ArgumentParser(
        description="Interactive configuration generator for auto-print. "
        "This tool helps you create and manage printer configurations."
    )


def input_choice(description: str, input_list: list[str], default: str) -> str:
    """Checks an input against a list of possible inputs and normalizes the input.

    Args:
        description: The description that should be made with the input.
        input_list: A list of possible inputs.
        default: The default value for the input.

    Returns:
        The choice made.

    Raises:
        InputValidationError: If validation fails for inputs.
    """
    # Validate inputs
    if not input_list:
        raise InputValidationError(InputValidationError.INVALID_INPUT_LIST)
    if not description:
        raise InputValidationError(InputValidationError.MISSING_DESCRIPTION)
    if default not in input_list:
        raise InputValidationError(InputValidationError.DEFAULT_NOT_IN_CHOICES)

    # Display options and get user input
    while True:
        print(description)
        print(f"Options: {', '.join(input_list)}")
        text_in = input(f"Choose [{default}]:").strip()

        # Use default if no input provided
        if not text_in:
            return default

        # Find case-insensitive match
        for option in input_list:
            if option.lower() == text_in.lower():
                return option

        # No match found, loop will continue


def bool_decision(description: str, *, default: bool = False) -> bool:
    """Get a yes/no decision from the user.

    Args:
        description: The description for the decision.
        default: The default value (True for yes, False for no).

    Returns:
        True for yes/y responses, False for no/n responses.
    """
    default_option = "yes" if default else "no"
    response = input_choice(description, ["yes", "y", "no", "n"], default_option)
    return response.startswith("y")


def print_element(name: str, config_element: dict[str, Any], index: int | None) -> None:
    """Print a printer configuration.

    Args:
        name: The name of the printer configuration section.
        config_element: The complete section of the printer configuration.
        index: The index of the section. Can be None if a section should not be printed with index.
    """
    # Extract configuration values
    printer = config_element.get("printer", get_default_printer())
    printing = config_element.get("print", False)
    showing = config_element.get("show", True)
    active = config_element.get("active", False)
    suffix = config_element.get("suffix")
    prefix = config_element.get("prefix")

    # Print section header
    if index is None:
        header = f'    Config section with name "{name}" '
    else:
        header = f'{index + 1:>2}. Prio config section with name "{name}" '

    header += f'prints on "{printer}"' if printing else "does not print."
    print(header)

    # Print file matching criteria
    if suffix or prefix:
        filter_msg = "    Action is taken on all files "
        filter_parts = []

        if prefix:
            filter_parts.append(f'starting with "{prefix}"')
        if suffix:
            filter_parts.append(f'ending with "{suffix}"')

        filter_msg += " and ".join(filter_parts)
        print(filter_msg)
    else:
        print("    This is executed for every file.")

    # Print action and status
    show_status = "not " if not showing else ""
    print_status = "not be " if not printing else ""
    active_status = "active" if active else "inactive"

    print(f"    The file should {show_status}be shown and {print_status}printed.")
    print(f"    The section is {active_status}.")


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
    """Loads the configuration.

    Returns:
        A CaseInsensitiveDict containing the configuration data.
        Returns an empty dictionary if the file is not found, empty, or contains invalid JSON.
    """
    try:
        with PRINTER_CONFIG_PATH.open(encoding="utf-8") as file:
            return CaseInsensitiveDict[str, dict](data=json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return CaseInsensitiveDict[str, dict](data={})


def save_config(config_object: CaseInsensitiveDict[str, dict[str, Any]]) -> None:
    """Saves the configuration."""
    with PRINTER_CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(dict(config_object), file, indent=2)
    print("Config saved!")


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
        # Configure prefix filter
        print(
            "Filter by the start of a file.\n"
            'Something like "test_str" to filter all files who start with "test_str"\n'
            "Can be empty if no filter of this type should be used!"
        )
        prefix = input("Type prefix:").strip()
        if prefix:
            config_element["prefix"] = prefix
        elif "prefix" in config_element:
            del config_element["prefix"]

        # Configure suffix filter
        print(
            "Filter by the end of a file.\n"
            'Something like "t_file.pdf" to filter all pdfs files who end with "t_file"\n'
            "Can be empty if no filter of this type should be used!"
        )
        suffix = input("Type suffix:").strip()
        if suffix:
            config_element["suffix"] = suffix
        elif "suffix" in config_element:
            del config_element["suffix"]

        # Configure printing options
        should_print = bool_decision(
            "Should the filtered file be printed automatically?",
            default=config_element.get("print", True),
        )
        config_element["print"] = should_print

        # Configure printer selection if printing is enabled
        if should_print:
            config_element["printer"] = input_choice(
                "Please choose a printer to use:",
                get_printer_list(),
                get_default_printer(),
            )
        else:
            config_element["printer"] = get_default_printer()

        # Configure display options
        config_element["show"] = bool_decision(
            "Should the file be shown by the system default?",
            default=config_element.get("show", False),
        )

        # Configure section activation
        config_element["active"] = bool_decision(
            "Should the new section be activated?",
            default=config_element.get("active", True),
        )

        # Show the configuration summary
        print()
        print_element(name, config_element, None)

        # Confirm or edit again
        if bool_decision("Is the above section correct?", default=True):
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
    webbrowser.open("file://" + str(Path("README.html").resolve()))
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


def main() -> None:
    """Run the auto-print configuration generator.

    This function initializes the logger, checks for ghostscript,
    and starts the interactive configuration process.
    """
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
                default=True,
            ):
                break
        elif action in ["help", "h"]:
            show_help()


if __name__ == "__main__":
    main()
