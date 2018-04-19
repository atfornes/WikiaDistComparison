#!/bin/bash

array=($(ls -d *.com.csv))
wikis=$(printf "%s/ " "${array[@]%.*}")

../../query_bot_users.py $wikis | grep -o "[0-9]*" > botIds.csv
