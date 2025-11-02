from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from executor import SSHExecutor

class TaskRunner:
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers

    def run_playbook(self, playbook_data: List[Dict], hosts_data: Dict[str, List[str]]) -> List[Dict]:
        all_results = []

        for play in playbook_data:
            host_group = play['hosts']

            # Get hosts for this group
            if host_group not in hosts_data:
                raise ValueError(
                    f"Host group '{host_group}' not found in hosts file. "
                )

            hosts = hosts_data[host_group]
            if not hosts:
                print(f"Warning: No hosts in group '{host_group}', skipping play")
                continue

            tasks = play['tasks']

            # Run tasks on all hosts
            results = self.run_tasks_on_hosts(hosts, tasks)
            all_results.extend(results)

        return all_results
    
    def run_tasks_on_hosts(self, hosts: List[str], tasks: List[Dict]) -> List[Dict]:
        """
        Run multiple tasks on multiple hosts in parallel.
        """
        results = []

        # Execute tasks sequentially, but run on all hosts in parallel
        for task in tasks:
            task_results = self._run_task_parallel(hosts, task)
            results.extend(task_results)

        return results
    
    def _run_task_parallel(self, hosts: List[str], task: Dict) -> List[Dict]:
        """
        Run a single task on multiple hosts in parallel.
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_host = {
                executor.submit(self.run_task_on_host, host, task): host
                for host in hosts
            }

            # Collect results as they complete
            for future in as_completed(future_to_host):
                host = future_to_host[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # This shouldn't happen as exceptions are caught in run_task_on_host,
                    # but let's handle it just in case
                    results.append({
                        'hostname': host,
                        'task_name': task['name'],
                        'command': task['bash'],
                        'success': False,
                        'stdout': '',
                        'stderr': f"Unexpected error: {e}",
                        'exit_code': -1,
                        'error': str(e)
                    })

        return results
    
    def run_task_on_host(self, hostname: str, task: Dict) -> Dict:
        """
        Run a single task on a single host.
        """
        result = {
            'hostname': hostname,
            'task_name': task['name'],
            'command': task['bash'],
            'success': False,
            'stdout': '',
            'stderr': '',
            'exit_code': -1,
            'error': None
        }

        try:
            with SSHExecutor(hostname) as executor:
                exec_result = executor.execute(task['bash'])
                result.update({
                    'success': exec_result['success'],
                    'stdout': exec_result['stdout'],
                    'stderr': exec_result['stderr'],
                    'exit_code': exec_result['exit_code']
                })
        except Exception as e:
            result['error'] = str(e)
            result['stderr'] = f"Connection/execution error: {e}"

        return result