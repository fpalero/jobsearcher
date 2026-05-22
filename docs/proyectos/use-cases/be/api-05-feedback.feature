# language: en
Feature: Job Feedback Endpoint
  As the frontend application
  I want to submit or remove feedback on a job match
  So that the system can learn from user preferences

  Background:
    Given the backend application is running on port 8000
    And the MongoDB "unified_jobs" collection has a document with job_id "test-job-123"

  Scenario: Submit positive feedback (thumbs up)
    When I send a POST request to "/jobs/test-job-123/feedback" with body:
      """
      {"rating": 1, "reasons": []}
      """
    Then the response status is 200
    And the response body is:
      """
      {"jobId": "test-job-123", "feedback": {"rating": 1, "reasons": []}}
      """
    And the MongoDB document has feedback.rating=1
    And feedback.submitted_at is a valid UTC timestamp
    And feedback.reasons is an empty array

  Scenario: Submit negative feedback (thumbs down)
    When I send a POST request to "/jobs/test-job-123/feedback" with body:
      """
      {"rating": -1, "reasons": ["Irrelevant location"]}
      """
    Then the response status is 200
    And the MongoDB document has feedback.rating=-1
    And feedback.reasons contains "Irrelevant location"

  Scenario: Submit neutral/remove feedback (rating 0)
    Given the job "test-job-123" has a previous feedback
    When I send a POST request to "/jobs/test-job-123/feedback" with body:
      """
      {"rating": 0, "reasons": []}
      """
    Then the response status is 200
    And the MongoDB document has feedback.rating=0
    And feedback.reasons is an empty array

  Scenario: Submit feedback with multiple reasons
    When I send a POST request to "/jobs/test-job-123/feedback" with body:
      """
      {"rating": -1, "reasons": ["Missing required skills", "Salary expectations not met"]}
      """
    Then the response status is 200
    And feedback.reasons contains 2 items

  Scenario: Feedback for non-existent job returns 404
    When I send a POST to "/jobs/nonexistent-id/feedback" with body:
      """
      {"rating": 1, "reasons": []}
      """
    Then the response status is 404
    And the response body contains "Job not found"

  Scenario: Missing rating field returns 422
    When I send a POST request to "/jobs/test-job-123/feedback" with body:
      """
      {"reasons": []}
      """
    Then the response status is 422

  Scenario: Invalid rating type returns 422
    When I send a POST request to "/jobs/test-job-123/feedback" with body:
      """
      {"rating": "good", "reasons": []}
      """
    Then the response status is 422

  # --- How to test manually ---
  # curl -s -X POST http://localhost:8000/jobs/test-job-123/feedback \
  #   -H "Content-Type: application/json" \
  #   -d '{"rating": 1, "reasons": []}'
  # curl -s -X POST http://localhost:8000/jobs/test-job-123/feedback \
  #   -H "Content-Type: application/json" \
  #   -d '{"rating": -1, "reasons": ["Irrelevant location", "Missing skills"]}'
