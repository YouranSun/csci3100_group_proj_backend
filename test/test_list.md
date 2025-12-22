# Test Case List for CodeAnalyzer

This document lists all required unit and integration test cases based on the requirements and current project structure.

## 0. User System

## 1. Repository Summarization
- [x] Unit: Test repo hash calculation and cache logic  <!-- test/RepositorySummarization/test_repo_hash.py -->
- [x] Unit: Test directory and file traversal
- [x] Unit: Test summary generation for files/directories (mock LLM)  <!-- test/RepositorySummarization/test_summary.py -->
- [x] Integration: End-to-end summary generation for test/example repo

## 2. Future Suggestions Generation
- [x] Unit: Test loading and validating repo summary from DB  <!-- test/FutureSuggestionsGeneration/test_load_summary.py -->
- [x] Unit: Test suggestion generation logic (mock LLM)  <!-- test/FutureSuggestionsGeneration/test_suggestion_logic.py -->
- [x] Integration: Generate suggestions with/without user requirements  <!-- test/FutureSuggestionsGeneration/test_integration_suggestion.py -->

## 3. Commit Splitting and Grouping
- [x] Unit: Test diff extraction from working tree  <!-- test/CommitSplittingAndGrouping/test_diff_extraction.py -->
- [x] Unit: Test diff block segmentation and clustering (mock LLM)  <!-- test/CommitSplittingAndGrouping/test_diff_segmentation.py -->
- [x] Integration: Split and group commits in test/example repo  <!-- test/CommitSplittingAndGrouping/test_integration_split_group.py -->

## 4. Commit Message Generator
- [x] Unit: Test commit group retrieval  <!-- test/CommitMessageGenerator/test_commit_group_retrieval.py -->
- [x] Unit: Test commit message generation (mock LLM)  <!-- test/CommitMessageGenerator/test_commit_message_generation.py -->
- [x] Integration: Generate commit messages for grouped changes  <!-- test/CommitMessageGenerator/test_integration_commit_messages.py -->

## 5. Commit Executor
- [x] Unit: Test applying grouped changes to filesystem (mock)  <!-- test/CommitExecutor/test_apply_grouped_changes.py -->
- [x] Integration: Execute grouped commits in test/example repo  <!-- test/CommitExecutor/test_integration_execute_commits.py -->

## 6. Commit Category Tagging
- [x] Unit: Test commit log loading and tag assignment  <!-- test/CommitCategoryTagging/test_commit_log_tagging.py -->
- [x] Integration: Tag commits in test/example repo  <!-- test/CommitCategoryTagging/test_integration_tag_commits.py -->

## 7. Error Handling & Edge Cases
- [x] Unit: Test repo unreadable, DB errors, LLM failures (mock)  <!-- test/ErrorHandling/test_error_cases.py -->
- [x] Integration: Simulate and handle failures in workflows  <!-- test/ErrorHandling/test_integration_error_handling.py -->

# API Testing

## 1. Router API Unit Tests

### user_router.py
- [x] POST /register: user registration  <!-- test/APIRouter/test_user_router.py -->
- [x] POST /login: user login  <!-- test/APIRouter/test_user_router.py -->
- [x] POST /logout: user logout  <!-- test/APIRouter/test_user_router.py -->
- [x] GET /me: get current user info  <!-- test/APIRouter/test_user_router.py -->

### summary_router.py
- [x] POST /summary: get repo summary  <!-- test/APIRouter/test_summary_router.py -->
- [x] POST /summary/refresh: refresh repo summary  <!-- test/APIRouter/test_summary_router.py -->

### repo_router.py
- [x] GET /repos: list repositories  <!-- test/APIRouter/test_repo_router.py -->
- [x] POST /repos: add repository  <!-- test/APIRouter/test_repo_router.py -->

### insights_router.py
- [x] POST /insights: generate future suggestions  <!-- test/APIRouter/test_insights_router.py -->

### commit_message_router.py
- [x] POST /commit_message/generate: generate group commit message  <!-- test/APIRouter/test_commit_message_router.py -->
- [x] POST /commit_message: get commit message  <!-- test/APIRouter/test_commit_message_router.py -->
- [x] POST /commit_message/edit: edit commit message  <!-- test/APIRouter/test_commit_message_router.py -->

### commits_router.py
- [x] POST /commit_groups: get commit groups  <!-- test/APIRouter/test_commits_router.py -->
- [x] POST /commit_groups/move_diff: move diff between groups  <!-- test/APIRouter/test_commits_router.py -->
- [x] POST /commit_groups: create commit group  <!-- test/APIRouter/test_commits_router.py -->
- [x] DELETE /commit_groups/delete: delete commit group  <!-- test/APIRouter/test_commits_router.py -->
- [x] POST /commit_groups/reorder: reorder commit groups  <!-- test/APIRouter/test_commits_router.py -->
- [x] POST /atomic_diffs: get atomic diffs  <!-- test/APIRouter/test_commits_router.py -->
- [x] POST /commit_groups/apply: apply commit groups  <!-- test/APIRouter/test_commits_router.py -->

## 2. API Integrated Tests

- [x] Integration: user authentication workflow (register, login, logout, get user)  <!-- test/APIRouter/test_api_integration.py -->
- [x] Integration: repo summary workflow (summary, refresh, get)  <!-- test/APIRouter/test_api_integration.py -->
- [x] Integration: commit split/group/apply workflow (commit_groups, move_diff, reorder, apply)  <!-- test/APIRouter/test_api_integration.py -->
- [x] Integration: commit message workflow (generate, edit, get)  <!-- test/APIRouter/test_api_integration.py -->
- [x] Integration: future suggestion workflow (insights)  <!-- test/APIRouter/test_api_integration.py -->
- [x] Integration: repository management workflow (list/add repo)  <!-- test/APIRouter/test_api_integration.py -->


**Note:**  
- All LLM-related tests must use mocks, not real API calls.
- All integration tests use the test/example repo.
- All test files should be placed in the `test` directory.
- All comments must be in English.
