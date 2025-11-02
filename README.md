# SERVER BASH RUNNER program

This is a Python command-line tool for executing bash commands on multiple servers in parralel designed with speed, reliability and simplicity in mind.

## Overview

Executes bash commands across multiple servers simultaneously using YAML playbooks and INI-style host groups. Built with Python's ThreadPoolExecutor for efficient parallel execution and Paramiko for SSH connections.

## Features

- Runs tasks on multiple servers in parralel to achieve maximum speed
- SSH connection is key-based meaning connection to the server can only be achieved if the
public keys of the client user is in the authorized_keys file in the server
- Graceful erro-handling meaning that executions continues if individual servers fail

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run a playbook
python -m main playbook.yml --hosts hosts

# Example with options
python -m main playbook.yml --workers 20 --no-color

```

## Architecture

Built with clean separation of concerns:
- Parsers - Parse hosts and playbook files with validation
- Executor - Handle SSH connections and command execution
- Runner - Orchestrate parallel task execution across servers
- Formatter - Display results in readable format

## Requirements

- Python 3.7+
- SSH access to target servers
- SSH keys configured for passwordless authentication
- PyYAML>=6.0
- paramiko>=3.0.0