To use git patch mode and display word diff rather than line diff, do the following.

1. copy `git-add--interactive` from your git installation directory to somewhere in your `PATH` like `/usr/local/bin`

2. rename the copied `git-add--interactive` to `git-add--interactive-words`

3. find the line that looks like this:
    @colored = run_cmd_pipe("git", @diff_cmd, qw(--color --), $path);
and replace it with this:
    @colored = run_cmd_pipe("git", @diff_cmd, qw(--color --color-words --), $path);


thanks to `mabraham`'s StackOverflow answer where this came from `http://stackoverflow.com/questions/10873882/how-to-use-color-words-with-git-add-patch`