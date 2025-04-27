import json
from datetime import datetime, timedelta

DEFAULT_TASKS_FILE = "tasks.json"

def load_tasks(file_path=DEFAULT_TASKS_FILE):
    """
    Load tasks from a JSON file.
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Warning: {file_path} contains invalid JSON. Creating new tasks list.")
        return []

def save_tasks(tasks, file_path=DEFAULT_TASKS_FILE):
    """
    Save tasks to a JSON file.
    """
    with open(file_path, "w") as f:
        json.dump(tasks, f, indent=2)

def generate_unique_id(tasks):
    """
    Generate a unique ID for a new task.
    """
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

def filter_tasks_by_priority(tasks, priority):
    """
    Filter tasks by priority level.
    """
    return [task for task in tasks if task.get("priority") == priority]

def filter_tasks_by_category(tasks, category):
    """
    Filter tasks by category.
    """
    return [task for task in tasks if task.get("category") == category]

def filter_tasks_by_completion(tasks, completed=True):
    """
    Filter tasks by completion status.
    """
    return [task for task in tasks if task.get("completed") == completed]

def search_tasks(tasks, query):
    """
    Search tasks by a text query in title and description.
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
    """
    today = datetime.now().strftime("%Y-%m-%d")
    return [
        task for task in tasks
        if not task.get("completed", False) and
            task.get("due_date", "") < today
    ]

def edit_task(task_id, updated_task):
    """
      Edit an existing task.

      Args:
          task_id (int): ID of the task to edit.
          updated_task (dict): Dictionary containing the updated task information.
      Raises:
          ValueError: If the task with the given ID is not found.
      """
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks[i].update(updated_task) #update the task
            save_tasks(tasks)
            return
    raise ValueError(f"Task with id {task_id} not found.")

def sort_tasks(tasks, sort_by="due_date"):
    """
    Sort tasks by a given criteria.

    Args:
        tasks (list): List of tasks to sort.
        sort_by (str): Criteria to sort by (e.g., "due_date", "priority", "category").

    Returns:
        list: Sorted list of tasks.
    """
    if not tasks:
        return []
    if sort_by == "due_date":
        return sorted(tasks, key=lambda x: datetime.strptime(x["due_date"], "%Y-%m-%d"))
    elif sort_by == "priority":
        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        return sorted(tasks, key=lambda x: priority_order[x["priority"]])
    elif sort_by == "category":
        return sorted(tasks, key=lambda x: x["category"])
    else:
        raise ValueError(f"Invalid sort_by value: {sort_by}")

def create_recurring_tasks(task, instances):
    """
    Creates recurring tasks based on the given task and number of instances.

    Args:
        task (dict): The base task.
        instances (int): The number of recurring task instances to create.

    Returns:
        list: A list of recurring task dictionaries.
    """
    recurring_tasks = []
    base_date = datetime.strptime(task["due_date"], "%Y-%m-%d")

    for i in range(instances):
        new_date = base_date + timedelta(days=i)
        new_task = task.copy()
        new_task["id"] = generate_unique_id([]) + i
        new_task["due_date"] = new_date.strftime("%Y-%m-%d")
        new_task["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        recurring_tasks.append(new_task)
    return recurring_tasks
