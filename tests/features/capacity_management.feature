Feature: Capacity Management
  As an admin
  I want to prevent signups when activities are at capacity
  So that the maximum participant limit is not exceeded

  Background:
    Given the activities database is initialized with capacity limits

  Scenario: Reject signup when activity is at capacity (English)
    Given "Chess Club" has maximum capacity of 12 participants
    And "Chess Club" currently has 2 participants
    When I fill all 10 available slots in "Chess Club"
    And I attempt to sign up one more student for "Chess Club" in "English"
    Then the signup should fail with status code 400
    And I should see error message "Activity is full"
    And "Chess Club" should have exactly 12 participants
    And the overflow student should not be in the participants list

  Scenario: Reject signup when activity is at capacity (Hungarian)
    Given "Sakk Klub" has maximum capacity of 12 participants
    And "Sakk Klub" currently has 2 participants
    When I fill all 10 available slots in "Sakk Klub"
    And I attempt to sign up one more student for "Sakk Klub" in "Hungarian"
    Then the signup should fail with status code 400
    And I should see error message "A tevékenység megtelt"
    And "Sakk Klub" should have exactly 12 participants

  Scenario: Allow signup when one spot below capacity
    Given "Gym Class" has maximum capacity of 30 participants
    And "Gym Class" currently has 1 participant
    When I fill 28 slots leaving one spot open in "Gym Class"
    And I sign up the final student for "Gym Class" in "English"
    Then the final signup should succeed with status code 200
    And "Gym Class" should have exactly 30 participants
    And the final student should be in the participants list

  Scenario: Sequential signups respect capacity limits
    Given "Programming Class" has maximum capacity of 20 participants
    And "Programming Class" currently has 2 participants
    When I sequentially fill all 18 available slots in "Programming Class"
    Then all 18 signups should succeed
    And "Programming Class" should have exactly 20 participants
    When I attempt 3 more signups for "Programming Class"
    Then all 3 overflow signups should fail with status code 400
    And "Programming Class" should still have exactly 20 participants

  Scenario: Concurrent signups compete for limited slots (Race Condition)
    Given "Chess Club" has maximum capacity of 12 participants
    And "Chess Club" currently has 11 participants leaving only 1 slot
    When 10 students attempt to sign up simultaneously for "Chess Club"
    Then exactly 1 signup should succeed with status code 200
    And exactly 9 signups should fail with status code 400
    And the failure message should be "Activity is full"
    And "Chess Club" should have exactly 12 participants
    And there should be no duplicate participants

  Scenario: Concurrent signups with multiple available slots
    Given "Programming Class" has maximum capacity of 10 participants
    And "Programming Class" currently has 7 participants leaving 3 slots
    When 10 students attempt to sign up simultaneously for "Programming Class"
    Then exactly 3 signups should succeed with status code 200
    And exactly 7 signups should fail with status code 400
    And "Programming Class" should have exactly 10 participants
    And there should be no duplicate participants

  Scenario: Cross-language concurrent signups respect same capacity
    Given "Chess Club" and "Sakk Klub" are the same activity with different translations
    And the activity has maximum capacity of 12 participants
    And the activity currently has 8 participants leaving 4 slots
    When 5 students sign up simultaneously for "Chess Club" in English
    And 5 students sign up simultaneously for "Sakk Klub" in Hungarian
    Then exactly 4 total signups should succeed across both languages
    And exactly 6 total signups should fail across both languages
    And the activity should have exactly 12 participants
    And both language endpoints should return the same participant list
