#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import unicode_literals
import sys
import logging
import argparse
import warnings

from bellyfeel.version import version
from bellyfeel.sql import User, generate_password


logger = logging.getLogger('bellyfeel')


def bellyfeel_create_admin_user(argv):  # pragma: no cover
    """executes an instance of the beacon keep-alive server.

    :param ``--email``: ip address of the interface where it should listen to connections
    """

    parser = argparse.ArgumentParser(
        prog='bellyfeel-create-admin-user',
    )

    parser.add_argument(
        'email',
        help='the email of the admin.',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help='Use this flag if you want to check if the given arguments are correct',
    )

    args = parser.parse_args(argv)

    existing = User.get_by_email(args.email)

    if args.dry_run:
        if existing:
            print "would set user", existing.email, 'to admin'
        else:
            print "would create user", existing.email, 'as admin'

        raise SystemExit(0)

    if existing:
        existing.set_admin(True)
        new_password = existing.reset_password()
        print "\033[1;33msucessfully granted admin clearance to user:\033[1;34m", existing.email, '\033[0m'
    else:
        new_password = generate_password(17)
        created = User.create_with_password(args.email, new_password).activate_now(is_admin=True)
        print "\033[1;32msuccessfully created user\033[0m", created.email, "\033[1;32mwith \033[1;37madmin\033[1;32m clearance\033[0m"

    print "take note of the new password below:"
    print new_password


def bellyfeel_version(argv):
    print "Bellyfeel Backend v{}".format(version)


def main():
    HANDLERS = {
        'version': bellyfeel_version,
        'create-admin': bellyfeel_create_admin_user,
        'admin': bellyfeel_create_admin_user,
    }

    parser = argparse.ArgumentParser(prog='bellyfeel')

    parser.add_argument(
        'command', help='Available commands:\n\n{0}\n'.format("|".join(HANDLERS.keys())))

    argv = sys.argv[1:2]
    args = parser.parse_args(argv)

    if args.command not in HANDLERS:
        parser.print_help()
        raise SystemExit(1)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            HANDLERS[args.command](sys.argv[2:])
        except Exception:
            logging.exception("Failed to execute %s", args.command)
            raise SystemExit(1)


if __name__ == '__main__':
    main()
