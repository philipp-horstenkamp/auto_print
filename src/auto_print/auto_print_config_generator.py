"""Configuration generator for the auto-print module."""

import argparse
import json
import webbrowser
from typing import Any

import questionary
import typer
from case_insensitive_dict import CaseInsensitiveDict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from auto_print.auto_print_execute import (
    PRINTER_CONFIG_PATH,
    check_ghostscript,
    configure_logger,
    get_default_printer,
    get_printer_list,
)

console = Console()
HELP_URL = "https://philipp-horstenkamp.github.io/auto_print/"


class InputValidationError(ValueError):
    """Error raised when input validation fails."""

    EMPTY_INPUT_LIST = "Empty input list"
    MISSING_DESCRIPTION = "Missing description"
    DEFAULT_NOT_IN_CHOICES = "Default not in choices"
    INVALID_INPUT_LIST = "The list of possible inputs need to be defined and have a minimum length of one."


def get_parser() -> argparse.ArgumentParser:
    """Create an argument parser for documentation purposes."""
    return argparse.ArgumentParser(
        description="Interactive configuration generator for auto-print."
    )


def input_choice(description: str, input_list: list[str], default: str) -> str:
    """Gets a choice selection using questionary."""
    if not input_list:
        raise InputValidationError(InputValidationError.INVALID_INPUT_LIST)
    if not description:
        raise InputValidationError(InputValidationError.MISSING_DESCRIPTION)
    if default not in input_list:
        raise InputValidationError(InputValidationError.DEFAULT_NOT_IN_CHOICES)

    choice = questionary.select(
        description,
        choices=input_list,
        default=default,
    ).ask()

    return choice if choice is not None else default


def bool_decision(description: str, *, default: bool = False) -> bool:
    """Get a yes/no decision from the user."""
    result = questionary.confirm(description, default=default).ask()
    return default if result is None else bool(result)


def print_configuration(
    config_object: CaseInsensitiveDict[str, dict],
    highlight_name: str | None = None,
) -> None:
    """Print the complete configuration in a clean, human-readable table.

    Args:
        config_object: An auto-print configuration object.
        highlight_name: Optional section name to visually highlight in the table.
    """
    console.print("[dim]The current config works as follows:[/dim]\n")
    if not config_object:
        console.print(
            Panel(
                "[yellow]No printing rules configured yet.[/yellow]\n"
                "Select [bold green]'Add new printer rule'[/bold green] below to create your first rule.",
                title="[bold blue]Configuration Overview[/bold blue]",
            )
        )
        return

    table = Table(
        title="Active Printing Rules (Highest Priority First)",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Prio", justify="center", style="dim")
    table.add_column("Rule Name", style="bold white")
    table.add_column("File Match Filter", style="magenta")
    table.add_column("Action", style="green")
    table.add_column("Target Printer", style="yellow")
    table.add_column("Status", justify="center")

    available_printers = set(get_printer_list())

    for count, (name, config_element) in enumerate(config_object.items()):
        printer = config_element.get("printer", get_default_printer())
        printing = config_element.get("print", False)
        showing = config_element.get("show", True)
        active = config_element.get("active", False)
        suffix = config_element.get("suffix")
        prefix = config_element.get("prefix")

        match_parts = []
        if prefix:
            match_parts.append(f'Starts with "{prefix}"')
        if suffix:
            match_parts.append(f'Ends with "{suffix}"')
        match_str = " & ".join(match_parts) if match_parts else "All files (*)"

        action_parts = []
        if printing:
            action_parts.append("Print")
        if showing:
            action_parts.append("View")
        action_str = " + ".join(action_parts) if action_parts else "No action"

        if printing:
            if printer in available_printers:
                printer_str = printer
            else:
                printer_str = f"[bold red]{printer} (Not Found!)[/bold red]"
        else:
            printer_str = "[dim]-[/dim]"

        status_str = (
            "[bold green]Active[/bold green]" if active else "[dim]Inactive[/dim]"
        )

        is_highlighted = (
            highlight_name is not None and name.lower() == highlight_name.lower()
        )
        rule_name_display = (
            f"[bold yellow]★ {name}[/bold yellow]" if is_highlighted else name
        )

        table.add_row(
            str(count + 1),
            rule_name_display,
            match_str,
            action_str,
            printer_str,
            status_str,
            style="bold yellow" if is_highlighted else None,
        )

    console.print(table)
    console.print()


def print_element(
    name: str,
    config_element: dict[str, Any],
    index: int | None = None,  # noqa: ARG001
    *,
    highlight: bool = True,
) -> None:
    """Print a single printer configuration rule using the Rich Table view."""
    single_config = CaseInsensitiveDict[str, dict]({name: config_element})
    print_configuration(single_config, highlight_name=name if highlight else None)


def load_config() -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Loads the configuration."""
    try:
        with PRINTER_CONFIG_PATH.open(encoding="utf-8") as file:
            return CaseInsensitiveDict[str, dict](data=json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return CaseInsensitiveDict[str, dict](data={})


def save_config(config_object: CaseInsensitiveDict[str, dict[str, Any]]) -> None:
    """Saves the configuration."""
    PRINTER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PRINTER_CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(dict(config_object), file, indent=2)
    console.print("[bold green]✔ Configuration saved successfully![/bold green]")


def edit_section(
    name: str, config_element: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    """Reconfiguration for a printer configuration rule."""
    console.print(Panel(f"[bold cyan]Configuring Rule: {name}[/bold cyan]"))

    while True:
        prefix = (
            questionary.text(
                "Filename Prefix Filter (e.g. 'invoice_' to match invoice_123.pdf):",
                instruction="Leave blank to match files with any prefix.",
                default=config_element.get("prefix", ""),
            ).ask()
            or ""
        ).strip()
        if prefix:
            config_element["prefix"] = prefix
        elif "prefix" in config_element:
            del config_element["prefix"]

        suffix = (
            questionary.text(
                "Filename Suffix / Extension Filter (e.g. '.pdf' or '_doc.pdf'):",
                instruction="Leave blank to match files with any suffix.",
                default=config_element.get("suffix", ""),
            ).ask()
            or ""
        ).strip()
        if suffix:
            config_element["suffix"] = suffix
        elif "suffix" in config_element:
            del config_element["suffix"]

        should_print = bool_decision(
            "Automatically print matching files?",
            default=config_element.get("print", True),
        )
        config_element["print"] = should_print

        if should_print:
            printer_list = get_printer_list()
            default_p = (
                get_default_printer()
                if get_default_printer() in printer_list
                else (printer_list[0] if printer_list else "PDF Printer")
            )
            config_element["printer"] = input_choice(
                "Select destination printer:",
                printer_list,
                default_p,
            )
        elif "printer" in config_element:
            del config_element["printer"]

        config_element["show"] = bool_decision(
            "Open document in default viewer (e.g. Adobe Reader) after processing?",
            default=config_element.get("show", False),
        )

        config_element["active"] = bool_decision(
            "Enable this rule immediately?",
            default=config_element.get("active", True),
        )

        console.print("\n[bold]Summary of rule settings:[/bold]")
        print_element(name, config_element, None)

        if bool_decision("Is this rule configuration correct?", default=True):
            return name, config_element
        console.print("[yellow]Re-editing rule configuration...[/yellow]\n")


def create_section(
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """Create a new printer configuration section."""
    config_element: dict[str, Any] = {}
    name = ""
    while not name:
        entered = questionary.text(
            "Enter a descriptive name for this rule (e.g. 'Invoices', 'Shipping Labels'):",
            instruction="Name must be unique and cannot be empty.",
        ).ask()
        name = (entered or "").strip()
        if name in config_object:
            console.print(
                f"[bold red]The name '{name}' is already in use. Choose another name![/bold red]"
            )
            name = ""
        elif name.lower() in {"cancel", "c"}:
            console.print(
                "[bold red]Invalid rule name. Please enter a valid name.[/bold red]"
            )
            name = ""
    return edit_section(name, config_element)


def insert_section(
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
    name_to_add: str,
    section_to_add: dict[str, Any],
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Insert a section at a specified place into the order of printers."""
    if not config_object:
        config_object[name_to_add] = section_to_add
        print_configuration(config_object, highlight_name=name_to_add)
        return config_object

    end_pos = len(config_object.keys())
    choices = (
        ["At start (top priority)"]
        + [
            f'After "{name}" (position {i + 1})'
            for i, name in enumerate(config_object.keys())
        ]
        + ["At end", "Cancel"]
    )

    insert_str: str = input_choice(
        "Please choose where to place the rule in priority order:",
        choices,
        "At end",
    )
    if insert_str == "Cancel":
        print_configuration(config_object)
        return config_object

    if insert_str == "At start (top priority)":
        insert_pos = 0
    elif insert_str == "At end":
        insert_pos = end_pos
    else:
        try:
            insert_pos = int(insert_str.split("(position ")[1].rstrip(")"))
        except (IndexError, ValueError):
            insert_pos = end_pos

    key_list = list(config_object.keys())
    key_list.insert(insert_pos, name_to_add)
    config_object[name_to_add] = section_to_add
    config_object = CaseInsensitiveDict[str, dict[str, Any]](
        {name: config_object[name] for name in key_list}
    )
    print_configuration(config_object, highlight_name=name_to_add)
    return config_object


def add_section(
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Add a new configuration to a printer."""
    console.print("[bold green]Add a new printer rule:[/bold green]")
    new_name, new_section = create_section(config_object)
    return insert_section(config_object, new_name, new_section)


def delete_section(
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Deletes a specified section."""
    if not config_object:
        console.print("[yellow]There are no rules to delete.[/yellow]")
        return config_object
    print_configuration(config_object)
    delete_object = input_choice(
        "Choose which printer rule section to delete:",
        [*list(config_object.keys()), "Cancel"],
        "Cancel",
    )
    if delete_object == "Cancel":
        console.print("[yellow]Cancelled delete operation.[/yellow]")
        return config_object

    console.print(f'[bold red]Deleting section "{delete_object}"...[/bold red]')
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
    """Changes the filter order."""
    section_names = list(config_object.keys())
    if not section_names:
        console.print("[yellow]There are no rules to reorder.[/yellow]")
        return config_object

    name_of_section = input_choice(
        "Choose the rule section to reorder:",
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
    """Edits a section in the configuration."""
    section_names = list(config_object.keys())
    if not section_names:
        console.print("[yellow]There are no rules to edit.[/yellow]")
        return config_object

    choice = input_choice(
        "Choose the rule section to edit:",
        section_names,
        section_names[0],
    )

    console.print(f"[bold cyan]Redefining rule section '{choice}':[/bold cyan]")
    print_element(choice, config_object[choice], None)

    _, config_object[choice] = edit_section(choice, config_object[choice])
    return config_object


def show_help() -> None:
    """Displays the online help documentation in the browser."""
    webbrowser.open(HELP_URL)
    console.print(
        f"[bold green]Opening browser to documentation ({HELP_URL})...[/bold green]"
    )


def generate_list_of_available_commands(
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> list[str]:
    """Generates the list of available commands based on config state."""
    options = ["Add new printer rule"]
    if config_object:
        options.append("Edit printer rule")
        if len(config_object.keys()) > 1:
            options.append("Change rule priority")
        options.append("Delete printer rule")
        options.append("Repair configuration")
    options.append("Save configuration")
    options += ["Open help in browser", "Exit / Close"]
    return options


def repair_config(
    config_object: CaseInsensitiveDict[str, dict[str, Any]],
) -> CaseInsensitiveDict[str, dict[str, Any]]:
    """Repair the configuration file for invalid printers."""
    printer_list = get_printer_list()
    if not printer_list:
        console.print("[bold red]No printers detected on this system.[/bold red]")
        return config_object

    error_found = False

    for key, section in config_object.items():
        if not section.get("print", False) or "printer" not in section:
            continue
        if section["printer"] not in printer_list:
            error_found = True
            console.print(
                f"[bold red]Printer '{section['printer']}' in rule '{key}' was not found on this system.[/bold red]\n"
            )
            print_element(key, section, None)
            console.print()
            default_p = (
                get_default_printer()
                if get_default_printer() in printer_list
                else printer_list[0]
            )
            printer = input_choice(
                "Please select a valid replacement printer:",
                printer_list,
                default_p,
            )
            section["printer"] = printer

    if not error_found:
        console.print(
            "[bold green]No printer errors found. All rules point to valid system printers.[/bold green]"
        )
    return config_object


def handle_action(
    action: str, config: CaseInsensitiveDict[str, dict[str, Any]]
) -> tuple[CaseInsensitiveDict[str, dict[str, Any]], bool]:
    """Execute the selected workflow action using match/case dispatch."""
    match action:
        case "Save configuration":
            save_config(config)
        case "Add new printer rule":
            config = add_section(config)
        case "Delete printer rule":
            config = delete_section(config)
        case "Repair configuration":
            config = repair_config(config)
        case "Change rule priority":
            config = change_section_position(config)
        case "Edit printer rule":
            config = edit_section_command(config)
        case "Exit / Close":
            if load_config() == config:
                console.print(
                    "[bold green]Exiting Configuration Manager. Goodbye![/bold green]"
                )
                return config, True
            save_choice = input_choice(
                "You have unsaved changes. What would you like to do?",
                ["Save & Exit", "Exit without saving", "Cancel"],
                "Save & Exit",
            )
            if save_choice == "Save & Exit":
                save_config(config)
                console.print("[bold green]Changes saved. Goodbye![/bold green]")
                return config, True
            if save_choice == "Exit without saving":
                console.print("[yellow]Exiting without saving changes.[/yellow]")
                return config, True
        case "Open help in browser":
            show_help()

    return config, False


app = typer.Typer(help="Interactive configuration generator for auto-print.")


@app.command()
def main_interactive() -> None:
    """Run the interactive configuration generator."""
    configure_logger()
    check_ghostscript()

    console.print(
        Panel.fit(
            "[bold cyan]Auto Print - Interactive Configuration Manager[/bold cyan]\n"
            "[dim]Route documents automatically to specific printers based on filenames.[/dim]\n"
            f"[dim]Config file: {PRINTER_CONFIG_PATH}[/dim]",
            border_style="cyan",
        )
    )
    console.print()

    config = load_config()

    available_printers = set(get_printer_list())
    broken_rules = [
        name
        for name, section in config.items()
        if section.get("printer") and section["printer"] not in available_printers
    ]
    if broken_rules:
        console.print(
            Panel(
                f"[bold red]Warning: {len(broken_rules)} rule(s) reference printers that are no longer installed![/bold red]\n"
                "Select '[bold yellow]Repair configuration[/bold yellow]' below to update their target printers.",
                border_style="red",
            )
        )
        console.print()

    print_configuration(config)

    default_cmd = "Repair configuration" if broken_rules else "Add new printer rule"

    while True:
        action = input_choice(
            "What workflow would you like to execute?:",
            generate_list_of_available_commands(config),
            default_cmd,
        )
        config, should_exit = handle_action(action, config)
        if should_exit:
            break


def main() -> None:
    """Run the config generator application via Typer."""
    app()


click_app = typer.main.get_command(app)


if __name__ == "__main__":
    main()
