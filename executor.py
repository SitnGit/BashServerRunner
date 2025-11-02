import os
import paramiko
from typing import Dict, Optional
from pathlib import Path
import time

class SSHExecutor:
    """Execute bash commands on remote servers via SSH."""

    def __init__(self, hostname: str, username: Optional[str] = None,
                 timeout: int = 30):
        self.hostname = hostname
        self.username = username or os.getenv('USER')
        self.timeout = timeout
        self.client = None

    def connect(self, max_retries: int = 3) -> None:
        """Establish SSH connection with retry logic."""
        for attempt in range(max_retries):
            try:
                self.client = paramiko.SSHClient()
                self.client.load_system_host_keys()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                self.client.connect(
                    hostname=self.hostname,
                    username=self.username,
                    timeout=self.timeout,
                    look_for_keys=True,
                    allow_agent=True
                )
                return  # Success!

            except Exception as e:
                if attempt == max_retries - 1:
                    raise ConnectionError(
                        f"Failed to connect to {self.hostname} after {max_retries} attempts: {e}"
                    )
                time.sleep(1)  # Wait before retry

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
