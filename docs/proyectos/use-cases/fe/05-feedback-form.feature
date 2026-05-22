# language: en
Feature: Batch Feedback Form
  As a job seeker
  I want to explain why the current job recommendations are not good matches
  So that the system can improve future recommendations

  Background:
    Given I am on the dashboard with recommended jobs displayed
    And the current filter is "Applicable" (applicable=true mode)

  Scenario: Show feedback prompt after viewing recommendations
    Given applicable jobs are displayed
    When I scroll to the bottom of the job list
    Then I see a card with a lightbulb icon asking "How can we improve?"
    And the subtitle reads "Tell us why these jobs weren't a good match..."
    And a "Give Feedback" link is visible

  Scenario: Open the feedback form
    When I click "Give Feedback"
    Then the prompt card is replaced by the feedback form "What went wrong?"
    And three checkbox options are shown:
      | Missing required skills    |
      | Irrelevant location        |
      | Salary expectations not met |

  Scenario: Fill and submit feedback
    When I check "Missing required skills" and "Irrelevant location"
    Then the checked items gain a primary border and background
    And I click "Submit Feedback"
    Then the form closes
    And the selected reasons are stored locally

  Scenario: Cancel feedback form
    When I click "Give Feedback" to open the form
    And I check a reason
    And I click "Cancel"
    Then the form closes
    And the prompt card returns to its initial "How can we improve?" state

  Scenario: Feedback form not shown in saved or applied views
    Given I am viewing "Saved Jobs" or "Applied Jobs"
    Then the "How can we improve?" card does NOT appear
    Because feedback is only relevant to the recommendation engine

  # --- How to test manually ---
  # 1. Select "Applicable" filter from sidebar
  # 2. Scroll to bottom of job list -> verify prompt card
  # 3. Click "Give Feedback" -> verify form with 3 checkboxes
  # 4. Check reasons -> verify visual highlight
  # 5. Click "Submit Feedback" -> verify form closes
  # 6. Switch to "Saved" -> verify prompt card does NOT appear
