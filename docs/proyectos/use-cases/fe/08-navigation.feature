# language: en
Feature: Application Navigation
  As a user
  I want to navigate between dashboard, sources, and different filters
  So that I can access all features of TalentMatch

  Background:
    Given the application is loaded

  Scenario: Navbar shows branding and links
    When the application loads
    Then the navbar is sticky at the top
    And "TalentMatch" is displayed in primary bold text
    And three nav links are visible: Dashboard, Matches, Applications
    And Dashboard is highlighted with a primary bottom border
    And notification and settings icons are in the top-right

  Scenario: Navigate to Dashboard from navbar
    Given I am on any page
    When I click "Dashboard" in the navbar
    Then I am routed to "/dashboard"
    And the Dashboard nav link has a primary border

  Scenario: Navigate to applicable matches from navbar
    When I click "Matches" in the navbar
    Then I am routed to "/dashboard?mode=applicable"
    And applicable/filtered jobs are displayed
    And the "Applied" sidebar item is highlighted

  Scenario: Sidebar always visible on desktop
    Given the viewport is >= 768px wide
    When the application loads
    Then the sidebar is fixed on the left side
    And the sidebar is 280px wide
    And has a surface-container-low background
    And sits at z-40 behind the navbar

  Scenario: Sidebar hidden on mobile
    Given the viewport is < 768px wide
    When the application loads
    Then the sidebar is hidden (display: none / md:flex)
    And the main content takes full width

  Scenario: Navbar has scroll-based shadow
    Given the page content is scrollable
    When I scroll down more than 20px
    Then the navbar gains a shadow-md class
    And the navbar gets a semi-transparent backdrop-blur background

  Scenario: Navbar is flat at the top of the page
    Given I am at the very top of the page (scrollY = 0)
    Then the navbar has a shadow-sm class
    And the background is solid #f8f9ff

  # --- How to test manually ---
  # 1. Verify navbar is sticky when scrolling
  # 2. Click "Dashboard" -> verify route
  # 3. Click "Matches" -> verify applicable filter
  # 4. Resize to mobile (<768px) -> verify sidebar hidden
  # 5. Resize to desktop -> verify sidebar visible
  # 6. Scroll down -> verify shadow appears
