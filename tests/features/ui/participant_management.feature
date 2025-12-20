Feature: Participant Management
  As a student
  I want to sign up for and unregister from activities
  So that I can manage my extracurricular participation

  Background:
    Given I am on the activities page
    And the page has loaded completely
    And the page is displayed in "English"

  Scenario: Successfully sign up for an activity
    Given I have email "uitest@mergington.edu"
    When I enter my email in the signup form
    And I select "Chess Club" from the activity dropdown
    And I click the signup button
    Then I should see a success message containing "Signed up uitest@mergington.edu for Chess Club"
    And "Chess Club" should have participant "uitest@mergington.edu"
    And the signup form should be reset

  Scenario: Delete participant with confirmation
    Given "Chess Club" has participant "michael@mergington.edu"
    When I delete participant "michael@mergington.edu" from "Chess Club" and confirm
    Then I should see a success message
    And "Chess Club" should not have participant "michael@mergington.edu"

  Scenario: Cancel delete keeps participant
    Given "Chess Club" has participant "michael@mergington.edu"
    When I delete participant "michael@mergington.edu" from "Chess Club" and cancel
    Then "Chess Club" should have participant "michael@mergington.edu"

  Scenario: Cannot sign up for the same activity twice
    Given I have email "duplicate@mergington.edu"
    And I sign up for "Chess Club" with email "duplicate@mergington.edu"
    When I sign up for "Chess Club" with email "duplicate@mergington.edu"
    Then I should see an error message
    And the error should contain "already signed up"

  Scenario: Signup when activity is full shows error
    Given "Chess Club" is at full capacity
    When I sign up for "Chess Club" with email "overflow@mergington.edu"
    Then I should see an error message
    And the error should contain "Activity is full"
    And "Chess Club" should not have participant "overflow@mergington.edu"

  Scenario: Unregister and signup again workflow
    Given I have email "workflow@mergington.edu"
    And I sign up for "Gym Class" with email "workflow@mergington.edu"
    And "Gym Class" has participant "workflow@mergington.edu"
    When I delete participant "workflow@mergington.edu" from "Gym Class" and confirm
    Then "Gym Class" should not have participant "workflow@mergington.edu"
    When I sign up for "Gym Class" with email "workflow@mergington.edu"
    Then I should see a success message
    And "Gym Class" should have participant "workflow@mergington.edu"

  Scenario: Multiple students can sign up for the same activity
    Given I sign up for "Programming Class" with email "student1@mergington.edu"
    When I sign up for "Programming Class" with email "student2@mergington.edu"
    Then "Programming Class" should have participant "student1@mergington.edu"
    And "Programming Class" should have participant "student2@mergington.edu"

  Scenario: Success message auto-hides after 5 seconds
    Given I sign up for "Chess Club" with email "autohide@mergington.edu"
    Then I should see a success message
    And the message should be visible
    When I wait for 6 seconds
    Then the message should not be visible
