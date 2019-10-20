# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 18:09:30 2019

@author: Chris
"""
from git import Repo
import re
import numpy as np

#find lines with summary of differences - marked with @@
def summary_lines(difflines):
    pattern = re.compile('@@')
    return [s for s in difflines if pattern.match(s)]

#find the deleted lines and added lines
#-startdel[,enddel] +startadd[,endadd]
def parse_summary(summary):
    bits = summary.split(' ')
    delBit = bits[1].split(',')
    addBit = bits[2].split(',')
    delStart = -int(delBit[0])
    if len(delBit)==1:
        delLength = 1
    else:
        delLength = int(delBit[1])
    addStart = int(addBit[0])
    if len(addBit)==1:
        addLength = 1
    else:
        addLength = int(addBit[1])
    return (delStart, delLength, addStart, addLength)
    
# find the enclosing scope
def find_enclosing_scope(delStart, delLength, addStart, addLength, fileContents):
    # first scan forward from delStart+delLength-1 until we find more closing braces than opening
    lineNum = delStart-1
    #print('s:'+fileContents[lineNum])
    numOpen = 1
    while numOpen > 0:
        lineNum += 1
        if lineNum >= len(fileContents):
            lineNum = len(fileContents) - 1
            break
        line = fileContents[lineNum]
        #print('f:' + line)
        for c in line:
            if c=='}':
                numOpen -= 1
                if numOpen==0:
                    break
            if c=='{':
                numOpen += 1
    scopeEnd = lineNum+1
    # now scan backwards from same spot    
    lineNum = delStart
    #print('s:'+fileContents[lineNum])
    numOpen = 1
    while numOpen > 0:
        lineNum -= 1
        if lineNum < 0:
            lineNum = 0
            break
        line = fileContents[lineNum]
        #print('b:' + line)
        for c in line[::-1]:
            if c=='{':
                numOpen -= 1
                if numOpen==0:
                    break
            if c=='}':
                numOpen += 1
    scopeStart = lineNum+1
    return (scopeStart, scopeEnd)


# in a list of blame messages, find the one with the most recent commit
def find_most_recent_commit(blames):
    commits = []
    times = []
    for b in blames:
        tmp = b.split()
        commits += [tmp[0]]
        times += [int(tmp[3])]
    return commits[np.argmax(times)]

    
# find the Vulnerability-Contributing Commit(s)
def find_vcc(repo_path, fixing_commit, blame_opt='-w'):
    # create repo object from path
    repo = Repo(repo_path)
    HEAD = fixing_commit
    PREV = fixing_commit + '^'

    # find all of the files changed
    files = repo.git.diff('--name-only', PREV, HEAD).splitlines()

    commitsFound = []
    for file in files:
        ##print('File: ' + file)
        # check file exists in PREV - if not then skip
        # read in the previous version of the file
        try:
            # we need the file contents to find the enclosing scope
            fileContents = repo.git.show(PREV+':'+file).splitlines()
        except:
            # file must be new in HEAD, so does not contribute to VCC
            continue
        # find the lines that are different, by looking for @@ -a,b +c,d @@
        difflines = repo.git.diff('-U0',PREV,HEAD,file).splitlines()
        summlines = summary_lines(difflines)
        for line in summlines:
            ##print(line)
            # parse the numbers
            (delStart, delLength, addStart, addLength) = parse_summary(line)
            ##print("delStart, delLength, addStart, addLength: ",delStart, delLength, addStart, addLength)
            # if there are deleted lines, find the blamed commit(s)
            if delLength > 0:
                blames = repo.git.blame(blame_opt,'--date=unix','-e','-f','-L '+str(delStart) + ',' + str(delStart + delLength - 1), PREV, file).splitlines()
                commit = find_most_recent_commit(blames)
                ##print('Commit: '+commit)
                commitsFound += [commit]*delLength # add one for each line deleted
            # if there are added lines, find the enclosing scope and then find the commits
            if addLength > 0:
                (scopeStart, scopeEnd) = find_enclosing_scope(delStart, delLength, addStart, addLength, fileContents)
                blames = repo.git.blame(blame_opt,'--date=unix','-e','-f','-L '+str(scopeStart) + ',' + str(scopeEnd), PREV, file).splitlines()
                commit = find_most_recent_commit(blames)
                ##print('Commit: '+commit)
                commitsFound += [commit]*addLength # add once for each line added
                
    # now find the most common entry in commitsFound
    mostCommonCommit = max(set(commitsFound), key=commitsFound.count)
    ##print(commitsFound)
    return mostCommonCommit