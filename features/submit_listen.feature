Feature: Submit a listen to morning_cd
  Scenario: I submit a valid song to morning.cd during the day
    Given my name is "Zach"
    And I live in new york
    And it's daytime at 10:30am on November 12th 2018
    And the first song I listened to today was 'Whispers' by DAP The Contract
    And I write the note "DAP is my friend from college!"
    When I submit my listen to morning.cd
    Then a request is sent to the listens service to add my listen
    And I get a response with my listen from morning.cd

  Scenario: I submit a valid song to morning.cd during the night
    Given my name is "Zach"
    And I live in new york
    And it's nighttime at 6pm on November 12th 2018
    And the first song I listened to today was 'Whispers' by DAP The Contract
    And I write the note "DAP is my friend from college!"
    When I submit my listen to morning.cd
    Then a request is sent to the listens service to add my listen
    And I get an error response that says "Listens can only be submitted during the day"
