# language: en
Feature: Data Sources Management
  As a recruiter or admin
  I want to manage automated job aggregation channels
  So that I can control data extraction from LinkedIn, JSearch, SerpApi, and other sources

  Background:
    Given I am logged in
    And I navigate to "/sources" via the sidebar

  Scenario: View all data sources
    When the Sources page loads
    Then the header reads "Data Sources"
    And a subtitle reads "Manage your automated job aggregation channels and sync frequencies."
    And a count badge shows "N Active Pipelines"
    And each source is displayed as a card with:
      | Source label   |
      | Description    |
      | Icon           |
      | Total Records  |
      | Last sync time |
      | More menu      |
    And an "Add New Data Source" dashed card is displayed at the end

  Scenario: View source details for LinkedIn
    Given LinkedIn data exists in MongoDB
    When the Sources page loads
    Then the LinkedIn card shows:
      | Label: "LinkedIn"                          |
      | Description: "Global Talent Network"       |
      | Total Records matching {_source: LinkedIn} |
      | Last sync: formatted date/time             |

  Scenario: Source card shows Start Sync button when idle
    Given a source has status "idle"
    Then the card displays a "Start Sync" button with a sync icon
    And the button has primary background with white text

  Scenario: Trigger extraction confirmation
    When I click "Start Sync" on the LinkedIn card
    Then a confirmation modal appears with:
      | Title: "Confirm Extraction"                                        |
      | Message: "You are about to initiate a full data extraction..."     |
      | Cancel button                                                      |
      | Confirm button                                                     |
    And the backdrop is blurred

  Scenario: Confirm extraction
    Given the confirmation modal is open
    When I click "Confirm"
    Then the modal closes
    And the source card status changes to "syncing"
    And a progress bar appears showing "Extracting data... 0%"
    And the "Start Sync" button is replaced by "Stop Extraction"

  Scenario: Stop an active extraction
    Given a source is currently syncing
    When I click the "Stop Extraction" button
    Then the card returns to idle status
    And the progress bar disappears
    And a POST /api/sources/{sourceName}/stop is sent

  Scenario: Cancel extraction confirmation
    Given the confirmation modal is open
    When I click "Cancel"
    Then the modal closes
    And the source remains in idle state

  Scenario: Close confirmation modal by clicking backdrop
    Given the confirmation modal is open
    When I click the blurred backdrop outside the modal
    Then the modal closes

  Scenario: New Extraction header button
    When I am on the Sources page
    Then a "New Extraction" button appears in the header
    With a play_circle icon

  # --- How to test manually ---
  # 1. Navigate to /sources from sidebar
  # 2. Verify 3 sources appear (LinkedIn, JSearch, SerpApi)
  # 3. Verify record counts match MongoDB
  # 4. Click "Start Sync" on LinkedIn -> verify confirmation modal
  # 5. Click "Confirm" -> verify syncing state with progress bar
  # 6. Click "Stop Extraction" -> verify idle state
  # 7. Click "Cancel" in modal -> verify it closes without action
  # 8. Click backdrop -> verify modal closes
