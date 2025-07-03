#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import os
import subprocess

RAGFORGE_VERSION_INFO = "unknown"


def get_ragforge_version() -> str:
    global RAGFORGE_VERSION_INFO
    if RAGFORGE_VERSION_INFO != "unknown":
        return RAGFORGE_VERSION_INFO
    version_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), os.pardir, "VERSION"
        )
    )
    if os.path.exists(version_path):
        with open(version_path, "r") as f:
            RAGFORGE_VERSION_INFO = f.read().strip()
    else:
        RAGFORGE_VERSION_INFO = get_closest_tag_and_count()
        LIGHTEN = int(os.environ.get("LIGHTEN", "0"))
        RAGFORGE_VERSION_INFO += " slim" if LIGHTEN == 1 else " full"
    return RAGFORGE_VERSION_INFO


def get_closest_tag_and_count():
    try:
        # Get the current commit hash
        version_info = (
            subprocess.check_output(["git", "describe", "--tags", "--match=v*", "--first-parent", "--always"])
            .strip()
            .decode("utf-8")
        )
        return version_info
    except Exception:
        return "unknown"
