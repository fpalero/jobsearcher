# language: en
Feature: Job Filtering via Sidebar
  As a job seeker
  I want to filter jobs by applicable, applied, and saved status
  So that I can focus on relevant opportunities

  Background:
    Given I am on the dashboard page
    And the sidebar is visible (desktop viewport >= 768px)
    And the sidebar shows four navigation items: All Jobs, Applied, Saved, Sources

  Scenario: Filter to show only applicable/remote jobs
    Given jobs exist with both applicable=true and applicable=false
    When I click "Applied" in the sidebar
    Then the API is called with applicable=true
    And the header changes to "Recommended for You"
    And only applicable jobs are displayed
    And the Applied nav item is highlighted with a primary background

  Scenario: Filter to show only saved jobs
    Given I have previously saved at least 1 job
    When I click "Saved" in the sidebar
    Then the API is called with saved=true
    And the header changes to "Saved Jobs"
    And the subtitle reads "Your bookmarked positions"
    And only saved jobs are displayed

  Scenario: Filter to show applied jobs
    Given I have previously applied to at least 1 job
    When I click "Applied" in the sidebar (from the direct filter)
    Then the API is called with applied=true
    And the header changes to "Applied Jobs"
    And only jobs marked as applied are displayed

  Scenario: Return to all jobs
    Given I am currently viewing a filtered list
    When I click "All Jobs" in the sidebar
    Then the API is called without any filter
    And the header changes to "Recommended for You"
    And the subtitle reads "Based on your profile and skills."
    And all jobs are displayed

  Scenario: Sidebar highlights the active filter
    Given I click "Saved" in the sidebar
    Then the "Saved" nav item gets bg-primary-container and text-on-primary-container
    And the "All Jobs" nav item has the default hover style
    When I click "All Jobs"
    Then the "All Jobs" nav item becomes highlighted
    And the "Saved" nav item returns to default style

  Scenario: Navigate to Sources from sidebar
    Given I am on the dashboard
    When I click "Sources" in the sidebar
    Then I am routed to "/sources"
    And the Sources Management page loads

  # --- How to test manually ---
  # 1. Ensure some jobs have applicable=true and some have saved=true (check MongoDB)
  # 2. Click "Applied" -> verify URL and filtered list
  # 3. Click "Saved" -> verify only bookmarked jobs
  # 4. Click "All Jobs" -> verify full list
  # 5. Click "Sources" -> verify navigation to /sources
