import os
import paramiko
from typing import Dict, Optional
from pathlib import Path

class SSHExecutor:
    """Execute bash commands on remote servers via SSH."""

    def __init__(self, hostname: str, username: Optional[str] = None,
                 timeout: int = 30):
        self.hostname = hostname
        self.username = username or os.getenv('USER')
        self.timeout = timeout
        self.client = None

    def connect(self) -> None:
        """
        Establish SSH connection using key-based authentication.
        """
        self.client = paramiko.SSHClient()

        # Load system host keys and auto-add unknown hosts
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # auto adds host to known host, COULD BE AN ATTACKER

        # Look for SSH keys in standard locations
        ssh_dir = Path.home() / '.ssh'
        key_files = ['id_rsa', 'id_ed25519', 'id_ecdsa', 'id_dsa']

        # Try connecting with available keys
        try:
            self.client.connect(
                hostname=self.hostname,
                username=self.username,
                timeout=self.timeout,
                look_for_keys=True,
                allow_agent=True
            )
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to {self.hostname}: {e}"
            )

    def execute(self, command: str) -> Dict[str, any]:
        """
        Execute a bash command on the server.
        """
        if not self.client:
            raise RuntimeError("Not connected to server. Call connect() first.")

        try:
            stdin, stdout, stderr = self.client.exec_command(command)

            # Wait for command to complete and get results
            exit_code = stdout.channel.recv_exit_status()
            stdout_data = stdout.read().decode('utf-8', errors='replace')
            stderr_data = stderr.read().decode('utf-8', errors='replace')

            return {
                'success': exit_code == 0,
                'stdout': stdout_data,
                'stderr': stderr_data,
                'exit_code': exit_code
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': f"Execution error: {e}",
                'exit_code': -1
            }

    def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None

# Magix methods -> called when class is used in with statement
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
