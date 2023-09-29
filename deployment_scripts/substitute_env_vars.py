import sys
import os
import re


def substitute(template_str: str) -> str:
    matches = re.findall("<([A-Z_]+)>", template_str)
    print(matches)
    for name in matches:
        value = os.environ.get(name)
        if value is not None:
            template_str = template_str.replace(f"<{name}>", value)
    return template_str


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 2:
        print(f"Usage: ${argv[0]} filename")
        exit(1)

    with open(argv[1]) as f:
        s = substitute(f.read())
    print(s)
