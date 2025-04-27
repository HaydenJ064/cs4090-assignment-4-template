from behave import given, when, then

@given('I am on the main page')
def step_impl(context):
  #  Add code here to navigate to your Streamlit app's main page.
  #  For example, if you are using st.session_state, you might initialize it here
  context.tasks = [] # Initialize an empty list of tasks

@when('I add a task with title "{title}" and description "{description}"')
def step_impl(context, title, description):
  # Add code here to add a task to your application's data structure.
  #  This is where you would interact with your Streamlit app's state.
  context.tasks.append({"title": title, "description": description, "completed": False})

@then('I should see the task "{title}" in the list')
def step_impl(context, title):
  #  Add code here to check if the task is displayed correctly in your Streamlit app.
  #  You'll need to access the application's state and assert that the task is present.
  task_titles = [task["title"] for task in context.tasks]
  assert title in task_titles

@given('I have a task "{title}"')
def step_impl(context, title):
  context.tasks = [{"title": title, "completed": False}]

@when('I complete the task "{title}"')
def step_impl(context, title):
  for task in context.tasks:
    if task["title"] == title:
      task["completed"] = True

@then('I should see that the task "{title}" is completed')
def step_impl(context, title):
  for task in context.tasks:
    if task["title"] == title:
      assert task["completed"] == True
