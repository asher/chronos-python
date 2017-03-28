Feature: chronos-python can interact with chronos

  @all
  Scenario: Trivial chronos interaction
    Given a working chronos instance
    When we create a trivial chronos job named "myjob"
    Then we should be able to see the job named "myjob" when we list jobs

  @3.0.2
  Scenario: Handling spaces in job names
    Given a working chronos instance
     When we create a trivial chronos job named "job with spaces"
     Then we should not see the job named "job with spaces" when we list jobs

  @2.4.0
  Scenario: Handling spaces in job names
    Given a working chronos instance
    When we create a trivial chronos job named "job with spaces"
    Then we should be able to see the job named "job with spaces" when we list jobs

  @all
  Scenario: Gathering job stats for job
    Given a working chronos instance
     When we create a trivial chronos job named "myjob"
     Then we should be able to see timings for the job named "myjob" when we look at scheduler stats
      And we should be able to see percentiles for all jobs
      And we should be able to see the median timing for all jobs
      And we should be able to see the mean timing for all jobs

  @all
  Scenario: Gathering scheduler graph
    Given a working chronos instance
     When we create a trivial chronos job named "myjob"
      And we create a trivial chronos job named "myotherjob"
     Then we should be able to see 2 jobs in the job graph

  @all
  Scenario: Getting metrics
    Given a working chronos instance
     Then we should be able to see metrics
