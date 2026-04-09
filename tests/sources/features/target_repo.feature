Feature: TargetRepoManager — multi-repo aware clone and worktree manager
  TargetRepoManager reads engagement config, resolves repo paths, enforces
  per-role access control, and creates git worktrees for isolated agent writes.
  Git worktrees are non-negotiable for DE and DO (concurrent safe writes).

  # ---------------------------------------------------------------------------
  # Config parsing
  # ---------------------------------------------------------------------------

  Scenario: Multi-repo config is parsed correctly
    Given a multi-repo engagement config with repos "api" (primary), "frontend", "worker"
    When TargetRepoManager is initialised
    Then get_repo_ids() returns ["api", "frontend", "worker"]
    And get_primary_id() returns "api"

  Scenario: Backward-compatible single-repo config maps to id "default"
    Given a single-repo engagement config
    When TargetRepoManager is initialised
    Then get_repo_ids() returns ["default"]
    And get_primary_id() returns "default"

  Scenario: Empty config has no repos and no primary
    Given an empty engagement config
    When TargetRepoManager is initialised
    Then get_repo_ids() returns []
    And get_primary_id() returns None

  # ---------------------------------------------------------------------------
  # Path resolution
  # ---------------------------------------------------------------------------

  Scenario: Clone path is correctly resolved for a named repo
    Given a multi-repo engagement config with repos "api" (primary), "frontend", "worker"
    When TargetRepoManager is initialised
    Then get_clone_path("api") returns the path engagements/<id>/target-repos/api

  Scenario: None repo_id resolves to the primary repo path
    Given a multi-repo engagement config with repos "api" (primary), "frontend", "worker"
    When TargetRepoManager is initialised
    Then get_clone_path(None) returns the path engagements/<id>/target-repos/api

  Scenario: Unknown repo_id raises TargetRepoNotFoundError
    Given a multi-repo engagement config with repos "api" (primary), "frontend", "worker"
    When TargetRepoManager is initialised
    Then get_clone_path("nonexistent") raises TargetRepoNotFoundError

  # ---------------------------------------------------------------------------
  # Access control
  # ---------------------------------------------------------------------------

  Scenario: DE agent gets read-write access to any registered repo
    Given a multi-repo engagement config with repos "api" (primary), "frontend", "worker"
    When TargetRepoManager is initialised
    Then check_access("api", "DE") returns "read-write"

  Scenario: DO agent gets read-write access to any registered repo
    Given a multi-repo engagement config with repos "api" (primary), "frontend", "worker"
    When TargetRepoManager is initialised
    Then check_access("frontend", "DO") returns "read-write"

  Scenario: SA agent gets read-only access to any registered repo
    Given a multi-repo engagement config with repos "api" (primary), "frontend", "worker"
    When TargetRepoManager is initialised
    Then check_access("api", "SA") returns "read-only"

  Scenario: Unknown repo returns no access for any role
    Given a multi-repo engagement config with repos "api" (primary), "frontend", "worker"
    When TargetRepoManager is initialised
    Then check_access("nonexistent", "DE") returns "none"

  # ---------------------------------------------------------------------------
  # Git worktree creation (neuralgic — must be isolated per agent+sprint)
  # ---------------------------------------------------------------------------

  Scenario: create_worktree creates an isolated git worktree for DE
    Given a real git repository cloned as "api"
    When create_worktree("api", "feature/de-sprint-1") is called
    Then a worktree directory exists at the expected path
    And the worktree is on branch "feature/de-sprint-1"
    And the worktree path is separate from the main clone path

  Scenario: Two worktrees for different agents do not share a directory
    Given a real git repository cloned as "api"
    When create_worktree("api", "feature/de-sprint-1") is called
    And create_worktree("api", "feature/do-sprint-1") is called
    Then the two worktree paths are different directories
