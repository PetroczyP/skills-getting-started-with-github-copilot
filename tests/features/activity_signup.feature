Feature: Activity Signup
  As a student
  I want to sign up for extracurricular activities
  So that I can participate in school programs

  Background:
    Given the activities database is initialized
    And the Chess Club has 2 existing participants

  Scenario: Successful signup for activity with available capacity (English)
    Given I am a new student with email "newstudent@mergington.edu"
    When I sign up for "Chess Club" in "English"
    Then the signup should succeed with status code 200
    And I should see confirmation message containing "Signed up newstudent@mergington.edu for Chess Club"
    And "Chess Club" in "English" should have 3 participants
    And "newstudent@mergington.edu" should be in "Chess Club" participants

  Scenario: Successful signup for activity with available capacity (Hungarian)
    Given I am a new student with email "ujdiak@mergington.edu"
    When I sign up for "Sakk Klub" in "Hungarian"
    Then the signup should succeed with status code 200
    And I should see confirmation message containing "ujdiak@mergington.edu sikeresen jelentkezett: Sakk Klub"
    And "Sakk Klub" in "Hungarian" should have 3 participants
    And "ujdiak@mergington.edu" should be in "Sakk Klub" participants

  Scenario: Signup for nonexistent activity returns error
    Given I am a new student with email "student@mergington.edu"
    When I sign up for "Nonexistent Club" in "English"
    Then the signup should fail with status code 404
    And I should see error message "Activity not found"

  Scenario: Prevent duplicate signup
    Given student "michael@mergington.edu" is already registered for "Chess Club"
    When I sign up for "Chess Club" in "English" with email "michael@mergington.edu"
    Then the signup should fail with status code 400
    And I should see error message "Student already signed up for this activity"

  Scenario: Multiple students can sign up for same activity
    Given "Programming Class" has capacity available
    When student "student1@mergington.edu" signs up for "Programming Class" in "English"
    And student "student2@mergington.edu" signs up for "Programming Class" in "English"
    Then both signups should succeed
    And "Programming Class" should include both "student1@mergington.edu" and "student2@mergington.edu"

  Scenario: Participants synced across languages
    Given I am a new student with email "bilingual@mergington.edu"
    When I sign up for "Sakk Klub" in "Hungarian"
    Then "bilingual@mergington.edu" should be in "Sakk Klub" participants in "Hungarian"
    And "bilingual@mergington.edu" should be in "Chess Club" participants in "English"
