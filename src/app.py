import streamlit as st
import subprocess
import os
import json
from datetime import datetime

# File path for task storage (moved to top for global access)
DEFAULT_TASKS_FILE = "tasks.json"

def load_tasks(file_path=DEFAULT_TASKS_FILE):
    """
    Load tasks from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing tasks

    Returns:
        list: List of task dictionaries, empty list if file doesn't exist
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        # Handle corrupted JSON file
        print(f"Warning: {file_path} contains invalid JSON. Creating new tasks list.")
        return []

def save_tasks(tasks, file_path=DEFAULT_TASKS_FILE):
    """
    Save tasks to a JSON file.

    Args:
        tasks (list): List of task dictionaries
        file_path (str): Path to save the JSON file
    """
    with open(file_path, "w") as f:
        json.dump(tasks, f, indent=2)

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
    today = datetime.now().strftime("%Y-%m-%d")
    return [
        task for task in tasks
        if not task.get("completed", False) and
            task.get("due_date", "") < today
    ]

def main():
    st.title("To-Do Application")

    # Load existing tasks
    tasks = load_tasks()

    # Sidebar for adding new tasks
    st.sidebar.header("Add New Task")

    # Task creation form
    with st.sidebar.form("new_task_form"):
        task_title = st.text_input("Task Title")
        task_description = st.text_area("Description")
        task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        task_category = st.selectbox("Category", ["Work", "Personal", "School", "Other"])
        task_due_date = st.date_input("Due Date")
        submit_button = st.form_submit_button("Add Task")

        if submit_button and task_title:
            new_task = {
                "id": generate_unique_id(tasks),
                "title": task_title,
                "description": task_description,
                "priority": task_priority,
                "category": task_category,
                "due_date": task_due_date.strftime("%Y-%m-%d"),
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            tasks.append(new_task)
            save_tasks(tasks)
            st.sidebar.success("Task added successfully!")

    # Main area to display tasks
    st.header("Your Tasks")

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox("Filter by Category", ["All"] + list(set([task["category"] for task in tasks])))
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])

    show_completed = st.checkbox("Show Completed Tasks")

    # Apply filters
    filtered_tasks = tasks.copy()
    if filter_category != "All":
        filtered_tasks = filter_tasks_by_category(filtered_tasks, filter_category)
    if filter_priority != "All":
        filtered_tasks = filter_tasks_by_priority(filtered_tasks, filter_priority)
    if not show_completed:
        filtered_tasks = [task for task in filtered_tasks if not task["completed"]]

    # Display tasks
    for task in filtered_tasks:
        col1, col2 = st.columns([4, 1])
        with col1:
            if task["completed"]:
                st.markdown(f"~~**{task['title']}**~~")
            else:
                st.markdown(f"**{task['title']}**")
            # Use get() with a default value to avoid KeyError
            st.write(task.get("description", ""))  
            st.caption(f"Due: {task['due_date']} | Priority: {task['priority']} | Category: {task['category']}")
        with col2:
            if st.button("Complete" if not task["completed"] else "Undo", key=f"complete_{task['id']}"):
                for t in tasks:
                    if t["id"] == task["id"]:
                        t["completed"] = not t["completed"]
                        save_tasks(tasks)
                        st.rerun()
            if st.button("Delete", key=f"delete_{task['id']}"):
                tasks = [t for t in tasks if t["id"] != task["id"]]
                save_tasks(tasks)
                st.rerun()

    # Pytest functions
    def run_pytest_coverage():
        """Runs pytest with coverage and displays the output."""
        try:
            # Ensure pytest runs in the correct directory.
            script_dir = os.path.dirname(os.path.abspath(__file__))
            result = subprocess.run(
                ["pytest", "--cov=.", "-vv"],  # Change --cov=tasks.py to --cov=.
                cwd=script_dir,  # Set the current working directory
                capture_output=True,
                text=True,
                check=True,
            )
            st.code(result.stdout)
            st.success("Coverage test executed successfully!")
        except subprocess.CalledProcessError as e:
            st.error(f"Error running coverage test: {e.stderr}")

    def run_pytest_parameterized():
        """Runs a parameterized pytest test and displays the output."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            result = subprocess.run(
                ["pytest", "test_tasks.py::test_filter_tasks_by_priority_parameterized", "-vv"],
                cwd=script_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            st.code(result.stdout)
            st.success("Parameterized test executed successfully!")
        except subprocess.CalledProcessError as e:
            st.error(f"Error running parameterized test: {e.stderr}")

    def run_pytest_mocking():
        """Runs pytest with a mock test and displays the output."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            result = subprocess.run(
                ["pytest", "test_tasks.py::test_generate_unique_id_mock", "-vv"],
                cwd=script_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            st.code(result.stdout)
            st.success("Mocking test executed successfully!")
        except subprocess.CalledProcessError as e:
            st.error(f"Error running mocking test: {e.stderr}")

    def run_pytest_html_report():
        """Runs pytest and generates an HTML report."""
        report_path = "pytest_report.html"
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            result = subprocess.run(
                ["pytest", "--html=" + report_path, "-vv"],
                cwd=script_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            st.code(result.stdout)
            # Display the report. Use a file reader.
            with open(os.path.join(script_dir, report_path), "r") as f:
                html_report = f.read()
            st.components.v1.html(html_report, height=800, scrolling=True)  # Adjust height as needed.
            st.success(f"HTML report generated at {report_path}!")
        except subprocess.CalledProcessError as e:
            st.error(f"Error running pytest and generating report: {e.stderr}")
        except Exception as ex:
            st.error(f"Error displaying the HTML report: {ex}")

    # Add buttons for running pytest functions
    st.sidebar.header("Run Pytest")
    st.sidebar.button("Run Coverage Test", on_click=run_pytest_coverage)
    st.sidebar.button("Run Parameterized Test", on_click=run_pytest_parameterized)
    st.sidebar.button("Run Mocking Test", on_click=run_pytest_mocking)
    st.sidebar.button("Generate HTML Report", on_click=run_pytest_html_report)

if __name__ == "__main__":
    main()
