# dsd-render

A plugin for deploying Django projects to Render, using django-simple-deploy.

For full documentation, see the documentation for [django-simple-deploy](https://django-simple-deploy.readthedocs.io/en/latest/).

Quick Start
---


## Prerequisites

Deployment to Render requires the following:

- You must be using Git to track your project
```
git init .
git add .
git commit -m "Initial commit"
```

- You must be hosting your Git repository on [GitHub](https://github.com/new),
  GitLab or Bitbucket. (For the free tier of Render, it must be a public
  repository.)

- You need to be tracking your dependencies with a `requirements.txt` file, or
  be using Poetry or Pipenv.

- Create a [Render account](https://dashboard.render.com/register)

- Install the [Render CLI](https://render.com/docs/cli).

- [Create a Render API key](https://render.com/docs/api#1-create-an-api-key)


## Configuration-only deployment

First, install `dsd-render` and add `django_simple_deploy` to `INSTALLED_APPS` in *settings.py*:

```sh
$ pip install dsd-render
# Add "django_simple_deploy" to INSTALLED_APPS in settings.py.
$ git commit -am "Added django_simple_deploy to INSTALLED_APPS."
```

When you install `dsd-render`, it will install `django-simple-deploy` as a dependency.

Now run the `deploy` command:

```sh
$ python manage.py deploy
```

This is the `deploy` command from `django-simple-deploy`, which makes all the
changes you need to run your project on Render.


At this point, you should review the changes that were made to your project.
Running `git status` will show you which files were modified, and which files
were created for a successful deployment. If you want to continue with the
deployment process, commit these changes and push them up to your remote.


```sh
$ git add .
$ git commit -m "Configured for deployment to Render."
$ git push
```

Create a Blueprint in Render and give it a name
  - https://dashboard.render.com/select-repo?type=blueprint
  - NOTE: this could potentially be done optionally via an API request
    directly to Render
  - NOTE: configure project name in blueprint via a CLI arg


Once the project has finished deploying, it will be given a URL e.g.
`test-project-5wig.onrender.com`. Add this to the `ALLOWED_HOSTS` list in your
project's `settings.py` file.

```
# Make changes to settings.py
```

Commit these changes and push them up to your remote.

```
git add .
git commit -m 'Add to ALLOWED_HOSTS.'
git push
```

The project is configured to automatically redploy for each push to the
remote. Your updates should be available momentarily.
  - ! NOTE: automatically deployments can be disabled, and the CLI can be used
    to trigger deployments manually.

You can find a record of the deployment process in `dsd_logs/`. It contains
most of the output you saw when running `deploy`.
