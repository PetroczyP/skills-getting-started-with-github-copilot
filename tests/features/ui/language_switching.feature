Feature: Language Switching
  As a student
  I want to switch between English and Hungarian
  So that I can use the application in my preferred language

  Background:
    Given I am on the activities page
    And the page has loaded completely

  Scenario: Toggle between English and Hungarian
    Given the page is displayed in "English"
    When I click the Hungarian flag button
    Then the page should be displayed in "Hungarian"
    And the page title should be "Tanórán Kívüli Tevékenységek"
    And the signup title should be "Jelentkezés Tevékenységre"
    When I click the English flag button
    Then the page should be displayed in "English"
    And the page title should be "Extracurricular Activities"
    And the signup title should be "Sign Up for an Activity"

  Scenario: Language preference persists in localStorage
    Given the page is displayed in "English"
    When I click the Hungarian flag button
    Then the language preference should be "hu" in localStorage
    When I reload the page
    Then the page should be displayed in "Hungarian"
    And the language preference should be "hu" in localStorage

  Scenario: Activity names update when switching language
    Given the page is displayed in "English"
    And I can see "Chess Club" in the activities list
    When I click the Hungarian flag button
    Then I can see "Sakk Klub" in the activities list
    And I cannot see "Chess Club" in the activities list
    When I click the English flag button
    Then I can see "Chess Club" in the activities list
    And I cannot see "Sakk Klub" in the activities list

  Scenario: Participant emails remain the same across languages
    Given the page is displayed in "English"
    And "Chess Club" has participant "michael@mergington.edu"
    When I click the Hungarian flag button
    Then "Sakk Klub" has participant "michael@mergington.edu"

  Scenario: Signup in one language appears in the other
    Given the page is displayed in "Hungarian"
    When I sign up for "Sakk Klub" with email "bilingual@mergington.edu"
    Then I should see a success message
    And "Sakk Klub" should have participant "bilingual@mergington.edu"
    When I click the English flag button
    Then "Chess Club" should have participant "bilingual@mergington.edu"

  Scenario: Delete in one language removes from the other
    Given the page is displayed in "English"
    And I sign up for "Chess Club" with email "delete_test@mergington.edu"
    And "Chess Club" has participant "delete_test@mergington.edu"
    When I click the Hungarian flag button
    And I delete participant "delete_test@mergington.edu" from "Sakk Klub" and confirm
    Then "Sakk Klub" should not have participant "delete_test@mergington.edu"
    When I click the English flag button
    Then "Chess Club" should not have participant "delete_test@mergington.edu"
