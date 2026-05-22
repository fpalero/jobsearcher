# language: en
Feature: API Error Handling
  As the frontend application
  I want consistent error responses from the API
  So that I can handle errors gracefully in the UI

  Background:
    Given the backend application is running on port 8000

  Scenario: Unknown route returns 404
    When I send a GET request to "/nonexistent-route"
    Then the response status is 404
    And the response body contains a "detail" field

  Scenario: Wrong HTTP method returns 405
    When I send a DELETE request to "/jobs/"
    Then the response status is 405

  Scenario: Invalid JSON body returns 422
    When I send a POST request to "/jobs/test-id/save" with body:
      """
      not valid json
      """
    And Content-Type is "application/json"
    Then the response status is 422

  Scenario: Missing Content-Type on POST returns 422
    When I send a POST request to "/jobs/test-id/save" with body "{}"
    And the Content-Type header is missing
    Then the response status is 422

  Scenario: CORS headers are present
    When I send an OPTIONS request to "/jobs/"
    Then the response status is 200 or 405
    And the response includes appropriate CORS headers

  Scenario: All error responses return JSON
    When I send a request that causes a 404
    Then the Content-Type header is "application/json"

    When I send a request that causes a 422
    Then the Content-Type header is "application/json"

    When I send a request that causes a 500
    Then the Content-Type header is "application/json"

  # --- How to test manually ---
  # curl -s http://localhost:8000/nonexistent | python3 -m json.tool  # expect 404
  # curl -s -X DELETE http://localhost:8000/jobs/                     # expect 405
  # curl -s -X POST http://localhost:8000/jobs/id/save -d "bad json"  # expect 422
