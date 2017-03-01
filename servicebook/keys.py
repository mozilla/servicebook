import sys
import argparse

from servicebook import mappings
from servicebook.db import init, Session


_SQLURI = 'sqlite:////tmp/qa_projects.db'


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='ServiceBook API Keys Manager')

    parser.add_argument('--sqluri', help='Database',
                        type=str, default=_SQLURI)

    subparsers = parser.add_subparsers(help='Available actions', dest='action')
    subparsers.add_parser('list', help='list keys')
    parser_add = subparsers.add_parser('add', help='add a key')
    parser_add.add_argument('app', type=str, help='Application name')
    parser_add.add_argument('--scope', type=str, help='Application Scope',
                            default='read')
    parser_revoke = subparsers.add_parser('revoke', help='Revoke a key')
    parser_revoke.add_argument('app', type=str, help='Application name')

    args = parser.parse_args(args=args)

    init(sqluri=args.sqluri)
    session = Session()

    if args.action == 'list':
        keys = session.query(mappings.AuthenticationKey).all()
        if len(keys) == 0:
            print('No keys!')
        for key in keys:
            print(key)
    elif args.action == 'add':
        q = session.query(mappings.AuthenticationKey)
        q = q.filter(mappings.AuthenticationKey.application == args.app)
        key = q.first()
        if key is not None:
            print("Key already exists for %s" % args.app)
            print("Revoke it if you want a new one")
            print(key)
        else:
            new_key = mappings.AuthenticationKey(args.app, scope=args.scope)
            session.add(new_key)
            session.commit()
            print(new_key)
    elif args.action == 'revoke':
        q = session.query(mappings.AuthenticationKey)
        q = q.filter(mappings.AuthenticationKey.application == args.app)
        key = q.first()
        if key is not None:
            session.delete(key)
            session.commit()
            print("Key revoked for %s" % args.app)
        else:
            print("No key found for  %s" % args.app)


if __name__ == '__main__':
    main()
