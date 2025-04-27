import pytest
from unittest.mock import patch
from tasks import load_tasks, filter_tasks_by_priority, generate_unique_id, edit_task, sort_tasks, create_recurring_tasks
from datetime import datetime, timedelta
import json

# Use the same DEFAULT_TASKS_FILE as app.py
DEFAULT_TASKS_FILE = "tasks.json"

# Create a simple fixture for setting up test data
@pytest.fixture
def sample_tasks():
    # Define tasks directly within the fixture for consistency and isolation
    tasks = [
        {"id": 1, "title": "Task 1", "priority": "High", "category": "Work", "completed": False, "due_date": "2025-01-01", "created_at": "2024-08-01 12:00:00"},
        {"id": 2, "title": "Task 2", "priority": "Medium", "category": "Personal", "completed": True, "due_date": "2025-01-05", "created_at": "2024-08-01 12:00:00"},
        {"id": 3, "title": "Task 3", "priority": "Low", "category": "Work", "completed": False, "due_date": "2025-01-10", "created_at": "2024-08-01 12:00:00"},
        {"id": 4, "title": "Task 4", "priority": "High", "category": "Personal", "completed": False, "due_date": "2025-02-01", "created_at": "2024-08-01 12:00:00"},
    ]
    #  Use a context manager to handle file operations
    with open(DEFAULT_TASKS_FILE, "w") as f:
        json.dump(tasks, f)
    return tasks  # Return the data, not the file path

# Parameterized test function
@pytest.mark.parametrize(
    "priority, expected_count",
    [
        ("High", 2),
        ("Medium", 1),
        ("Low", 1),
        ("Invalid", 0),  # Test with an invalid priority
    ],
)
def test_filter_tasks_by_priority_parameterized(sample_tasks, priority, expected_count):
    """
    Test filter_tasks_by_priority with various priority levels.
    This test reads from the file created by the fixture.
    """
    tasks = load_tasks(DEFAULT_TASKS_FILE) # Load tasks *within* the test
    filtered_tasks = filter_tasks_by_priority(tasks, priority)
    assert len(filtered_tasks) == expected_count, f"Expected {expected_count} tasks for priority '{priority}', got {len(filtered_tasks)}"

# Mocking test function
def test_generate_unique_id_mock():
    """
    Test generate_unique_id using a mock to control the return value of
    the max() function.
    """
    # Create a mock list of task IDs.
    existing_ids = [1, 5, 10]

    # Patch the max function.  Any code that calls max() within generate_unique_id
    # will now get the return value specified here.
    with patch("builtins.max", return_value=10):
        # Call the function we want to test.
        next_id = generate_unique_id([{"id": i} for i in existing_ids])
    # Assert the result is what we expect, given that max() was mocked
    assert next_id == 11, "Should return max ID + 1"

    # Test with an empty list
    with patch("builtins.max", side_effect=ValueError("max() arg is an empty sequence")):
        next_id = generate_unique_id([])
    assert next_id == 1, "Should return 1 when task list is empty"

def test_edit_task():
    """
    Test editing an existing task.
    """
    # 1. Arrange: Create an initial task
    initial_tasks = [
        {"id": 1, "title": "Old Title", "description": "Old Description", "priority": "Medium", "category": "Personal", "due_date": "2024-08-01", "completed":False, "created_at": "2024-08-01 12:00:00"}
    ]
    with open(DEFAULT_TASKS_FILE, "w") as f:
        json.dump(initial_tasks, f)

    # 2. Act: Edit the task
    edited_task = {
        "id": 1, "title": "New Title", "description": "New Description", "priority": "High", "category": "Work", "due_date": "2024-08-05", "completed": True, "created_at": "2024-08-01 12:00:00"
    }
    edit_task(1, edited_task) # Call a function that doesn't exist yet

    # 3. Assert: Load the tasks and check if the task was edited correctly
    updated_tasks = load_tasks()
    assert len(updated_tasks) == 1
    assert updated_tasks[0] == edited_task

def test_sort_tasks_by_due_date():
    """Test sorting tasks by due date."""
    # 1. Arrange: Create unsorted tasks
    tasks = [
        {"id": 1, "title": "Task 1", "due_date": "2024-08-05", "created_at": "2024-08-01 12:00:00"},
        {"id": 2, "title": "Task 2", "due_date": "2024-08-01", "created_at": "2024-08-01 12:00:00"},
        {"id": 3, "title": "Task 3", "due_date": "2024-08-10", "created_at": "2024-08-01 12:00:00"},
    ]
    with open(DEFAULT_TASKS_FILE, "w") as f:
        json.dump(tasks, f)

    # 2. Act: Sort the tasks
    sorted_tasks = sort_tasks(load_tasks(), "due_date")

    # 3. Assert: Check if the tasks are sorted correctly
    assert [task["id"] for task in sorted_tasks] == [2, 1, 3]

def test_create_recurring_task():
    """Test creating a recurring task."""
    # 1. Arrange

    # 2. Act
    recurring_task = {
        "title": "Recurring Task",
        "description": "This task repeats daily",
        "priority": "Medium",
        "category": "Personal",
        "due_date": "2024-08-01",
        "recurrence": "daily",  # "daily", "weekly", "monthly", None
    }
    created_tasks = create_recurring_tasks(recurring_task, 3)  # Create 3 instances

    # 3. Assert
    assert len(created_tasks) == 3
    assert created_tasks[0]["due_date"] == "2024-08-01"
    assert created_tasks[1]["due_date"] == "2024-08-02"
    assert created_tasks[2]["due_date"] == "2024-08-03"
