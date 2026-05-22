# language: en
Feature: Feedback Persistence
  As a job seeker
  I want my job feedback (thumbs up/down) to persist across page refreshes
  So that my preferences are remembered and recommendations improve

  Background:
    Given I am on the dashboard with job cards displayed
    And the backend API is available at port 8000
    And the MongoDB "unified_jobs" collection has the necessary documents

  Scenario: Positive feedback persists after page refresh
    Given a job card is displayed with no feedback
    When I click the thumb_up button
    Then the thumb_up icon fills and turns secondary green
    And a POST /api/jobs/{jobId}/feedback is sent with rating=1
    When I refresh the page
    Then the thumb_up icon is still filled and green
    And the job's feedback state is loaded from the backend

  Scenario: Negative feedback persists after page refresh
    Given a job card is displayed with no feedback
    When I click the thumb_down button
    Then the thumb_down icon fills and turns error red
    And a POST /api/jobs/{jobId}/feedback is sent with rating=-1
    When I refresh the page
    Then the thumb_down icon is still filled and red
    And the job's feedback state is loaded from the backend

  Scenario: Toggling feedback off persists
    Given a job card has positive feedback (thumb_up filled)
    When I click the thumb_up button again
    Then the icon returns to outline style
    And a POST /api/jobs/{jobId}/feedback is sent with rating=0
    When I refresh the page
    Then the thumb_up icon is in outline style (no feedback)
    And the backend has feedback.rating=0 or no feedback field

  Scenario: Switching from positive to negative feedback persists
    Given a job card has positive feedback (thumb_up filled)
    When I click the thumb_down button
    Then the thumb_up icon returns to outline
    And the thumb_down icon fills and turns error red
    And a POST /api/jobs/{jobId}/feedback is sent with rating=-1
    When I refresh the page
    Then the thumb_down icon is still filled and red
    And thumb_up is in outline style

  Scenario: Feedback persists in job detail modal
    Given a job card has no feedback
    And the job card is in the "Applicable" filter view
    When I click the job card to open the detail modal
    And I click thumb_up in the modal
    Then the thumb_up icon fills in the modal
    When I close the modal
    And I click the same job card again to open the modal
    Then the thumb_up icon is still filled in the modal
    When I refresh the page
    And I open the job detail modal again
    Then the thumb_up icon is still filled

  Scenario: Multiple jobs with different feedback states persist
    Given I have three jobs with different feedback states:
      | Job 1 | positive (thumb_up filled) |
      | Job 2 | negative (thumb_down filled) |
      | Job 3 | no feedback |
    When I refresh the page
    Then Job 1 has thumb_up filled
    And Job 2 has thumb_down filled
    And Job 3 has no feedback icons filled

  # --- How to test manually ---
  # 1. Navigate to dashboard
  # 2. Click thumb_up on a card -> verify POST /feedback with rating=1
  # 3. Check MongoDB -> document should have feedback.rating=1
  # 4. Refresh page -> icon should remain filled
  # 5. Repeat for thumb_down with rating=-1
  # 6. Toggle feedback off -> icon returns to outline
  # 7. Refresh -> icon stays in outline