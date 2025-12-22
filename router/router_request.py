from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class RepoRequest(BaseModel):
    repo_path: str


#-------------------#
# Repo list Request #
#-------------------#

class AddRepoRequest(RepoRequest):
    pass

#-----------------#
# Summary Request #
#-----------------#

class GetSummaryRequest(RepoRequest):
    pass

class RefreshSummaryRequest(RepoRequest):
    pass

#-----------------#
# Commits Request #
#-----------------#

class CommitGroupRequest(RepoRequest):
    name: str

class DeleteGroupRequest(RepoRequest):
    group_id: str

class MoveDiffRequest(RepoRequest):
    diff_id: str
    target_group_id: str

class ReorderGroupsRequest(RepoRequest):
    ordered_ids: List[str]

class ApplyCommitGroupsRequest(RepoRequest):
    pass

class GetCommitGroupsRequest(RepoRequest):
    pass

class GetAtomicDiffsRequest(RepoRequest):
    pass


#-----------------#
# Insight Request #
#-----------------#

class FutureSuggestionsRequest(RepoRequest):
    requirements: str = ""
    max_commits: int = 50

#------------------------#
# Commit Message Request #
#------------------------#

class CommitMessageRequest(RepoRequest):
    group_id: str

class EditCommitMessageRequest(RepoRequest):
    group_id: str
    message: str


class TagRequest(RepoRequest):
    pass



# -----------------------------
# Request / Response Models
# -----------------------------
class UserRegisterRequest(BaseModel):
    username: str
    password: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str