import json
import os
from datetime import datetime
from tasks import load_tasks, save_tasks, filter_tasks_by_priority, filter_tasks_by_category, filter_tasks_by_completion, search_tasks, get_overdue_tasks

def test_load_tasks_empty_file():
    """Test loading tasks from an empty file."""
    # Create an empty file for testing
    with open("empty_tasks.json", "w") as f:
        json.dump([], f)
    tasks = load_tasks("empty_tasks.json")
    assert tasks == []
    os.remove("empty_tasks.json")  # Clean up

def test_load_tasks_nonexistent_file():
    """Test loading tasks from a nonexistent file."""
    tasks = load_tasks("nonexistent_tasks.json")
    assert tasks == []

def test_load_tasks_corrupted_file():
    """Test loading tasks from a corrupted JSON file."""
    with open("corrupted_tasks.json", "w") as f:
        f.write("invalid json")
    tasks = load_tasks("corrupted_tasks.json")
    assert tasks == []
    os.remove("corrupted_tasks.json")

def test_save_tasks():
    """Test saving tasks to a file."""
    tasks = [{"id": 1, "title": "Test Task", "description": "Test Description"}]
    save_tasks(tasks, "test_save_tasks.json")
    loaded_tasks = load_tasks("test_save_tasks.json")
    assert loaded_tasks == tasks
    os.remove("test_save_tasks.json")

def test_filter_tasks_by_priority():
    """Test filtering tasks by priority."""
    tasks = [
        {"id": 1, "title": "Task 1", "priority": "High"},
        {"id": 2, "title": "Task 2", "priority": "Medium"},
        {"id": 3, "title": "Task 3", "priority": "High"},
    ]
    filtered_tasks = filter_tasks_by_priority(tasks, "High")
    assert len(filtered_tasks) == 2
    assert all(task["priority"] == "High" for task in filtered_tasks)

def test_filter_tasks_by_category():
    """Test filtering tasks by category."""
    tasks = [
        {"id": 1, "title": "Task 1", "category": "Work"},
        {"id": 2, "title": "Task 2", "category": "Personal"},
        {"id": 3, "title": "Task 3", "category": "Work"},
    ]
    filtered_tasks = filter_tasks_by_category(tasks, "Work")
    assert len(filtered_tasks) == 2
    assert all(task["category"] == "Work" for task in filtered_tasks)

def test_filter_tasks_by_completion():
    tasks = [
        {"id": 1, "title": "Task 1", "completed": True},
        {"id": 2, "title": "Task 2", "completed": False},
        {"id": 3, "title": "Task 3", "completed": True},
    ]
    completed_tasks = filter_tasks_by_completion(tasks, completed=True)
    assert len(completed_tasks) == 2
    assert all(task["completed"] == True for task in completed_tasks)

    incomplete_tasks = filter_tasks_by_completion(tasks, completed=False)
    assert len(incomplete_tasks) == 1
    assert incomplete_tasks[0]["completed"] == False

def test_search_tasks():
    """Test searching tasks by title and description."""
    tasks = [
        {"id": 1, "title": "Grocery Shopping", "description": "Buy milk and eggs"},
        {"id": 2, "title": "Write Report", "description": "Finish the quarterly report"},
        {"id": 3, "title": "Meeting", "description": "Team meeting at 2pm"},
    ]
    results = search_tasks(tasks, "report")
    assert len(results) == 1
    assert results[0]["title"] == "Write Report"
    results = search_tasks(tasks, "meeting")
    assert len(results) == 1
    assert results[0]["title"] == "Meeting"
    results = search_tasks(tasks, "Grocer")
    assert len(results) == 1
    assert results[0]["title"] == "Grocery Shopping"
    results = search_tasks(tasks, "eggs")
    assert len(results) == 1
    assert results[0]["title"] == "Grocery Shopping"
    results = search_tasks(tasks, "nonexistent")
    assert len(results) == 0

def test_get_overdue_tasks():
    tasks = [
        {"id": 1, "title": "Task 1", "due_date": "2024-01-01", "completed": False},
        {"id": 2, "title": "Task 2", "due_date": datetime.now().strftime("%Y-%m-%d"), "completed": False},
        {"id": 3, "title": "Task 3", "due_date": "2023-01-01", "completed": True},
        {"id": 4, "title": "Task 4", "due_date": "2025-01-01", "completed": False},
    ]
    overdue_tasks = get_overdue_tasks(tasks)
    # Depends on the date the test is run.
    assert len(overdue_tasks) == 1
    assert overdue_tasks[0]["title"] == "Task 1"
