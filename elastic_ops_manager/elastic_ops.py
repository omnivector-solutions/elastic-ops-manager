#!/usr/bin/python3
"""ElasticOpsManager."""
import pathlib
import subprocess


from jinja2 import (
    Environment,
    FileSystemLoader,
)


OS_RELEASE = pathlib.Path("/etc/os-release").read_text().split("\n")
OS_RELEASE_CTXT = {
    k: v.strip("\"")
    for k, v in [item.split("=") for item in OS_RELEASE if item != '']
}

TEMPLATE_DIR = pathlib.Path("./templates")


def _render_template(template_name, target, context):
    rendered_template = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR))
    ).get_template(template_name)
    target.write_text(rendered_template.render(context))


class ElasticOpsManager:
    """ElasticOpsManager."""

    def __init__(self, elastic_service):
        """Initialize class attributes."""
        self._os = OS_RELEASE_CTXT['ID']
        self._version_id = OS_RELEASE_CTXT['VERSION_ID']
        self._elastic_service = elastic_service
        self._config_file_path = pathlib.Path(
            f"/etc/{elastic_service}/{elastic_service}.yml"
        )
        self._config_template_name = f"{elastic_service}.yml.j2"

    def install(self, resource):
        """Install system level deps."""
        self._install_java()
        self._install_elastic_resource(resource)

    def _install_elastic_resource(self, resource):
        if self._os == 'ubuntu':
            subprocess.call([
                "dpkg",
                "-i",
                resource
            ])
        elif self._os == 'centos':
            subprocess.call([
                "rpm",
                "--install",
                resource
            ])

    def _install_java(self):
        if self._os == 'ubuntu':
            subprocess.call(["apt", "update", "-y"])
            if self._version_id in ['20.04', '18.04']:
                subprocess.call(
                    ["apt", "install", "openjdk-8-jre-headless", "-y"]
                )
        elif self._os == 'centos':
            if self._version_id == '7':
                subprocess.call(["yum", "update", "-y"])
                subprocess.call(
                    ["yum", "install", "java-1.8.0-openjdk-headless", "-y"]
                )
            elif self._version_id == '8':
                subprocess.call(["dnf", "update", "-y"])
                subprocess.call(
                    ["dnf", "install", "java-1.8.0-openjdk-headless", "-y"]
                )

    def start_elastic_service(self):
        """Start elastic service."""
        subprocess.call([
            "systemctl",
            "enable",
            self._elastic_service
        ])
        subprocess.call([
            "systemctl",
            "start",
            self._elastic_service
        ])

    def render_config_and_restart(self, context):
        """Render the config and restart the service."""
        # Remove the pre-existing config
        if self._config_file_path.exists():
            self._config_file_path.unlink()

        # Write /etc/filebeat/filebeat.yml
        _render_template(
            self._config_template_name,
            self._config_file_path,
            context
        )

        # Restart filebeat service
        subprocess.call([
            "systemctl",
            "restart",
            self._elastic_service
        ])
