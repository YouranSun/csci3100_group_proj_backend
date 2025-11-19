import unittest
from router import router_request

class TestRouterRequest(unittest.TestCase):
    def test_add_repo_request(self):
        req = router_request.AddRepoRequest(repo_path="repo", name="repo1")
        self.assertEqual(req.repo_path, "repo")
        self.assertEqual(req.name, "repo1")

    def test_commit_group_request(self):
        req = router_request.CommitGroupRequest(repo_path="repo", name="group")
        self.assertEqual(req.repo_path, "repo")
        self.assertEqual(req.name, "group")

    def test_delete_group_request(self):
        req = router_request.DeleteGroupRequest(repo_path="repo", group_id="gid")
        self.assertEqual(req.group_id, "gid")

    def test_move_diff_request(self):
        req = router_request.MoveDiffRequest(repo_path="repo", diff_id="d1", target_group_id="g2")
        self.assertEqual(req.diff_id, "d1")
        self.assertEqual(req.target_group_id, "g2")

    def test_reorder_groups_request(self):
        req = router_request.ReorderGroupsRequest(repo_path="repo", ordered_ids=["g1", "g2"])
        self.assertEqual(req.ordered_ids, ["g1", "g2"])

    def test_future_suggestions_request(self):
        req = router_request.FutureSuggestionsRequest(repo_path="repo", requirements="Improve", max_commits=10)
        self.assertEqual(req.requirements, "Improve")
        self.assertEqual(req.max_commits, 10)

    def test_user_register_request(self):
        req = router_request.UserRegisterRequest(username="u", password="p")
        self.assertEqual(req.username, "u")
        self.assertEqual(req.password, "p")

    def test_user_response(self):
        resp = router_request.UserResponse(id=1, username="u")
        self.assertEqual(resp.id, 1)
        self.assertEqual(resp.username, "u")

if __name__ == "__main__":
    unittest.main()
