import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class TaskTracker:
    """Track task execution status and completion metrics in JSON format."""

    def __init__(self, project_path: str | Path, project_name: str):
        """
        Initialize task tracker.

        Args:
            project_path: Path to the project directory
            project_name: Human-readable name of the project
        """
        self.project_path = Path(project_path)
        self.project_name = project_name
        self.tracker_file = self.project_path / 'task-completion.json'
        self.data = self._init_tracker()

    def _init_tracker(self) -> Dict[str, Any]:
        """
        Initialize or load task-completion.json.

        Returns:
            dict: Task tracker data structure
        """
        # If file exists, load it
        if self.tracker_file.exists():
            try:
                content = self.tracker_file.read_text()
                return json.loads(content)
            except (json.JSONDecodeError, IOError):
                pass

        # Default structure
        return {
            'project_name': self.project_name,
            'generated_at': datetime.now().isoformat(),
            'tasks': [],
            'summary': {
                'total_tasks': 0,
                'completed': 0,
                'in_progress': 0,
                'pending': 0,
                'failed': 0,
                'overall_progress': 0.0,
            },
        }

    def start_task(self, task_id: str, title: str, skill_used: str = None) -> None:
        """
        Mark a task as in_progress.

        Args:
            task_id: Unique task identifier (e.g., "01-database-schema")
            title: Human-readable task title
            skill_used: Which skill/agent executed this task
        """
        # Check if task already exists
        existing_task = None
        for task in self.data['tasks']:
            if task['id'] == task_id:
                existing_task = task
                break

        if existing_task:
            # Update existing task
            existing_task['status'] = 'in_progress'
            existing_task['started_at'] = datetime.now().isoformat()
            if skill_used:
                existing_task['skill_used'] = skill_used
        else:
            # Create new task
            task = {
                'id': task_id,
                'title': title,
                'status': 'in_progress',
                'started_at': datetime.now().isoformat(),
                'completed_at': None,
                'skill_used': skill_used,
                'files_generated': [],
                'test_coverage': 0,
                'status_details': {
                    'success': False,
                    'errors': [],
                    'warnings': [],
                },
            }
            self.data['tasks'].append(task)

        self._update_summary()

    def complete_task(
        self,
        task_id: str,
        files_generated: List[str] = None,
        test_coverage: int = 0,
    ) -> None:
        """
        Mark a task as completed.

        Args:
            task_id: Unique task identifier
            files_generated: List of files created/modified by this task
            test_coverage: Test coverage percentage (0-100)
        """
        task = self._find_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task['status'] = 'completed'
        task['completed_at'] = datetime.now().isoformat()

        if files_generated:
            task['files_generated'] = files_generated

        # Ensure test_coverage is within valid range
        task['test_coverage'] = max(0, min(100, test_coverage))

        task['status_details']['success'] = True
        self._update_summary()

    def fail_task(self, task_id: str, error_message: str = None, errors: List[str] = None) -> None:
        """
        Mark a task as failed.

        Args:
            task_id: Unique task identifier
            error_message: Main error message (deprecated, use errors instead)
            errors: List of error messages
        """
        task = self._find_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task['status'] = 'failed'
        task['completed_at'] = datetime.now().isoformat()
        task['status_details']['success'] = False

        # Handle both error_message and errors list
        if error_message:
            task['status_details']['errors'].append(error_message)

        if errors:
            task['status_details']['errors'].extend(errors)

        self._update_summary()

    def add_warning(self, task_id: str, warning: str) -> None:
        """
        Add a warning to a task's status details.

        Args:
            task_id: Unique task identifier
            warning: Warning message
        """
        task = self._find_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if warning not in task['status_details']['warnings']:
            task['status_details']['warnings'].append(warning)

    def _find_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task dictionary or None if not found
        """
        for task in self.data['tasks']:
            if task['id'] == task_id:
                return task
        return None

    def _update_summary(self) -> None:
        """Update overall summary statistics."""
        tasks = self.data['tasks']

        summary = {
            'total_tasks': len(tasks),
            'completed': sum(1 for t in tasks if t['status'] == 'completed'),
            'in_progress': sum(1 for t in tasks if t['status'] == 'in_progress'),
            'pending': sum(1 for t in tasks if t['status'] == 'pending'),
            'failed': sum(1 for t in tasks if t['status'] == 'failed'),
        }

        # Calculate overall progress percentage
        if summary['total_tasks'] > 0:
            summary['overall_progress'] = (
                (summary['completed'] / summary['total_tasks']) * 100
            )
        else:
            summary['overall_progress'] = 0.0

        self.data['summary'] = summary
        self.data['generated_at'] = datetime.now().isoformat()

    def save(self) -> None:
        """Write tracker data to JSON file."""
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tracker_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get the current summary statistics.

        Returns:
            dict: Summary data
        """
        return self.data['summary']

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific task's data.

        Args:
            task_id: Task identifier

        Returns:
            Task dictionary or None if not found
        """
        return self._find_task(task_id)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks.

        Returns:
            List of task dictionaries
        """
        return self.data['tasks']

    def get_progress(self) -> float:
        """
        Get overall progress percentage.

        Returns:
            float: Progress percentage (0-100)
        """
        return self.data['summary']['overall_progress']
