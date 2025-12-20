Feature: Activity Display
  As a student
  I want to view all available extracurricular activities
  So that I can see what options are available to me

  Background:
    Given I am on the activities page
    And the page has loaded completely

  Scenario: All activities are displayed
    Given the page is displayed in "English"
    Then I should see 9 activities in the list
    And I should see activity "Chess Club"
    And I should see activity "Programming Class"
    And I should see activity "Gym Class"
    And I should see activity "Soccer Team"
    And I should see activity "Swimming Club"
    And I should see activity "Drama Club"
    And I should see activity "Art Studio"
    And I should see activity "Debate Team"
    And I should see activity "Science Olympiad"

  Scenario: Activity cards show all required information
    Given the page is displayed in "English"
    Then "Chess Club" should display a description
    And "Chess Club" should display a schedule
    And "Chess Club" should display spots remaining
    And "Chess Club" should display current participants

  Scenario: Spots remaining are calculated correctly
    Given the page is displayed in "English"
    And "Chess Club" has max participants of 12
    And "Chess Club" has 2 current participants
    Then "Chess Club" should show 10 spots remaining

  Scenario: Activity dropdown contains all activities
    Given the page is displayed in "English"
    Then the activity dropdown should contain 9 activities
    And the activity dropdown should include "Chess Club"
    And the activity dropdown should include "Programming Class"

  Scenario: No participants message displayed when empty
    Given the page is displayed in "English"
    And "Art Studio" has 1 participant
    When I delete the last participant from "Art Studio"
    Then "Art Studio" should show "No participants yet" message

  Scenario: Participant list updates after signup
    Given the page is displayed in "English"
    And "Chess Club" has 2 participants
    When I sign up for "Chess Club" with email "newcount@mergington.edu"
    Then "Chess Club" should have 3 participants
    And the participant count should be updated in the UI

  Scenario: Activities displayed in Hungarian
    Given the page is displayed in "Hungarian"
    Then I should see 9 activities in the list
    And I should see activity "Sakk Klub"
    And I should see activity "Programozás Tanfolyam"
    And I should see activity "Tornaterem"
    And I should see activity "Focicsapat"
