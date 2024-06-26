# Reference Implementation for a Debian/Docker Project

This repository contains a reference implementation for a software project
which targets Linux (on 64-bit Intel, and 64-bit ARM platforms), and which
is distributed as a Debian package, and/or as a multi-platform Docker image.

The repository uses a mix of GitHub's Settings and GitHub Actions to
[implement, and enforce, a CI/CD development workflow](#implemented-development-workflow).

This reference implementation can be used as the basis for quickly bootstrapping
other similar projects (by [following the included guide](#project-bootstrap-guide)),
or as an inspiration for implementing similar solution targeting different
platforms (e.g. Windows), or distribution methods (e.g. other packaging formats).

## Implemented Development Workflow

### Releases

- The project is developed and maintained from a single, **main development branch**.

- The project follows the ["semantic versiosing"](https://semver.org/) approach to releases naming:

  - Every release is assigned a 3-components label `<major>.<minor>.<patch>`.

  - Every release is uniquely associated with a `git` tag of the same name referencing a
    commit from the **main development branch**.

- New releases are triggered automatically by changes in the repository:

  - **Nightly** releases are automatically triggered every time new commits are pushed
    to the **main development branch**.

  - **Stable** releases are automatically triggered whenever a **tag** is pushed
    to the repository (unless the tag contains a `/`).

- The project will release two Docker images named after the repository (`<owner>/<repo>`):

  - A **nightly** image, built from the `HEAD` commit of the **main development branch**, and
    tagged as `<owner>/<repo>:nightly`, and `<owner>/<repo>:<main-dev-branch>`.

  - A **stable** image, built from the most recently pushed `git` tag (expected to follow
    the scheme `<major>.<minor>.<patch>`). This image is tagged on the Docker registry as
    `<owner>/<repo>:latest`.

    The image also receives "semantic" labels derived from the `git` tag:
    `<owner>/<repo>:<major>.<minor>.<patch>`, `<owner>/<repo>:<major>.<minor>`,
    and `<owner>/<repo>:<major>`.

  - The images are pushed both to [DockerHub](https://hub.docker.com/), and to GitHub's
    [Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry),
    as a ["container" package](https://github.com/features/packages).

  - Images are first built with a "pre-release" tag to undergo testing, and they are pushed
    with their final release tags only after successful validation.

  - The "pre-release" tags can be pushed to a different registry than the final one,
    so that access to them may be restricted to only authorized users (and CI infrastructure),
    and to prevent unsuccessful processes from polluting the release repository.

- The project provides architecture-specific Debian packages for every **stable** release.

  - The packages follow the naming scheme `<repo>_<deb-version>_<arch>.deb`, where:

    - `<deb-version>` takes the form `A.B.C-N`, from the concatenation of the **upstream version**
      (i.e. `A.B.C`) with the **debian release increment** (i.e. `N`).

    - `<arch>` is the Debian architecture identifier (e.g. `amd64`, `arm64`).
  
  - The packages are made available through the repository's "Releases" page, and from the artifact
    logs of the builder workflows.

### Development

- All changes to the **main development branch** must be submitted through a **pull request** (PR).

  - Every PR must receive a minimum number of reviews (`1`) by a maintainer in order to be accepted.

  - Every commit pushed to a PR branch will invalidate previously received reviewes.

  - A PR must be in sync with the **main development branch** (via merge or rebase) in order to be
    accepted.

  - The "auto-merge" feature can be used to automatically merge PRs after review by requiring that
    all expected checks are successful.

  - Every PR must undergo two levels of automatic validation in order to be merged:
  
    - A **basic validation**, which is triggered every time a new PR is opened, or whenever an
      existing PR is updated (by new commits, or by transitioning to "ready for review" state
      if opened as draft). The basic validation is expected to build and test the project's image
      for a selected reference platform (e.g. `linux/amd64`).
  
    - A **full validation**, which is triggered every time a PR transitions to the "accepted"
      review state. The full validation is expected to build and test the project's image for other
      targeted platforms (e.g. `linux/arm64`). It is also expected validate the changes by running
      the Debian release workflow on a reference platform (e.g. `linux/amd64`).

  - All workflow runs associated with a PR will be automatically pruned once the PR is closed:

    - If the PR was closed without merging, all runs will be deleted.

    - If the PR was merged, all runs will be deleted except for the most recent "basic validation",
      and "full validation" runs.

## Project Bootstrap Guide

The guide assumes that the repository will be owned by a GitHub organization
(of which you are an administrator). Some adjustments might be required to
use it for a personal repository.

### Repository Initialization

1. Create your repository (e.g. `my-org/my-repo`) if it doesn't already exist.

2. Import files from the reference repository into your repository:

   ```sh
   # Clone the reference repository
   git clone https://github.com/mentalsmash/ref-project-debdocker
   export REF_PROJECT=$(pwd)/ref-project-docker

   # Clone your repository
   git clone https://github.com/my-org/my-repo
   cd my-repo

   # GitHub Action workflows and the helper Python scripts
   mkdir -p .github/
   cp -a ${REF_PROJECT}/.github/* .github/

   # Makefile
   cp -a ${REF_PROJECT}/Makefile ./Makefile

   # Docker compose configuration
   cp -a ${REF_PROJECT}/compose.yml ./compose.yml

   # Docker build files
   mkdir -p docker/
   cp -a ${REF_PROJECT}/docker/* ./docker/

   # Helper scripts
   mkdir -p scripts/
   cp -a ${REF_PROJECT}/scripts/* ./scripts/

   # Debian packaging files
   mkdir -p debian/
   cp -a ${REF_PROJECT}/debian/* ./debian/

   # pre-commit and ruff configuration
   cp -a ${REF_PROJECT}/.pre-commit-config.yaml ./.pre-commit-config.yaml
   cp -a ${REF_PROJECT}/ruff.toml ./ruff.toml
   ```

3. Edit [.github/workflows_pyconfig/settings.yml](.github/workflows_pyconfig/settings.yml) with your preferred settings.

   - Replace all references to `mentalsmash/ref-project-debdocker` with your repository. Using `sed` if you want:

     ```sh
     sed -r -i -e "s:mentalsmash(.)ref-project-debdocker:my-org(\1)my-repo:g" .github/workflows_pyconfig/settings.yml
     ```

   - Common settings:

     - `release.base_image`: the base image for the generated images (e.g. `ubuntu:22.04`).

     - `release.build_platforms`: list of Docker build platforms (supported values: `linux/amd64`, `linux/arm64`).

     - `release.prerelease_repo` the "pre-release" image tag that will be used for testing and to derive
       the release images after validation (e.g. `ghcr.io/my-org/my-repo-test`).

     - `release.repo`: a list of image repository that will be used to publish the
       "release" image after validation.

