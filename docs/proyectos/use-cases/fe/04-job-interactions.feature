# language: en
Feature: Job Interactions (Save, Apply, Feedback)
  As a job seeker
  I want to bookmark jobs, mark them as applied, and give feedback
  So that I can track my job search progress and improve recommendations

  Background:
    Given I am on the dashboard with job cards displayed

  Scenario: Bookmark a job
    Given a job card is displayed with saved=false
    When I click the bookmark icon in the top-right corner of the card
    Then the bookmark icon fills to "FILL 1" (solid)
    And a POST request is sent to /api/jobs/{jobId}/save with saved=true
    And the job appears in the "Saved" filtered view

  Scenario: Unbookmark a job
    Given a job card is displayed with saved=true
    When I click the bookmark icon in the top-right corner
    Then the bookmark icon returns to "FILL 0" (outline)
    And a POST request is sent to /api/jobs/{jobId}/save with saved=false
    And the job no longer appears in the "Saved" filtered view

  Scenario: Bookmark toggle survives click on the card
    Given a job card is displayed
    When I click the bookmark icon
    Then the job detail modal does NOT open
    And only the bookmark state toggles

  Scenario: Save status persists across page refresh
    Given a job card has saved=true
    When I refresh the page
    Then the bookmark icon is filled
    And the job appears in the "Saved" filtered view

  Scenario: Give positive feedback (thumbs up)
    Given a job card is displayed
    When I click the thumb_up button on the card
    Then the thumb_up icon fills to "FILL 1" and turns secondary green
    And a POST /api/jobs/{jobId}/feedback is sent with rating=1

  Scenario: Give negative feedback (thumbs down)
    Given a job card is displayed
    When I click the thumb_down button on the card
    Then the thumb_down icon fills to "FILL 1" and turns error red
    And a POST /api/jobs/{jobId}/feedback is sent with rating=-1

  Scenario: Toggle feedback off
    Given positive feedback was submitted for a job (thumb_up filled)
    When I click the thumb_up button again
    Then the icon returns to outline style
    And a POST /api/jobs/{jobId}/feedback is sent with rating=0

  Scenario: View Applied badge on a job card
    Given a job has applied=true
    When the job card renders
    Then an "Applied" badge appears next to the company name
    And the badge uses secondary-container background with on-secondary-container text

  Scenario: No Applied badge when job is not applied
    Given a job has applied=false or undefined
    When the job card renders
    Then no "Applied" badge appears

  Scenario: Mark job as applied from card
    Given a job card is displayed with applied=false
    When I click the check_circle icon on the card
    Then the icon fills to "FILL 1"
    And a POST request is sent to /api/jobs/{jobId}/apply with applied=true
    And an "Applied" badge appears next to the company name

  Scenario: Applied status persists across page refresh
    Given a job card has applied=true
    When I refresh the page
    Then the check_circle icon is filled
    And the "Applied" badge is visible
    And the applied status is loaded from the backend

  # --- How to test manually ---
  # 1. Click bookmark on a card -> icon fills, verify API POST /save
  # 2. Navigate to "Saved" in sidebar -> job appears
  # 3. Unbookmark -> icon returns to outline
  # 4. Click thumb_up -> icon fills green
  # 5. Click thumb_down -> icon fills red
  # 6. Click check_circle -> icon fills, badge appears
  # 7. Refresh page -> verify all states persist
  # 8. Check MongoDB -> applied=true documents should show badge
