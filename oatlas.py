import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from dotenv import dotenv_values

from oatlas.main import run

try:
    import absl.logging

    absl.logging.set_verbosity(absl.logging.ERROR)
except Exception:
    pass


def update_environment_variables():
    """
    Update the environment variables from .env and .env.private
    """
    env_defaults = dotenv_values(".env")
    env_private = dotenv_values(".env.private")

    final_env = {}
    for key, value in env_defaults.items():
        override = env_private.get(key)
        if override and override.lower() != "none":
            final_env[key] = override
        else:
            final_env[key] = value

    os.environ.update(final_env)


if __name__ == "__main__":
    update_environment_variables()
    run()
