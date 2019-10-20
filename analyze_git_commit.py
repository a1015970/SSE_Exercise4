# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 21:27:47 2019

@author: Chris Crouch - a1015970
"""


from git import Repo
import re


def match_deleted(lines):
    # return lines with leading dash
    pattern = re.compile('^-$|^-[^-]')
    return [s for s in lines if pattern.match(s)]

def match_added(lines):
    #return lines with leading plus
    pattern = re.compile('^\+$|^\+[^\+]')
    return [s for s in lines if pattern.match(s)]

def notmatch_comment(lines):
    # return lines that aren't comments
    # note that this is clearly not robust to all comments, just what are in my files
    pattern = re.compile('^[-|\+]\s*\*') # plus or minus, whitespace, '*' 
    lines = [s for s in lines if not pattern.match(s)]
    pattern = re.compile('^[-|\+]\s*/\*') # plus or minus, whitespace, '/*' 
    lines = [s for s in lines if not pattern.match(s)]
    pattern = re.compile('^[-|\+]\s*\/\/') # plus or minus, whitespace, '//' 
    lines = [s for s in lines if not pattern.match(s)]
    return lines

def notblank(lines):
    # strip out blank lines - for some reason some get past diff flag
    pattern = re.compile('^[-|\+]\s*$') #SOL, plus or minus, whitespace, EOL
    return [s for s in lines if not pattern.match(s)]


# this is the main function
# analyze the given commit in a git repo
# print out the results
def analyze_git_commit(repo_path, fixing_commit):
    # create repo object from path
    repo = Repo(repo_path)
    HEAD = fixing_commit
    PREV = fixing_commit + '^'
    print(repo_path + '  ' + fixing_commit)
        
    # get commit message
    out1 = repo.git.log(HEAD, -1, '--pretty=%s')
    print("[A] Commit message: %s"%out1)

    # get number of files affected by commit
    out2 = repo.git.diff('--name-only', HEAD, PREV).splitlines()
    print("[B] Number of affected files: %d"%len(out2))
    
    # how many affected directories
    out3 = repo.git.diff('--dirstat', HEAD, PREV).splitlines()
    print("[C] Number of affected directories: %d"%len(out3))
    
    # how many lines of code deleted
    out4 = repo.git.diff(HEAD, PREV).splitlines()
    # only keep lines starting with '-' (and not '---')
    out4 = match_deleted(out4)
    print("[D] Number of deleted lines (including comments and blank lines): %d"%len(out4))
    
    # how many lines of code added
    out5 = repo.git.diff(HEAD, PREV).splitlines()
    # only keep lines starting with '+' (and not '+++')
    out5 = match_added(out5)
    print("[E] Number of added lines (including comments and blank lines): %d"%len(out5))

    # how many lines of code deleted
    out6 = repo.git.diff('--ignore-blank-lines', HEAD, PREV).splitlines()
    # only keep lines starting with '-' (and not '---')
    out6 = match_deleted(out6)
    out6 = notmatch_comment(out6)
    out6 = notblank(out6)
    print("[F] Number of deleted lines (excluding comments and blank lines): %d"%len(out6))
    
    # how many lines of code added
    out7 = repo.git.diff('--ignore-blank-lines', HEAD, PREV).splitlines()
    # only keep lines starting with '+' (and not '+++')
    out7 = match_added(out7)
    out7 = notmatch_comment(out7)
    out7 = notblank(out7)
    print("[G] Number of added lines (excluding comments and blank lines): %d"%len(out7))
    
    # number of days between fixing commit and previous commit
    print("[H] Number of days between fixing commit and previous commit: ")
    for file in repo.git.diff('--name-only', HEAD, PREV).splitlines():
        try:
            modTimes = repo.git.log(HEAD, PREV, -2, '--pretty=%ct', file).splitlines();
            if len(modTimes) == 2:
                print("  %s:  %.1f"%(file, (float(modTimes[0])-float(modTimes[1]))/86400)) # diff, convert sec to days
            else:
                print("  %s:  N/A (new file)"%file)
        except:
            print("  %s:  N/A (no file)"%file)
            
    # number of times each file has been modified
    print("[I] Number of time each file has been modified (including fixing commit): ")
    for file in repo.git.diff('--name-only', HEAD, PREV).splitlines():
        try:
            modLog = repo.git.log(HEAD, PREV, '--follow', '--pretty=oneline', file).splitlines();
            print("  %s:  %d"%(file, len(modLog)))
        except:
            print("  %s:  N/A"%file)

        
    # which developers have modified each file
    print("[J] Which developers have modified each file since its creation: ")
    for file in repo.git.diff('--name-only', HEAD, PREV).splitlines():
        print("  %s"%file)
        try:
            auths = repo.git.log(HEAD, PREV, '--follow', '--pretty=%aN', file).splitlines()
            for auth in set(auths):
                print("    %s"%auth)
        except:
            print("    N/A")
    
    # how many commits have each of these developers made
    print("[K] How many commits has each of these author made: ")
    allAuths = []
    for file in repo.git.diff('--name-only', HEAD, PREV).splitlines():
        try:
            allAuths += repo.git.log(HEAD, PREV, '--follow', '--pretty=%aN', file).splitlines()
        except:
            pass
    allAuths = list(set(allAuths)) # unique
    log = repo.git.log(HEAD, PREV,'--pretty=%aN')
    for auth in allAuths:
        print("  %s: %d"%(auth, len(re.findall(auth,log))))