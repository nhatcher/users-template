import sys
import configparser

"""
This script performs template substitution by replacing placeholders in an input
template file with values from a provided configuration file.

Usage:
    python3 montyplate.py template_file

Arguments:
    - template_file (str): The path to the template file containing placeholders
      to be replaced.

The script reads a configuration file (INI format) and replaces placeholders in
the template file with corresponding values from the configuration file.

Placeholders should be in the format <SECTION_NAME.KEY_NAME>, and values are
retrieved from the specified sections and keys in the configuration file.

Example:
    python3 montyplate.py script.template.sh > script.sh
"""


# Function to perform substitution
def substitute_placeholders(template, config):
    for section in config.sections():
        for key, value in config.items(section):
            placeholder = f"<{section}.{key}>"
            template = template.replace(placeholder, value.strip('"'))
    return template


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 2:
        print(f"Usage: ${argv[0]} template_file")
        exit(1)
    # Load the configuration file
    # interpolation=None means % is just a percentage sign
    config = configparser.ConfigParser(interpolation=None)
    config.read("/etc/server_config.ini")

    with open(argv[1]) as f:
        s = substitute_placeholders(f.read(), config)
    print(s)
