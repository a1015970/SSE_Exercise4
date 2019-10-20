# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 21:46:41 2019

@author: Chris
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 22:45:02 2019

@author: Chris Crouch - a1015970
"""
import find_vcc
import analyze_git_commit
from git import Repo, RemoteProgress
import os

class Progress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(self._cur_line)
        
vcc_opts = ['-e', '-w', '-wM', '-wC', '-wCC', '-wCCC']
#%%

local_link = "../ovirt-engine"
remote_link = "https://gerrit.ovirt.org/ovirt-engine"
fixing_commit = "d0e33ace71b7603450fc1aa7725f53dbc545831"

if not os.path.isdir(local_link):
    Repo.clone_from(remote_link, local_link, progress=Progress())

repo = Repo(local_link)
print("\n\n", repo.git.remote('get-url','origin'))

vccs = []
for opt in vcc_opts:
    vccs += [find_vcc.find_vcc(local_link, fixing_commit, opt)]
print("\nVCC is ", str(set(vccs)))
for vcc in set(vccs):
    analyze_git_commit.analyze_git_commit(local_link, vcc)


#%%

local_link = "../tomcat80"
remote_link = "https://github.com/apache/tomcat80"
fixing_commit = "2e5cc28052e84ba45196949ba602484221bbf33c"

if not os.path.isdir(local_link):
    Repo.clone_from(remote_link, local_link, progress=Progress())

repo = Repo(local_link)
print("\n\n", repo.git.remote('get-url','origin'))

vccs = []
for opt in vcc_opts:
    vccs += [find_vcc.find_vcc(local_link, fixing_commit, opt)]
print("\nVCC is ", str(set(vccs)))
for vcc in set(vccs):
    analyze_git_commit.analyze_git_commit(local_link, vcc)

#%%
local_link = "../camel-4580"
remote_link = "https://github.com/apache/camel"
fixing_commit = "4580e4d6c65cfd544c1791c824b5819477c583c"

if not os.path.isdir(local_link):
    Repo.clone_from(remote_link, local_link, progress=Progress())

repo = Repo(local_link)
print("\n\n", repo.git.remote('get-url','origin'))

vccs = []
for opt in vcc_opts:
    vccs += [find_vcc.find_vcc(local_link, fixing_commit, opt)]
print("\nVCC is ", str(set(vccs)))
for vcc in set(vccs):
    analyze_git_commit.analyze_git_commit(local_link, vcc)

