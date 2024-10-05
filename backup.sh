#!/usr/bin/env bash

pg_dump --host=localhost --username=boston --verbose --format=c pgsearch > pg_search_backup.dump
cp pg_search_backup.dump '/Users/jonstefansson/Library/Mobile Documents/com~apple~CloudDocs/Documents/Personal/backups/pg_search/'
