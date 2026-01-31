## Testing

- Check your work in between changes by running `just test`. This runs _all_
  checks.
- To resolve issues, the `just test` command takes no arguments and fans out to
  more specific commands like `just pytest`, `just lint`, and `just typecheck`.
  When fixing a particular issue, verify your fix by running the more specific
  check command, e.g. `just pytest -- -k name_of_your_specific_test`.
