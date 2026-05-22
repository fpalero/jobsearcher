# language: en
Feature: Tailored CV PDF Endpoint
  As the frontend application
  I want to generate a tailored CV PDF for a specific job
  So that the user can download an ATS-optimized resume

  Background:
    Given the backend application is running on port 8000
    And the LLM service is configured and operational
    And the MongoDB "unified_jobs" collection has a document with job_id "test-job-123"
    And CV.md and resume tips exist in backend/resources/

  Scenario: Generate tailored CV successfully
    When I send a POST request to "/jobs/tailored-pdf" with body:
      """
      {"job_id": "test-job-123"}
      """
    Then the response status is 200
    And the Content-Type header is "application/pdf"
    And the Content-Disposition header contains 'filename="cv_' (starts with cv_)
    And the response body is a binary PDF

  Scenario: Job not found returns 404
    When I send a POST request to "/jobs/tailored-pdf" with body:
      """
      {"job_id": "nonexistent-job-999"}
      """
    Then the response status is 404
    And the response body contains "Job not found"

  Scenario: Missing job_id field returns 422
    When I send a POST request to "/jobs/tailored-pdf" with body:
      """
      {}
      """
    Then the response status is 422

  Scenario: Generate tailored CV is idempotent (cached)
    Given a CV was previously generated for "test-job-123"
    When I send a POST request to "/jobs/tailored-pdf" with body:
      """
      {"job_id": "test-job-123"}
      """
    Then the response status is 200
    And the cached PDF is returned without re-running the LLM

  Scenario: CV generation returns a valid PDF
    When I send a POST request to "/jobs/tailored-pdf" with body:
      """
      {"job_id": "test-job-123"}
      """
    Then the response body starts with "%PDF" (PDF magic bytes)

  # --- How to test manually ---
  # curl -s -o /tmp/cv.pdf -X POST http://localhost:8000/jobs/tailored-pdf \
  #   -H "Content-Type: application/json" \
  #   -d '{"job_id": "test-job-123"}'
  # file /tmp/cv.pdf  # should output "PDF document"
  # curl -s -X POST http://localhost:8000/jobs/tailored-pdf \
  #   -H "Content-Type: application/json" \
  #   -d '{"job_id": "nonexistent-999"}'  # expect 404
