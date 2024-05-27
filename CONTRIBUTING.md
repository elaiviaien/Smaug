# Contributing to Smaug

First off, thank you for considering contributing to Smaug. With your help, we can make Smaug better for everyone.

## Where do I go from here?

If you've noticed a bug or have a feature request, make one! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## Fork & create a branch

If this is something you think you can fix, then fork Smaug and create a branch with a descriptive name.

A good branch name would be (where issue #55 is the ticket you're working on):

```bash
git checkout -b 55-add-nodejs-support
```

## Get the test suite running

Make sure you're using a venv with the requirements installed while developing:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first.

## Get the style right

Your patch should follow the same syntax and semantic.

## Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with Smaug's master branch:

```bash
git remote add upstream git@github.com:elaiviaien/Smaug.git
git checkout master
git pull upstream master
```

Then update your feature branch from your local copy of master, and push it!

```bash
git checkout 55-add-nodejs-support
git rebase master
git push --set-upstream origin 55-add-nodejs-support
```

Finally, go to GitHub and make a Pull Request.

## Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

## Merging a PR (maintainers only)

A PR can only be merged into master by a maintainer if:

- It is passing CI.
- It has been approved by at least one maintainer. If it was a maintainer who opened the PR, only an additional maintainer can approve it.
- It has no requested changes.
- It is up to date with current master.

Any maintainer is allowed to merge a PR if all of these conditions are met.
