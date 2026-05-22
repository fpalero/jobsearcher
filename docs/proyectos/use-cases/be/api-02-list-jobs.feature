# language: en
Feature: List Jobs Endpoint
  As the frontend application
  I want to retrieve paginated job listings with optional filters
  So that I can display job cards to the user

  Background:
    Given the backend application is running on port 8000
    And the MongoDB "unified_jobs" collection has test data

  Scenario: Retrieve all jobs with default pagination
    When I send a GET request to "/jobs/?limit=100&skip=0"
    Then the response status is 200
    And the response body contains:
      | field  | type   |
      | data   | array  |
      | total  | number |
      | limit  | 100    |
      | skip   | 0      |
    And each item in "data" has fields: id, jobId, company, title, location, salary, matchPercentage, logoUrl, description, tags, postedDate, applicable, saved, applied, responsibilities, requirements

  Scenario: Respect limit and skip for pagination
    When I send a GET request to "/jobs/?limit=5&skip=0"
    Then the "data" array contains at most 5 items
    And "limit" is 5
    When I send a GET request to "/jobs/?limit=5&skip=5"
    Then the "data" array contains at most 5 items
    And "skip" is 5

  Scenario: Filter by applicable jobs
    When I send a GET request to "/jobs/?applicable=true"
    Then every item in "data" has applicable=true
    And "total" reflects only applicable jobs

  Scenario: Filter by saved jobs
    When I send a GET request to "/jobs/?saved=true"
    Then every item in "data" has saved=true

  Scenario: Filter by applied jobs
    When I send a GET request to "/jobs/?applied=true"
    Then every item in "data" has applied=true

  Scenario: Combine multiple filters
    When I send a GET request to "/jobs/?applicable=true&saved=true"
    Then every item in "data" has applicable=true and saved=true

  Scenario: Invalid limit returns 422
    When I send a GET request to "/jobs/?limit=0"
    Then the response status is 422

    When I send a GET request to "/jobs/?limit=501"
    Then the response status is 422

  Scenario: Negative skip returns 422
    When I send a GET request to "/jobs/?skip=-1"
    Then the response status is 422

  Scenario: Response includes all required fields for each job
    Given jobs exist in the database
    When I send a GET request to "/jobs/"
    Then each job in "data" has:
      | field            | presence    |
      | jobId            | non-empty   |
      | company          | non-empty   |
      | title            | non-empty   |
      | matchPercentage  | 0-100       |
      | tags             | array       |
      | saved            | boolean     |
      | applied          | boolean     |
      | responsibilities | array       |
      | requirements     | array       |

  # --- How to test manually ---
  # curl -s "http://localhost:8000/jobs/?limit=3&skip=0" | python3 -m json.tool
  # curl -s "http://localhost:8000/jobs/?applicable=true" | python3 -m json.tool
  # curl -s "http://localhost:8000/jobs/?saved=true" | python3 -m json.tool
  # curl -s "http://localhost:8000/jobs/?applied=true" | python3 -m json.tool
  # curl -s "http://localhost:8000/jobs/?limit=0"  # expect 422
  # curl -s "http://localhost:8000/jobs/?skip=-1"  # expect 422
