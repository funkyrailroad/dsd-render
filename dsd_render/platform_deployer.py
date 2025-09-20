"""Manages all Render-specific aspects of the deployment process.

Notes:
- 

Add a new file to the user's project, without using a template:

    def _add_dockerignore(self):
        # Add a dockerignore file, based on user's local project environmnet.
        path = dsd_config.project_root / ".dockerignore"
        dockerignore_str = self._build_dockerignore()
        plugin_utils.add_file(path, dockerignore_str)

Add a new file to the user's project, using a template:

    def _add_dockerfile(self):
        # Add a minimal dockerfile.
        template_path = self.templates_path / "dockerfile_example"
        context = {
            "django_project_name": dsd_config.local_project_name,
        }
        contents = plugin_utils.get_template_string(template_path, context)

        # Write file to project.
        path = dsd_config.project_root / "Dockerfile"
        plugin_utils.add_file(path, contents)

Modify user's settings file:

    def _modify_settings(self):
        # Add platformsh-specific settings.
        template_path = self.templates_path / "settings.py"
        context = {
            "deployed_project_name": self._get_deployed_project_name(),
        }
        plugin_utils.modify_settings_file(template_path, context)

Add a set of requirements:

    def _add_requirements(self):
        # Add requirements for deploying to Fly.io.
        requirements = ["gunicorn", "psycopg2-binary", "dj-database-url", "whitenoise"]
        plugin_utils.add_packages(requirements)
"""

import sys, os, re, json
from pathlib import Path

from django.utils.safestring import mark_safe

import requests

from . import deploy_messages as platform_msgs

from django_simple_deploy.management.commands.utils import plugin_utils
from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config
from django_simple_deploy.management.commands.utils.command_errors import DSDCommandError


class PlatformDeployer:
    """Perform the initial deployment to Render

    If --automate-all is used, carry out an actual deployment.
    If not, do all configuration work so the user only has to commit changes, and ...
    """

    def __init__(self):
        self.templates_path = Path(__file__).parent / "templates"
        self.deployed_project_name = "test project"

    # --- Public methods ---

    def deploy(self, *args, **options):
        """Coordinate the overall configuration and deployment."""
        plugin_utils.write_output("\nConfiguring project for deployment to Render...")

        self._validate_platform()
        self._prep_automate_all()

        # Configure project for deployment to Render

        self._add_render_yaml()
        self._add_render_entrypoint()
        self._add_requirements()
        self._conclude_automate_all()
        self._show_success_message()

    # --- Helper methods for deploy() ---

    def _validate_platform(self):
        """Make sure the local environment and project supports deployment to Render.

        Make sure CLI is installed, and user is authenticated. Make sure necessary
        resources have been created and identified, and that we have the user's
        permission to use those resources.

        Returns:
            None
        Raises:
            DSDCommandError: If we find any reason deployment won't work.
        """
        if dsd_config.unit_testing:
            # Unit tests don't use the platform's CLI. Use the deployed project name
            # that was passed to the django-simple-deploy CLI.
            self.deployed_project_name = dsd_config.deployed_project_name
            return

        self._validate_cli()

    def _prep_automate_all(self):
        """Take any further actions needed if using automate_all."""
        pass

    def _add_render_entrypoint(self):
        """Add an entrypoint script for Render."""

        # Build contents of render.yaml
        template_path = self.templates_path / "render_entrypoint.sh"
        context = {}
        contents = plugin_utils.get_template_string(template_path, context)

        # Write file to project.
        path = dsd_config.project_root / "render_entrypoint.sh"
        plugin_utils.add_file(path, contents)

    def _add_render_yaml(self):
        """Add a minimal render.yaml file."""

        # Build contents of render.yaml
        template_path = self.templates_path / "render.yaml"
        context = {
            "deployed_project_name": self.deployed_project_name,
        }
        contents = plugin_utils.get_template_string(template_path, context)

        # Write file to project.
        path = dsd_config.project_root / "render.yaml"
        plugin_utils.add_file(path, contents)

    def _add_requirements(self):
        """Add requirements for deploying to Render."""
        requirements = [
            "gunicorn",
            # "psycopg2-binary",
            # "dj-database-url",
            # "whitenoise",
        ]
        plugin_utils.add_packages(requirements)

    def _validate_cli(self):
        """Make sure the Render CLI is installed, and user is authenticated."""
        cmd = "render --version"

        # This generates a FileNotFoundError on Ubuntu if the CLI is not installed.
        try:
            output_obj = plugin_utils.run_quick_command(cmd)
        except FileNotFoundError:
            raise DSDCommandError(platform_msgs.cli_not_installed)

        plugin_utils.log_info(output_obj)

        # DEV: Note which OS this block runs on; I believe it's macOS.
        if output_obj.returncode:
            raise DSDCommandError(platform_msgs.cli_not_installed)

        # Check that user is authenticated.
        user_email = self._get_cli_logged_in_user_or_error()
        msg = f"  Logged in to Render CLI as: {user_email}"
        plugin_utils.write_output(msg)

    def _get_cli_logged_in_user_or_error(self):
        cmd = "render whoami"
        output_obj = plugin_utils.run_quick_command(cmd)

        error_msg = "Error: failed to create client: run `render login` to authenticate"
        if error_msg in output_obj.stderr.decode():
            raise DSDCommandError(platform_msgs.cli_logged_out)

        # render whoami command does not support json output (as of version 2.2.0)
        stdout = output_obj.stdout.decode()
        for line in stdout.split("\n"):
            if "Email" in line:
                user_email = line.split(":")[1].strip()
        return user_email

    def _conclude_automate_all(self):
        """Finish automating the push to Render.

        - Commit all changes.
        - ...
        """
        # Making this check here lets deploy() be cleaner.
        if not dsd_config.automate_all:
            return

        plugin_utils.commit_changes()

        # Push project.
        plugin_utils.write_output("  Deploying to Render...")

        # Should set self.deployed_url, which will be reported in the success message.
        pass

    def _show_success_message(self):
        """After a successful run, show a message about what to do next.

        Describe ongoing approach of commit, push, migrate.
        """
        if dsd_config.automate_all:
            msg = platform_msgs.success_msg_automate_all(self.deployed_url)
        else:
            msg = platform_msgs.success_msg(log_output=dsd_config.log_output)
        plugin_utils.write_output(msg)
