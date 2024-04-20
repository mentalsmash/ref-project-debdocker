###############################################################################
# Copyright 2020-2024 Andrea Sorbini
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################
from typing import NamedTuple

from ..write_output import write_output


def configure(cfg: NamedTuple, github: NamedTuple, inputs: NamedTuple) -> dict:
  runner = cfg.ci.runners[inputs.build_platform]

  repository_name = github.repository.replace("/", "-")
  build_platform_label = cfg.dyn.build.platform.replace("/", "-")
  base_image_tag = inputs.base_image.replace(":", "-")
  ci_tester_image = f"{cfg.ci.ci_tester_repo}:{base_image_tag}"

  test_id = f"ci-{build_platform_label}__{cfg.dyn.build.version}"
  test_artifact = f"{repository_name}-test-{test_id}__{cfg.dyn.test_date}"

  write_output(
    {
      "CI_RUNNER": runner,
      "CI_TESTER_IMAGE": ci_tester_image,
      "TEST_ARTIFACT": test_artifact,
      "TEST_ID": test_id,
    }
  )