#!/bin/bash
# Git Backup Script

git add --all

git commit -am "backup $(date +'%x %X')"

# git remote set-url origin https://theharto:[PASSWORD]@github.com/theharto/rpi-boiler.git
git push -u origin master
