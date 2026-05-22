# language: en
Feature: Tailored CV and Cover Letter Generation
  As a job seeker
  I want to generate a tailored CV and cover letter for a specific job
  So that I can apply with documents optimized for that role

  Background:
    Given the backend LLM service is configured and running
    And my CV (CV.md) and resume tips are available in the backend resources

  Scenario: Generate tailored CV from job card
    Given a job card is displayed for "Senior Frontend Engineer" at "Velocity AI"
    When I click "Generate CV" on the card
    Then the button shows a loading spinner with "Generating..."
    And the CV button is disabled during generation
    And other buttons on the card remain functional (Cover Letter, Apply Now)
    And a PDF file downloads with name "cv_velocity_ai.pdf"
    And the button returns to "Generate CV" after completion

  Scenario: Generate cover letter from job card
    Given a job card is displayed
    When I click "Cover Letter" on the card
    Then the button shows a loading spinner with "..."
    And a PDF file downloads with name "cover_letter_company_name.pdf"
    And the button returns to "Cover Letter" after completion

  Scenario: Generate tailored CV from job detail modal
    Given the job detail modal is open
    When I click "Generate Tailored CV" in the modal footer
    Then the button shows "Generating..." with a spinner
    And a PDF download starts upon completion

  Scenario: Generate cover letter from job detail modal
    Given the job detail modal is open
    When I click "Generate Cover Letter" in the modal footer
    Then the button shows "Generating..." with a spinner
    And a PDF download starts upon completion

  Scenario: Prevent double generation on CV button
    Given I click "Generate CV" and it is loading
    When I click "Generate CV" again
    Then no second API request is sent
    Because the button is disabled during generation

  Scenario: Separate generation states for CV and cover letter
    When I click "Generate CV" (CV starts loading)
    Then the "Cover Letter" button remains clickable
    And clicking "Cover Letter" starts its own generation independently

  Scenario: Handle CV generation error gracefully
    Given the backend generates a CV error (job not found, LLM failure, etc.)
    When I click "Generate CV"
    Then an error is logged to the console
    And the button returns to its enabled state
    And no PDF download occurs

  # --- How to test manually ---
  # 1. Click "Generate CV" on a card -> verify spinner, disable, PDF download
  # 2. Click "Cover Letter" on a card -> verify spinner, disable, PDF download
  # 3. Open modal -> click "Generate Tailored CV" -> same verification
  # 4. Double-click "Generate CV" -> verify only one request
  # 5. Verify CV and cover letter can be generated simultaneously
  # 6. Test with a non-existent jobId -> verify error handling
