---
created: 2026-03-23T17:01:23.376Z
title: Preserve branch history context
area: general
files: []
---

## Problem

The commit history UI appears to hide or drop forward commits when the user is on a detached HEAD, which can make the history view feel incomplete and confusing. The current checkout-style action is also a bit too destructive for a read-only inspection flow.

## Solution

TBD: keep the history view aligned with the current Git branch state, and consider a non-destructive preview/read-only inspection mode before changing any checkout behavior.
