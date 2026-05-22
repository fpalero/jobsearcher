# language: en
Feature: Apply Job Endpoint
  As the frontend application
  I want to mark a job as applied or unapplied
  So that users can track their application status

  Background:
    Given the backend application is running on port 8000
    And the MongoDB "unified_jobs" collection has a document with job_id "test-job-123"

  Scenario: Mark a job as applied
    Given the job "test-job-123" has applied=false
    When I send a POST request to "/jobs/test-job-123/apply" with body:
      """
      {"applied": true}
      """
    Then the response status is 200
    And the response body is:
      """
      {"jobId": "test-job-123", "applied": true}
      """
    And the MongoDB document now has applied=true
    And the MongoDB document has applied_at set to the current UTC timestamp

  Scenario: Mark a job as unapplied
    Given the job "test-job-123" has applied=true and applied_at is set
    When I send a POST request to "/jobs/test-job-123/apply" with body:
      """
      {"applied": false}
      """
    Then the response status is 200
    And the response body is:
      """
      {"jobId": "test-job-123", "applied": false}
      """
    And the MongoDB document now has applied=false
    And the MongoDB document has applied_at=null

  Scenario: Apply to a non-existent job returns 404
    When I send a POST request to "/jobs/nonexistent-id/apply" with body:
      """
      {"applied": true}
      """
    Then the response status is 404
    And the response body contains "Job not found"

  Scenario: Missing applied field returns 422
    When I send a POST request to "/jobs/test-job-123/apply" with body:
      """
      {}
      """
    Then the response status is 422

  Scenario: applied_at is set only when marking as applied
    Given the job "test-job-123" has applied=false and applied_at=null
    When I send a POST to "/jobs/test-job-123/apply" with {"applied": true}
    Then applied_at is a valid UTC datetime
    When I send a POST to "/jobs/test-job-123/apply" with {"applied": false}
    Then applied_at is null

  # --- How to test manually ---
  # curl -s -X POST http://localhost:8000/jobs/test-job-123/apply \
  #   -H "Content-Type: application/json" \
  #   -d '{"applied": true}'
  # curl -s -X POST http://localhost:8000/jobs/test-job-123/apply \
  #   -H "Content-Type: application/json" \
  #   -d '{"applied": false}'
