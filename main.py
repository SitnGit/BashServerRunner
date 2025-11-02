import argparse
import sys
from parsers import parse_hosts,parse_playbook
from pathlib import Path
from runner import TaskRunner
from formatter import Formatter

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

    try:
        hosts_data = parse_hosts(args.hosts)

        if not hosts_data:
            print("Error: No host groups found in hosts file", file=sys.stderr)
            sys.exit(1)

        playbook_data = parse_playbook(args.playbook)

        runner = TaskRunner(max_workers=args.workers)
        results = runner.run_playbook(playbook_data, hosts_data)

        formatter = Formatter()
        formatter.print_results(results)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
      main()