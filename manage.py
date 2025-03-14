#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import django


def main():
    """Run administrative tasks."""
    #we will ALWAYS want to set up the above
    if os.environ.get('DAPHNE', default=False) == 'TRUE':
        os.environ.setdefault('DAPHNE','TRUE') #Adding this so i dont have to do it everytime
        sys.argv = ['daphne', 'config.asgi:application']
        from daphne.cli import CommandLineInterface
        django.setup()
        CommandLineInterface.entrypoint()
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
