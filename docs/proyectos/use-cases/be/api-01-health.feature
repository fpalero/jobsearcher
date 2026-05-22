# language: en
Feature: Health Check Endpoint
  As a DevOps engineer
  I want to check the API health status
  So that I can monitor service availability

  Background:
    Given the backend application is running on port 8000

  Scenario: Health check returns OK
    When I send a GET request to "/health"
    Then the response status is 200
    And the response body is:
      """
      {"status": "ok"}
      """
    And the Content-Type header is "application/json"

  Scenario: Health check responds quickly
    When I send a GET request to "/health"
    Then the response time is less than 500ms

  # --- How to test manually ---
  # curl -s http://localhost:8000/health
  # Expected: {"status":"ok"}
