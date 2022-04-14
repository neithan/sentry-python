import os
import shutil
import subprocess
import tempfile

from sentry_sdk.consts import VERSION as SDK_VERSION

DIST_PATH = "dist"  # created by "make dist" that is called by "make aws-lambda-layer"
PYTHON_SITE_PACKAGES = "python"  # see https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path


class LayerBuilder:
    def __init__(
        self,
        base_dir,  # type: str
    ):
        # type: (...) -> None
        self.base_dir = base_dir
        self.python_site_packages = os.path.join(self.base_dir, PYTHON_SITE_PACKAGES)

    def make_directories(self):
        # type: (...) -> None
        os.makedirs(self.python_site_packages)

    def install_python_packages(self):
        # type: (...) -> None
        sentry_python_sdk = os.path.join(
            DIST_PATH,
            f"sentry_sdk-{SDK_VERSION}-py2.py3-none-any.whl",  # this is generated by "make dist" that is called by "make aws-lamber-layer"
        )
        subprocess.run(
            [
                "pip",
                "install",
                "--no-cache-dir",  # always access PyPI
                "--quiet",
                sentry_python_sdk,
                "--target",
                self.python_site_packages,
            ],
            check=True,
        )

    def create_init_serverless_sdk_package(self):
        # type: (...) -> None
        """
        Method that creates the init_serverless_sdk pkg in the
        sentry-python-serverless zip
        """
        serverless_sdk_path = (
            f"{self.python_site_packages}/sentry_sdk/"
            f"integrations/init_serverless_sdk"
        )
        if not os.path.exists(serverless_sdk_path):
            os.makedirs(serverless_sdk_path)
        shutil.copy(
            "scripts/init_serverless_sdk.py", f"{serverless_sdk_path}/__init__.py"
        )


def build_layer_dir():
    with tempfile.TemporaryDirectory() as base_dir:
        layer_builder = LayerBuilder(base_dir)
        layer_builder.make_directories()
        layer_builder.install_python_packages()
        layer_builder.create_init_serverless_sdk_package()

        shutil.copytree(base_dir, "dist-serverless")


if __name__ == "__main__":
    build_layer_dir()
