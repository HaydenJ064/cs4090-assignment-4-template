Feature: Task Management
      As a user, I want to be able to manage my tasks.

      Scenario: Add a new task
        Given I am on the main page
        When I add a task with title "Buy groceries" and description "Milk, eggs, bread"
        Then I should see the task "Buy groceries" in the list

      Scenario: Complete a task
        Given I have a task "Buy groceries"
        When I complete the task "Buy groceries"
        Then I should see that the task "Buy groceries" is completed
