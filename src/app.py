import streamlit as st
import subprocess
import os
import json
from datetime import datetime, timedelta
from hypothesis import given, strategies as st_data
from hypothesis import example
import sys  # Import the sys module

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
    return [task for task in tasks if task.get("completed", False) == completed]

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
        task_recurrence = st.selectbox("Recurrence", [None, "daily", "weekly", "monthly"])
        task_instances = st.number_input("Number of recurrences", min_value=1, value=1) # added number of instances
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
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "recurrence": task_recurrence
            }
            if task_recurrence:
                recurring_tasks = create_recurring_tasks(new_task, task_instances)
                tasks.extend(recurring_tasks)
            else:
                tasks.append(new_task)
            save_tasks(tasks)
            st.sidebar.success("Task added successfully!")

    # Main area to display tasks
    st.header("Your Tasks")

    # Filter options
    col1, col2, col3 = st.columns(3) # Added a new column for sorting
    with col1:
        # Ensure tasks is not empty before trying to extract categories
        categories = ["All"]
        if tasks:
            unique_categories = list(set(task.get("category", "Other") for task in tasks))  # Use get()
            categories.extend(unique_categories)
        filter_category = st.selectbox("Filter by Category", categories)


    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Due Date", "Priority", "Category"]) #added sort by
    show_completed = st.checkbox("Show Completed Tasks")

    # Apply filters
    filtered_tasks = tasks.copy()
    if filter_category != "All":
        filtered_tasks = filter_tasks_by_category(filtered_tasks, filter_category)
    if filter_priority != "All":
        filtered_tasks = filter_tasks_by_priority(filtered_tasks, filter_priority)
    filtered_tasks = [task for task in filtered_tasks if not task.get("completed", False)] # Fix the filtering
    # Apply sorting
    if sort_by == "Due Date":
        filtered_tasks = sort_tasks(filtered_tasks, "due_date")
    elif sort_by == "Priority":
        filtered_tasks = sort_tasks(filtered_tasks, "priority")
    elif sort_by == "Category":
        filtered_tasks = sort_tasks(filtered_tasks, "category")

    # Display tasks
    for task in filtered_tasks:
        col1, col2 = st.columns([4, 1])
        with col1:
            if task.get("completed"):
                st.markdown(f"~~**{task['title']}**~~")
            else:
                st.markdown(f"**{task['title']}**")
            # Use get() with a default value to avoid KeyError
            st.write(task.get("description", ""))
            st.caption(f"Due: {task.get('due_date', 'N/A')} | Priority: {task.get('priority', 'N/A')} | Category: {task.get('category', 'N/A')}")
        with col2:
            if st.button("Complete" if not task.get("completed",False) else "Undo", key=f"complete_{task['id']}"):
                for t in tasks:
                    if t["id"] == task["id"]:
                        t["completed"] = not t.get("completed",False)
                        save_tasks(tasks)
                        st.rerun()
            if st.button("Edit", key=f"edit_{task['id']}"): #added edit button
                edited_task_data = {
                    "id": task["id"],
                    "title": st.text_input("Title", value=task["title"], key=f"edit_title_{task['id']}"),
                    "description": st.text_area("Description", value=task["description"], key=f"edit_description_{task['id']}"),
                    "priority": st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(task["priority"]), key=f"edit_priority_{task['id']}"),
                    "category": st.selectbox("Category", ["Work", "Personal", "School", "Other"], index=["Work", "Personal", "School", "Other"].index(task["category"]), key=f"edit_category_{task['id']}"),
                    "due_date": st.date_input("Due Date", value=datetime.strptime(task["due_date"], "%Y-%m-%d"), key=f"edit_due_date_{task['id']}").strftime("%Y-%m-%d"),
                    "completed": task.get("completed",False),
                    "created_at": task["created_at"]
                }
                edit_task(task["id"], edited_task_data)
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

    # BDD Test Execution
    def run_bdd_tests():
        """Runs the BDD tests using the 'behave' command."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            features_dir = os.path.join(script_dir, "features")  # Construct the full path
            result = subprocess.run(
                ["behave", features_dir],
                cwd=script_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            st.code(result.stdout)
            st.success("BDD tests executed successfully!")
        except subprocess.CalledProcessError as e:
            error_message = (
                f"Error running BDD tests:\n"
                f"  Command: {' '.join(e.cmd)}\n"
                f"  Return Code: {e.returncode}\n"
                f"  Standard Output:\n{e.stdout}\n"
                f"  Standard Error:\n{e.stderr}"
            )
            st.error(error_message)
        except FileNotFoundError:
            st.error("Behave is not installed or not found in the system's PATH. Please install it using 'pip install behave' and ensure it is correctly configured.")

    # Add a button to run BDD tests
    st.sidebar.header("Run Tests")
    st.sidebar.button("Run BDD Tests", on_click=run_bdd_tests) # Added BDD test button
    st.sidebar.button("Run Coverage Test", on_click=run_pytest_coverage)
    st.sidebar.button("Run Parameterized Test", on_click=run_pytest_parameterized)
    st.sidebar.button("Run Mocking Test", on_click=run_pytest_mocking)
    st.sidebar.button("Generate HTML Report", on_click=run_pytest_html_report)


    # Hypothesis tests
    def run_hypothesis_tests(): # Removed the st.cache_data decorator
        """
        Runs property-based tests using Hypothesis and displays the results.
        """
        results = []
        st.write("Running Hypothesis tests...") #prints
        print("Starting Hypothesis tests...")  # Add this print statement

        try:
            # Example 1: Test that the task title is always a string
            @given(st_data.text())
            @example(s="")
            def test_task_title_is_string(s):
                print(f"Running test_task_title_is_string with s = {s}")  # Add print
                assert isinstance(s, str)
                result_string = f"Test: Task title is string - Passed for: {s}"
                results.append(result_string)
                return result_string

            # Example 2: Test that the task description is always a string
            @given(st_data.text())
            @example(s="")
            def test_task_description_is_string(s):
                print(f"Running test_task_description_is_string with s = {s}") # Add Print
                assert isinstance(s, str)
                result_string = f"Test: Task description is string - Passed for: {s}"
                results.append(result_string)
                return result_string

            # Example 3: Test task priority is one of "High", "Medium", or "Low"
            @given(st_data.sampled_from(["High", "Medium", "Low"]))
            def test_task_priority_valid(p):
                print(f"Running test_task_priority_valid with p = {p}") # Add Print
                assert p in ["High", "Medium", "Low"]
                result_string = f"Test: Task priority is valid - Passed for: {p}"
                results.append(result_string)
                return result_string

            # Example 4: Test that the filter function returns a subset of the original tasks
            @given(st_data.lists(st_data.dictionaries(st_data.text(), st_data.text())))
            def test_filter_tasks_by_category_subset(tasks):
                print(f"Running test_filter_tasks_by_category_subset with tasks = {tasks}") # Add Print
                if not tasks:
                    return
                category = tasks[0].get("category")  # Use get to avoid KeyError
                filtered = filter_tasks_by_category(tasks, category)
                assert all(task in tasks for task in filtered)
                result_string = f"Test: Filtered tasks are subset - Passed for category: {category}"
                results.append(result_string)
                return result_string

            # Example 5:  Check that generate_unique_id generates unique IDs
            @given(st_data.lists(st_data.dictionaries(st_data.text(), st_data.text())))
            def test_generate_unique_id_is_unique(task_list):
                print(f"Running test_generate_unique_id_is_unique with task_list = {task_list}") # Add Print
                ids = [generate_unique_id(task_list + [{"id": i}]) for i in range(5)] # Generate 5 new IDs
                assert len(ids) == len(set(ids)) # Check for uniqueness
                result_string = "Test: Generate unique IDs - Passed"
                results.append(result_string)
                return result_string
        except Exception as e:
            error_string = f"Error: {e}"
            print(f"An error occurred during Hypothesis tests: {e}")  # Print any exceptions
            results.append(error_string)
            return results

        print("Finished running Hypothesis tests.")
        return results

    if st.sidebar.button("Run Hypothesis Tests"):
        hypothesis_results = run_hypothesis_tests()
        if hypothesis_results:  # Check if hypothesis_results is not empty
            st.write("Hypothesis Test Results:")
            for result in hypothesis_results:
                st.write(result)
        else:
            st.write("No Hypothesis tests were run or no results were generated.")

if __name__ == '__main__':
    main()
