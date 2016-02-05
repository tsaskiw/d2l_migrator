#!/usr/bin/env sh

`ctags -R --languages=python --exclude=.git -f ../d2l_migrator/tags --tag-relative=yes ../d2l_migrator/*`
