# language: en
Feature: Job Feed Dashboard
  As a job seeker
  I want to browse recommended job offers on a dashboard
  So that I can find positions matching my profile

  Background:
    Given the backend is running on port 8000
    And the MongoDB "unified_jobs" collection has job documents with match and applicable fields

  Scenario: Load all recommended jobs
    Given at least 1 job exists in the database
    When I navigate to "/dashboard"
    Then I see a list of job cards
    And each card displays company name, job title, location, and salary
    And each card shows a match percentage ring
    And each card shows tech stack tags
    And the header reads "Recommended for You"

  Scenario: Empty job feed with no results
    Given no jobs exist in the database
    When I navigate to "/dashboard"
    Then I see the message "No job offers found. Start by fetching some data."

  Scenario: Job feed shows loading state
    Given the API response takes more than 500ms
    When I navigate to "/dashboard"
    Then I see "Loading jobs..." while data is being fetched
    And job cards appear after the response completes

  Scenario: Click a job card to view details
    Given at least 1 job is displayed
    When I click on a job card
    Then a modal overlay opens
    And the modal shows the full job title, company, description, and match ring

  Scenario: API unavailable falls back to mock data
    Given the backend API is unreachable
    When I navigate to "/dashboard"
    Then I see mock job cards with sample data
    And each mock card has a company logo, title, and match percentage

  Scenario: Close the job detail modal
    Given the job detail modal is open
    When I click the close button (X icon)
    Then the modal closes
    And I see the dashboard job feed again

  Scenario: Check Material Symbols icons on cards
    Given job cards are displayed
    Then each card shows a "location_on" icon next to the location
    And each card shows a "payments" icon next to the salary

  # --- How to test manually ---
  # 1. Start backend: `cd backend && uv run uvicorn application.api.main:app --port 8000`
  # 2. Start frontend: `cd frontend && npm start`
  # 3. Open http://localhost:4200/dashboard
  # 4. Verify job cards render with company, title, location, salary, match ring, tags
  # 5. Click a card -> verify modal opens with full details
  # 6. Stop backend -> reload page -> verify mock data fallback
