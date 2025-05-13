# Auto Print

<!--TOC-->



- [Auto Print](#auto-print)

  - [Integrate in browser workflow](#integrate-in-browser-workflow)

  - [Main commands](#main-commands)

  - [Configuration example](#configuration-example)

  - [Software dependencies](#software-dependencies)

  - [How it works](#how-it-works)

  - [About](#about)



<!--TOC-->










## Integrate in browser workflow
One of the use cases is to use this software as a default PDF executable from Firefox or Chrome:
Here some images on how to configure that:

1. Open the Settings Tab in your Browser as shown by the firefox browser:
![go to settings](docs/Settings.PNG)
2. Choose the auto-printer.exe as your default executable for pdf and all pdf like formats.
![Choose auto-printer.exe as your default software](docs/ChoosePrinter.PNG)

## Main commands

| Command | Short | Result                                                    |
|:-------:|-------|:----------------------------------------------------------|
|  save   | s     | Save the configuration.                                   |
|  close  | c     | Closes the configuration generator.                       |
|   add   | a     | Add a new section to the configuration.                   | 
| delete  | d     | Delete a section from the configuration.                  |
|  show   | s     | Show the configuration in text form.                      |
| change  |       | Changes the section order.                                |
|  edit   | e     | Edits a section.                                          |
|  help   | h     | Show the help information.                                |
| repair  | r     | Repair the config file by checking if all printers exist. |

 

## Configuration example

The below file is an example with comments.
The file `TEST_something.pdf` would be printed with the first printer.
The file `Something_to_print.pdf` would be used by the second printer.
The file `ABC.docx` would be shown with MS Word (if installed).
```json
{
  "Marke": {
    "active": true,                 // Section active. Should be used.
    "printer": "MyPreciousPrinter",
    "prefix": "TEST_",              // How the file should start.
    "suffix": ".pdf",               // How the file should end.
    "print": true,                  // Prints the file.
    "show": false                   // Does not show the file.
  },
  "SomeOtherCategory": {
    "active": false,                // Section not active. Can't be used.
    "printer": "AnotherPrinter",
    "prefix": "Something",
    "suffix": ".pdf",
    "show": true,                   // Printing via default windows application
    "print": true
  },
  "UseDefaultPrinter": {
    "active": true,
                                    //no printer is given therefore the default printer is used."
    "prefix": "DefPrintFile",
    "suffix": ".pdf",
    "show": false,
    "print": true
  },
  "All": {                          // Default action (No requirements)
    "active": true,               
    "show": true,                   // Show without printing (Windows Default action)
    "print": false
  }
}
```


## Software dependencies
Um die Software gut nutzen zu können werden folgende Programme benötigt:

- [Ghostscript](https://www.ghostscript.com/releases/gsdnld.html)
- [Adobe PDF Reader](https://www.adobe.com/de/acrobat/pdf-reader.html)

## How it works 

The goal of this project is to simplify the tedious task or printing similar forms.

1. The program is started with a filepath as an argument.
2. The filename gets extracted.
3. The filename is compared to a list of suffixes and prefixes.
4. If suffix and prefix are a match the file gets executed.
If a suffix or a prefix is not given the comparison is true either way.
5. The file is then eiter Printed and/or shown depending on the configuration.

Everything is logged and can be locked up in the auto_print.log file!

## About

This project was written by Philipp Horstenkamp in the hope 
that it will make some office processes a bit more smooth.
