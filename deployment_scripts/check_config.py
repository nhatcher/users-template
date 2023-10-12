import configparser
import sys

# This is just a smoke test that the config file is in place and all parameters
# look good. Note that we could test further things like the github account exists or
# that the passwords are strong enough.
# This is probably not the place


def check_config(config):
    """Checks that the config file parameters are in place"""
    # check django section
    django_section = config["django"]
    assert len(django_section["secret_key"]) > 20
    assert django_section["host"] != ""
    assert django_section["static_root"] != ""

    # This is optional
    # caddy_section = config['caddy']
    # assert caddy_section['host'] != ""

    email_section = config["email"]
    assert len(email_section["host_password"]) > 3
    assert email_section["host"] != ""
    assert email_section["host_user"] != ""

    database_section = config["database"]
    assert len(database_section["password"]) > 8
    assert database_section["name"] != ""
    assert database_section["user"] != ""

    sentry_section = config["sentry"]
    assert sentry_section["dsn"] != ""

    github_section = config["github"]
    assert github_section["url"] != ""
    assert github_section["name"] != ""


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 1:
        print(f"Usage: ${argv[0]}")
        exit(1)
    # Load the configuration file
    # interpolation=None means % is just a percentage sign
    config = configparser.ConfigParser(interpolation=None)
    config.read("/etc/server_config.ini")
    check_config(config)
