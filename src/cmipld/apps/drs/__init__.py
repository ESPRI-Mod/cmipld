import logging

from cmipld.apps.drs.models import ProjectSpecs
import cmipld.api.projects as projects

_LOGGER = logging.getLogger("drs")


def parse_project_specs(project_id: str) -> ProjectSpecs:
    cmip6_project = projects.find_project(project_id)
    if not cmip6_project:
        msg = f'Unable to find project {project_id}'
        _LOGGER.fatal(msg)
        raise ValueError(msg)
    try:
        drs_json_specs = cmip6_project[project_id]
        drs_specs = ProjectSpecs(**drs_json_specs)
    except Exception as e:
        msg = f'Unable to read specs in project {project_id}'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
    return drs_specs


if __name__ == "__main__":
    drs_specs = parse_project_specs('cmip6plus').drs_specs
    print(drs_specs[1])
    