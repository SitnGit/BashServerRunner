from typing import List, Dict


class Formatter:

    def format_result(self, result: Dict) -> str:
        """ Format a single task result. """
        lines = []

        status = "SUCCESS" if result['success'] else "FAILED"
        lines.append(f"[{status}] {result['hostname']} - {result['task_name']}")

        lines.append(f"Command: {result['command']}")

        if result['stdout']:
            lines.append(f"Output: {result['stdout'].strip()}")

        if result['stderr']:
            lines.append(f"Error: {result['stderr'].strip()}")

        lines.append(f"Exit Code: {result['exit_code']}")

        lines.append("")  # Blank line between results

        return '\n'.join(lines)

    def format_results(self, results: List[Dict]) -> str:
        """ Format all results. """
        if not results:
            return "No results."

        output = []

        output.append("=" * 60)
        output.append("EXECUTION RESULTS")
        output.append("=" * 60)
        output.append("")

        for result in results:
            output.append(self.format_result(result))

        total = len(results)
        successful = sum(1 for r in results if r['success'])
        failed = total - successful

        output.append("=" * 60)
        output.append(f"Total: {total} | Successful: {successful} | Failed: {failed}")
        output.append("=" * 60)

        return '\n'.join(output)

    def print_results(self, results: List[Dict]) -> None:
        print(self.format_results(results))
