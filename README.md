# BEAN Server

License: MIT

## Setup
- Install `devenv` by following steps #1 and #2 of [this tutorial](https://devenv.sh/getting-started/)
- Clone this repo.
- `devenv shell` to enter the developer environment. This automatically gets all necessary resources like `python` and `postgres`, and makes them available on your `$PATH`.
- `devenv up -d` to start necessary services, such as Postgres.

## Project Overview
- This is a Django project created using the [Cookiecutter Django template](https://github.com/cookiecutter/cookiecutter-django).
  - The repository structure follows [Cookiecutter Django's template](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#creating-your-first-django-app).
    - In our case, `django_project_root` is `beanserver`, and our main app is `beanserver/backend`. **Put your generation logic in `backend`**.
    - NOTE: `beanserver/users` was automatically generated with the template.
    - **Read the Cookiecutter docs page to learn how to test and lint your code!**
  - We use [Django REST framework](https://www.django-rest-framework.org/) to build our API endpoints.
    - Skim through [Mozilla's introduction of Django (specifically the diagram)](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Introduction#what_does_django_code_look_like) to understand Django's architecture.
    - Follow [the REST framework's tutorials](https://www.django-rest-framework.org/tutorial/quickstart/) and documentation to learn how to build APIs.
    - The [Django documentation will be useful](https://docs.djangoproject.com/en/5.1/). Just note that a lot of its API are wrapped
      by the REST framework, so you should use that instead.
- Development resources are managed by `devenv`, which internally uses `nix` to manage packages.
  - Refer to the [documentation](https://devenv.sh/basics/) if you want to make changes.
  - **Integration with VSCode**: [Set up direnv (click and follow both links)](https://devenv.sh/editor-support/vscode/)
- [git pre-commit](https://pre-commit.com/) (configured with `devenv`) is used to enforce code quality when committing. It should automatically run whenever you commit anything.
- The `main` branch of the repo is protected. Make changes in a branch and then create a PR.


## Basic Commands
- NOTE: Taken from [the cookiecutter django docs.](https://cookiecutter-django.readthedocs.io/en/latest/index.html).
### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy beanserver

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest
