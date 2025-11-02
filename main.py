import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description='Run playbooks on multiple servers'
    )

    parser.add_argument(
        'playbook',
        type=str,
        help='Path to the playbook YAML file'
    )

    parser.add_argument(
        '--hosts',
        type=str,
        default='/etc/playbook/hosts',
        help='Path to the hosts file (default: /etc/playbook/hosts)'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=10,
        help='Maximum number of parallel SSH connections (default: 10)'
    )

    args = parser.parse_args()

    if not Path(args.playbook).exists():
        print(f"Error: Playbook file not found: {args.playbook}", file=sys.stderr)
        sys.exit(1)
