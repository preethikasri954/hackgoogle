import subprocess
import json
import os
import sys

class Analyzer:
    def run_bandit(self, repo_path):
        """
        Runs bandit on the repo_path and returns a list of issues.
        """
        print(f"Running Bandit on {repo_path}...")
        # Run bandit and dump to a temp json file
        output_file = "bandit_report.json"
        
        # -r: recursive, -f: format, -o: output file
        cmd = [sys.executable, "-m", "bandit", "-r", repo_path, "-f", "json", "-o", output_file]
        
        try:
            result = subprocess.run(cmd, check=False, capture_output=True) 
            # Bandit returns 1 if issues found, so we don't check=True
            if result.returncode not in [0, 1]:
                 print(f"Bandit failed: {result.stderr}")
                 return {"error": "Bandit execution failed"}
        except FileNotFoundError:
            return {"error": "Bandit not installed"}

        if not os.path.exists(output_file):
            return []

        with open(output_file, "r") as f:
            data = json.load(f)
        
        # Cleanup
        os.remove(output_file)
        
        results = data.get("results", [])
        return self._filter_results(results)

    def _filter_results(self, results):
        """
        Filters for high/medium severity.
        """
        filtered = []
        for issue in results:
            if issue["issue_confidence"] in ["LOW", "MEDIUM", "HIGH"]:
                filtered.append({
                    "filename": issue["filename"],
                    "line_number": issue["line_number"],
                    "issue_text": issue["issue_text"],
                    "code": issue["code"],
                    "more_info": issue["more_info"],
                    "cwe": issue.get("cwe_id", "Unknown") # hypothetical, bandit json has specific fields
                })
        return filtered
