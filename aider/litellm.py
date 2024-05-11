import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

os.environ["OR_SITE_URL"] = "http://Aider.chat"
os.environ["OR_APP_NAME"] = "Aider"

import litellm  # noqa: E402

__all__ = [litellm]
