import yaml
from typing import Dict, List
from pathlib import Path

def parse_hosts(hosts_path: str = "/etc/playbook/hosts") -> Dict[str, List[str]]:
    hosts_file = Path(hosts_path)
    if not hosts_file.exists():
        raise FileNotFoundError(f"Hosts file not found: {hosts_path}")

    groups = {}
    current_group = None

    with open(hosts_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Check if theres a group header
            if line.startswith('[') and line.endswith(']'):
                current_group = line[1:-1]
                groups[current_group] = []
            elif current_group: # else if its a host add it to the current group
                groups[current_group].append(line)
            else: # else throw an error if theres no host group at the start
                raise ValueError(
                    f"Host '{line}' found before any group definition "
                    f"at line {line_num}"
                )

    return groups

def parse_playbook(playbook_path: str) -> List[Dict]:
    playbook_file = Path(playbook_path)
    if not playbook_file.exists():
        raise FileNotFoundError(f"Playbook not found: {playbook_path}")
    
    with open(playbook_file, 'r') as f:
        try:
            data = yaml.safe_load(f) # load with safe_load to skip executing code
                                    # inside the yaml file, if there is any
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in playbook: {e}")
        
    if not isinstance(data, list):
        raise ValueError("Playbook must be a list of plays")
    
    # Validate the playbook structure
    for play_num, play in enumerate(data, 1):
        if not isinstance(play, dict):
            raise ValueError(f"Play {play_num} must be a dictionary")

        if 'hosts' not in play:
            raise ValueError(f"Play {play_num} missing 'hosts' field")

        if 'tasks' not in play:
            raise ValueError(f"Play {play_num} missing 'tasks' field")

        if not isinstance(play['tasks'], list):
            raise ValueError(f"Play {play_num} 'tasks' must be a list")
        
        # Validate each task
        for task_num, task in enumerate(play['tasks'], 1):
            if not isinstance(task, dict):
                raise ValueError(
                    f"Play {play_num}, task {task_num} must be a dictionary"
                )

            if 'name' not in task:
                raise ValueError(
                    f"Play {play_num}, task {task_num} missing 'name' field"
                )

            if 'bash' not in task:
                raise ValueError(
                    f"Play {play_num}, task {task_num} missing 'bash' field"
                )
    return data
