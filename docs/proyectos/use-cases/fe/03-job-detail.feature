# language: en
Feature: Job Detail Modal
  As a job seeker
  I want to view full job details in a modal
  So that I can understand the role, responsibilities, and requirements before applying

  Background:
    Given I am on the dashboard with job cards displayed

  Scenario: Open job detail modal from a card
    When I click a job card for "Senior Frontend Engineer" at "QuantumFlow Systems"
    Then a modal overlay appears with a 12px blur backdrop
    And the modal shows the company logo
    And the modal shows the job title "Senior Frontend Engineer"
    And the modal shows "QuantumFlow Systems" as the company name
    And the modal shows the posted date, location, and salary

  Scenario: View match percentage in modal
    When the modal is open for a job with 95% match
    Then a circular match ring renders "95%" in the center
    And the label "Top Match" appears below the ring
    And thumb_up and thumb_down feedback buttons are visible next to the match ring

  Scenario: Read the job description
    When the modal is open
    Then an "About the Role" section displays the full job description
    And the description text is wrapped in whitespace-pre-line for proper formatting

  Scenario: View responsibilities list
    Given the job has responsibilities ["Architect React features", "Optimize performance"]
    When the modal is open
    Then a "Responsibilities" section appears
    And each responsibility is prefixed with a check_circle icon in secondary green

  Scenario: View requirements tags
    Given the job has requirements ["React.js", "TypeScript", "Next.js"]
    When the modal is open
    Then a "Requirements" section appears
    And each requirement is rendered as a rounded tag with border

  Scenario: View technology tags
    Given the job has tags ["React", "TypeScript"]
    When the modal is open
    Then a "Tags" section displays each tag as a rounded pill

  Scenario: Show Applied badge on applied jobs
    Given the job has applied=true
    When the modal is open
    Then an "Applied" badge appears next to the job title
    And the badge has a secondary-container background

  Scenario: Generate Tailored CV from modal
    When I click "Generate Tailored CV" in the modal footer
    Then the button shows a loading spinner with "Generating..."
    And a PDF download is triggered upon completion
    And the filename is "cv_company_name.pdf"

  Scenario: Generate Cover Letter from modal
    When I click "Generate Cover Letter" in the modal footer
    Then the button shows a loading spinner with "Generating..."
    And a PDF download is triggered upon completion
    And the filename is "cover_letter_company_name.pdf"

  Scenario: Apply Now from modal
    Given the job has an apply link
    When I click "Apply Now" in the modal footer
    Then the apply link opens in a new browser tab with noopener,noreferrer

  Scenario: Submit positive feedback from modal
    When the modal is open
    And I click the thumb_up button
    Then the thumb_up icon fills to "FILL 1" and turns secondary green
    And a POST /api/jobs/{jobId}/feedback is sent with rating=1

  Scenario: Submit negative feedback from modal
    When the modal is open
    And I click the thumb_down button
    Then the thumb_down icon fills to "FILL 1" and turns red (error)
    And a POST /api/jobs/{jobId}/feedback is sent with rating=-1

  Scenario: Close modal by clicking X
    When the modal is open
    And I click the close button (X) in the top-right corner
    Then the modal closes with a fade-out animation
    And the close button shows error colors on hover

  Scenario: Close modal by clicking backdrop
    When the modal is open
    And I click outside the modal (on the blurred backdrop area)
    Then the modal closes

  # --- How to test manually ---
  # 1. Click any job card -> verify modal opens
  # 2. Verify all sections: About the Role, Responsibilities, Requirements, Tags
  # 3. Verify match ring percentage matches the card
  # 4. Click "Generate Tailored CV" -> verify loading state and PDF download
  # 5. Click "Generate Cover Letter" -> verify loading state and PDF download
  # 6. Click "Apply Now" -> verify new tab opens
  # 7. Click thumb_up -> verify icon fills and API call happens
  # 8. Click X button or backdrop -> verify modal closes
