Feature: chronos-python can interact with chronos

  Scenario: Trivial chronos interaction
    Given a working chronos instance
    When we create a trivial chronos job named "myjob"
    Then we should be able to see the job named "myjob" when we list jobs

  Scenario: Handling spaces in job names
    Given a working chronos instance
     When we create a trivial chronos job named "job with spaces"
     Then we should be able to see the job named "job with spaces" when we list jobs
      And we should be able to delete the job named "job with spaces"
      And we should not be able to see the job named "job with spaces" when we list jobs

  Scenario: Gathering job stats for job
    Given  a working chronos instance
    When we create a trivial chronos job named "myjob"
    Then we should be able to see timings for the job named "myjob" when we look at scheduler stats
    And we should be able to see percentiles for all jobs
    And we should be able to see the median timing for all jobs
    And we should be able to see the mean timing for all jobs
