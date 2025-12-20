Feature: Language Support
  As a student
  I want to view and interact with activities in my preferred language
  So that I can understand the information better

  Background:
    Given the activities database supports English and Hungarian

  Scenario: View all activities in English
    When I request activities in "English"
    Then I should receive 9 activities
    And all activity names should be in English
    And I should see "Chess Club"
    And I should see "Programming Class"
    And I should see "Gym Class"

  Scenario: View all activities in Hungarian
    When I request activities in "Hungarian"
    Then I should receive 9 activities
    And all activity names should be in Hungarian
    And I should see "Sakk Klub"
    And I should see "Programozás Tanfolyam"
    And I should see "Tornaterem"

  Scenario: Default language is English
    When I request activities without specifying a language
    Then I should receive activities in English
    And I should see "Chess Club"

  Scenario: Activity structure includes all required fields
    When I request activities in "English"
    Then each activity should have a "description" field
    And each activity should have a "schedule" field
    And each activity should have a "max_participants" field
    And each activity should have a "participants" list

  Scenario: Participant lists are included in responses
    When I request activities in "English"
    Then "Chess Club" should show participants list
    And the participants list should include "michael@mergington.edu"
    And the participants list should include "daniel@mergington.edu"

  Scenario: Participants synchronized across both languages
    Given student "test@mergington.edu" is registered for "Chess Club"
    When I request activities in "English"
    Then "Chess Club" participants should include "test@mergington.edu"
    When I request activities in "Hungarian"
    Then "Sakk Klub" participants should include "test@mergington.edu"
