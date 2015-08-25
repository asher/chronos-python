Feature: chronos-python can interact with chronos

  Scenario: Trivial chronos interaction
    Given a working chronos instance
    When we create a trivial chronos job
    Then we should be able to see it when we list jobs

  Scenario: Handling spaces in job names
    Given a working chronos instance
     When we create a chronos job with spaces
     Then we should be able to see the job with spaces when we list jobs
      And we should be able to delete it
      And we should not be able to see it when we list jobs
