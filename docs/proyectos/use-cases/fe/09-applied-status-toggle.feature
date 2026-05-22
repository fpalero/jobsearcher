# language: en
Feature: Job Applied Status Toggle
  As a job seeker
  I want to mark jobs as applied or unmark them
  So that I can track my application progress

  Background:
    Given I am on the dashboard with job cards displayed
    And the backend API is available at port 8000

  Scenario: Mark a job as applied from the card
    Given a job card is displayed with applied=false
    When I click the check_circle icon on the card
    Then the icon fills to "FILL 1" indicating applied=true
    And a POST request is sent to /api/jobs/{jobId}/apply with applied=true
    And an "Applied" badge appears next to the company name on the card
    And the job appears in the "Applied" filtered view

  Scenario: Unmark a job as applied from the card
    Given a job card is displayed with applied=true
    When I click the check_circle icon (filled) on the card
    Then the icon returns to outline "FILL 0"
    And a POST request is sent to /api/jobs/{jobId}/apply with applied=false
    And the "Applied" badge disappears from the card
    And the job no longer appears in the "Applied" filtered view

  Scenario: Click on check_circle does not open job details modal
    Given a job card is displayed
    When I click the check_circle icon
    Then the job detail modal does NOT open
    And only the applied status toggles

  Scenario: Applied status persists across page refresh
    Given a job card has applied=true
    When I refresh the page
    Then the check_circle icon is filled
    And the "Applied" badge is visible
    And the applied status is loaded from the backend

  Scenario: Applied status persists across page refresh (negative case)
    Given a job card has applied=false
    When I refresh the page
    Then the check_circle icon is in outline style
    And no "Applied" badge appears

  Scenario: Toggle applied from job detail modal
    Given a job detail modal is open
    And the job has applied=false
    When I click the check_circle icon in the modal
    Then the icon fills to "FILL 1"
    And an "Applied" badge appears in the modal header
    And the same update is sent to the backend

  Scenario: API error reverts applied toggle
    Given a job card is displayed with applied=false
    When I click the check_circle icon
    But the backend returns an error (e.g., 404 or 500)
    Then the icon remains in outline style
    And the applied status is reverted to false

  # --- How to test manually ---
  # 1. Navigate to dashboard
  # 2. Find a job card, click the check_circle icon -> verify API POST /apply
  # 3. Check MongoDB -> document should have applied=true and applied_at set
  # 4. Refresh page -> icon should remain filled
  # 5. Click check_circle again -> verify unmarking works
  # 6. Open job detail modal -> verify check_circle exists there too