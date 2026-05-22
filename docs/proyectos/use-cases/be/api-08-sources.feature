# language: en
Feature: Sources Management Endpoints
  As the frontend application
  I want to list, start, and stop data extraction sources
  So that the user can manage automated job aggregation pipelines

  Background:
    Given the backend application is running on port 8000
    And the MongoDB "unified_jobs" collection has data from multiple sources

  Scenario: List all data sources
    When I send a GET request to "/sources/"
    Then the response status is 200
    And the response body contains "data" as an array
    And each source in "data" has fields:
      | field          | type    |
      | name           | string  |
      | label          | string  |
      | description    | string  |
      | query          | string  |
      | total_records  | number  |
      | last_sync      | string or null |
      | status         | "idle"  |

  Scenario: Sources list contains at least LinkedIn, JSearch, SerpApi
    When I send a GET request to "/sources/"
    Then the "data" array contains an item with name="linkedin"
    And the "data" array contains an item with name="jsearch"
    And the "data" array contains an item with name="serpapi"

  Scenario: Source last_sync reflects the most recent extraction
    Given the newest LinkedIn document has _fetched_at in MongoDB
    When I send a GET request to "/sources/"
    Then the LinkedIn source has last_sync matching the newest _fetched_at for LinkedIn documents

  Scenario: Source last_sync is null when no data exists
    Given no documents exist for a source
    When I send a GET request to "/sources/"
    Then that source has last_sync=null

  Scenario: Source total_records matches MongoDB count
    Given there are N documents with _source="LinkedIn" in MongoDB
    When I send a GET request to "/sources/"
    Then the LinkedIn source has total_records=N

  Scenario: Trigger sync for a source
    When I send a POST request to "/sources/linkedin/sync"
    Then the response status is 200
    And the response body is:
      """
      {"source": "linkedin", "status": "started", "message": "Sync triggered for linkedin"}
      """

  Scenario: Stop sync for a source
    When I send a POST request to "/sources/linkedin/stop"
    Then the response status is 200
    And the response body is:
      """
      {"source": "linkedin", "status": "stopped", "message": "Sync stopped for linkedin"}
      """

  Scenario: Sync and stop work for all known sources
    When I send a POST request to "/sources/jsearch/sync"
    Then the response status is 200
    When I send a POST request to "/sources/jsearch/stop"
    Then the response status is 200
    When I send a POST request to "/sources/serpapi/sync"
    Then the response status is 200
    When I send a POST request to "/sources/serpapi/stop"
    Then the response status is 200

  # --- How to test manually ---
  # curl -s http://localhost:8000/sources/ | python3 -m json.tool
  # curl -s -X POST http://localhost:8000/sources/linkedin/sync
  # curl -s -X POST http://localhost:8000/sources/linkedin/stop
  # Verify total_records: run in mongosh:
  #   db.unified_jobs.countDocuments({_source: "LinkedIn"})
