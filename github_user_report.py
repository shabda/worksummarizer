from pygithub3 import Github
from pygithub3.services.repos import Commits

from settings.auth import github_auth

gh = Github(login=github_auth[0], password=github_auth[1])
commits = []
agiliq = gh.users.get('agiliq')
agiliq_repos = gh.repos.list('agiliq').all()
for repo in agiliq_repos:
	print repo
	agiliq_commit = Commits(user='agiliq', repo=repo.name)
	agiliq_commit.list().all()
print commits


