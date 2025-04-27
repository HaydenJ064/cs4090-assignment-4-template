import json
import os
from datetime import datetime, date

# Default file path for task storage
DEFAULT_TASKS_FILE = os.path.join(os.path.expanduser("~"), "tasks.json")

def load_tasks(file_path=DEFAULT_TASKS_FILE):
    """
    Load tasks from a JSON file.  Handles file not found and JSON decode errors.

    Args:
        file_path (str): Path to the JSON file containing tasks

    Returns:
        list: List of task dictionaries, empty list if file doesn't exist or is corrupted.
    """
    try:
        with open(file_path, "r") as f:
            tasks = json.load(f)
            # Convert due_date strings to date objects
            for task in tasks:
                if "due_date" in task and isinstance(task["due_date"], str):
                    try:
                        task["due_date"] = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
                    except ValueError:
                        print(f"Invalid date format in task: {task}.  Expected %Y-%m-%d.")
                        task["due_date"] = None
            return tasks
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Error: {file_path} contains invalid JSON.  Returning an empty task list.")
        return []

def save_tasks(tasks, file_path=DEFAULT_TASKS_FILE):
    """
    Save tasks to a JSON file.

    Args:
        tasks (list): List of task dictionaries
        file_path (str): Path to save the JSON file
    """
    # Convert date objects to strings before saving
    tasks_serializable = []
    for task in tasks:
        task_copy = task.copy()  # Create a copy to avoid modifying the original list
        if "due_date" in task_copy and isinstance(task_copy["due_date"], date):
            task_copy["due_date"] = task_copy["due_date"].strftime("%Y-%m-%d")
        tasks_serializable.append(task_copy)

    with open(file_path, "w") as f:
        json.dump(tasks_serializable, f, indent=2)

def generate_unique_id(tasks):
    """
    Generate a unique ID for a new task.

    Args:
        tasks (list): List of existing task dictionaries

    Returns:
        int: A unique ID for a new task
    """
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

def filter_tasks_by_priority(tasks, priority):
    """
    Filter tasks by priority level.

    Args:
        tasks (list): List of task dictionaries
        priority (str): Priority level to filter by (High, Medium, Low)

    Returns:
        list: Filtered list of tasks matching the priority
    """
    return [task for task in tasks if task.get("priority") == priority]

def filter_tasks_by_category(tasks, category):
    """
    Filter tasks by category.

    Args:
        tasks (list): List of task dictionaries
        category (str): Category to filter by

    Returns:
        list: Filtered list of tasks matching the category
    """
    return [task for task in tasks if task.get("category") == category]

def filter_tasks_by_completion(tasks, completed=True):
    """
    Filter tasks by completion status.

    Args:
        tasks (list): List of task dictionaries
        completed (bool): Completion status to filter by

    Returns:
        list: Filtered list of tasks matching the completion status
    """
    return [task for task in tasks if task.get("completed") == completed]

def search_tasks(tasks, query):
    """
    Search tasks by a text query in title and description.

    Args:
        tasks (list): List of task dictionaries
        query (str): Search query

    Returns:
        list: Filtered list of tasks matching the search query
    """
    query = query.lower()
    return [
        task for task in tasks
        if query in task.get("title", "").lower() or
           query in task.get("description", "").lower()
    ]

def get_overdue_tasks(tasks):
    """
    Get tasks that are past their due date and not completed.

    Args:
        tasks (list): List of task dictionaries

    Returns:
        list: List of overdue tasks
    """
    today = date.today()
    return [
        task for task in tasks
        if not task.get("completed", False) and
        task.get("due_date") and  # Check if due_date exists and is not None
        task["due_date"] < today
    ]
