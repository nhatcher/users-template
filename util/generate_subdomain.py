import random

"""
Generates a random subdomain
"""

with open("/usr/share/dict/words") as f:
    words = f.read().splitlines()


def rand_name():
    return (
        "-".join([words[random.randint(0, len(words) - 1)] for i in range(2)])
        .lower()
        .replace("'", "")
    )


if __name__ == "__main__":
    print(rand_name())
