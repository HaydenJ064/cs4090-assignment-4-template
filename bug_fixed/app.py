import streamlit as st
from datetime import datetime, date
from tasks import load_tasks, save_tasks, generate_unique_id, filter_tasks_by_priority, filter_tasks_by_category

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

        if submit_button:
            if not task_title:
                st.sidebar.error("Task title is required.")
            elif not task_due_date:
                st.sidebar.error("Task due date is required.")
            else:
                new_task = {
                    "id": generate_unique_id(tasks),
                    "title": task_title,
                    "description": task_description,
                    "priority": task_priority,
                    "category": task_category,
                    "due_date": task_due_date,
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
        filter_category = st.selectbox("Filter by Category", ["All"] + list(set(task.get("category") for task in tasks)))
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
        filtered_tasks = [task for task in filtered_tasks if not task.get("completed", False)]

    # Display tasks
    if not filtered_tasks:
        st.write("No tasks to display.")
    else:
        for task in filtered_tasks:
            col1, col2 = st.columns([4, 1])
            with col1:
                if task.get("completed"):
                    st.markdown(f"~~**{task.get('title', 'No Title')}**~~")
                else:
                    st.markdown(f"**{task.get('title', 'No Title')}**")
                st.write(task.get("description", "No Description"))
                due_date_str = task.get("due_date")
                if isinstance(due_date_str, date):
                    due_date_str = due_date_str.strftime("%Y-%m-%d")
                st.caption(f"Due: {due_date_str} | Priority: {task.get('priority', 'N/A')} | Category: {task.get('category', 'N/A')}")
            with col2:
                if st.button("Complete" if not task.get("completed") else "Undo", key=f"complete_{task['id']}"):
                    for t in tasks:
                        if t["id"] == task["id"]:
                            t["completed"] = not t["completed"]
                            save_tasks(tasks)
                            st.rerun()
                if st.button("Delete", key=f"delete_{task['id']}"):
                    tasks = [t for t in tasks if t["id"] != task["id"]]
                    save_tasks(tasks)
                    st.rerun()

if __name__ == "__main__":
    main()
