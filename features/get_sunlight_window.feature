Feature: Request a sunlight window
  Scenario: I request a sunlight window for today
    Given I live in new york
    And today's date is November 12th, 2018
    And sunrise is at "2018-11-12T11:40:04" utc
    And sunset is at "2018-11-12T21:40:26" utc
    When I request today's sunlight window
    Then I get a sunlight window with the values
      | sunrise_utc         | sunset_utc          |
      | 2018-11-12T11:40:04 | 2018-11-12T21:40:26 |
