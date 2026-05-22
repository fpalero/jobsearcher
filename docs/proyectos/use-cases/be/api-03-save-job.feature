# language: en
Feature: Save Job Endpoint
  As the frontend application
  I want to bookmark or unbookmark a job
  So that users can save positions for later review

  Background:
    Given the backend application is running on port 8000
    And the MongoDB "unified_jobs" collection has a document with job_id "test-job-123"

  Scenario: Save a job (bookmark)
    Given the job "test-job-123" has saved=false
    When I send a POST request to "/jobs/test-job-123/save" with body:
      """
      {"saved": true}
      """
    Then the response status is 200
    And the response body is:
      """
      {"jobId": "test-job-123", "saved": true}
      """
    And the MongoDB document now has saved=true

  Scenario: Unsave a job (remove bookmark)
    Given the job "test-job-123" has saved=true
    When I send a POST request to "/jobs/test-job-123/save" with body:
      """
      {"saved": false}
      """
    Then the response status is 200
    And the response body is:
      """
      {"jobId": "test-job-123", "saved": false}
      """
    And the MongoDB document now has saved=false

  Scenario: Save a non-existent job returns 404
    When I send a POST request to "/jobs/nonexistent-id/save" with body:
      """
      {"saved": true}
      """
    Then the response status is 404
    And the response body contains "Job not found"

  Scenario: Missing saved field returns 422
    When I send a POST request to "/jobs/test-job-123/save" with body:
      """
      {}
      """
    Then the response status is 422

  Scenario: Invalid saved type returns 422
    When I send a POST request to "/jobs/test-job-123/save" with body:
      """
      {"saved": "yes"}
      """
    Then the response status is 422

  # --- How to test manually ---
  # curl -s -X POST http://localhost:8000/jobs/test-job-123/save \
  #   -H "Content-Type: application/json" \
  #   -d '{"saved": true}'
  # curl -s -X POST http://localhost:8000/jobs/test-job-123/save \
  #   -H "Content-Type: application/json" \
  #   -d '{"saved": false}'
  # curl -s -X POST http://localhost:8000/jobs/nonexistent/save \
  #   -H "Content-Type: application/json" \
  #   -d '{"saved": true}'  # expect 404
