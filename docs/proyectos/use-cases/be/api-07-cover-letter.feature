# language: en
Feature: Cover Letter PDF Endpoint
  As the frontend application
  I want to generate a cover letter PDF for a specific job
  So that the user can download a tailored cover letter

  Background:
    Given the backend application is running on port 8000
    And the LLM service is configured and operational
    And the MongoDB "unified_jobs" collection has a document with job_id "test-job-123"

  Scenario: Generate cover letter successfully
    When I send a POST request to "/jobs/cover-letter" with body:
      """
      {"job_id": "test-job-123"}
      """
    Then the response status is 200
    And the Content-Type header is "application/pdf"
    And the Content-Disposition header contains 'filename="cover_letter_'
    And the response body is a binary PDF

  Scenario: Cover letter generation failure returns 500
    Given the LLM service is unreachable or returns an error
    When I send a POST request to "/jobs/cover-letter" with body:
      """
      {"job_id": "test-job-123"}
      """
    Then the response status is 500

  Scenario: Missing job_id field returns 422
    When I send a POST request to "/jobs/cover-letter" with body:
      """
      {}
      """
    Then the response status is 422

  Scenario: Cover letter returns a valid PDF
    When I send a POST request to "/jobs/cover-letter" with body:
      """
      {"job_id": "test-job-123"}
      """
    Then the response body starts with "%PDF" (PDF magic bytes)

  # --- How to test manually ---
  # curl -s -o /tmp/cover.pdf -X POST http://localhost:8000/jobs/cover-letter \
  #   -H "Content-Type: application/json" \
  #   -d '{"job_id": "test-job-123"}'
  # file /tmp/cover.pdf  # should output "PDF document"
