## Testing

- Check your work in between changes by running `just test`. This runs _all_
  checks.
- To resolve issues, the `just test` command takes no arguments and fans out to
  more specific commands like `tox`, `pytest`, and `pre-commit`. When fixing a
  particular issue, verify your fix by running the more specific check command
  defined in tox.ini, e.g. `pytest -k name_of_your_specific_test`.
