import logging

from esgvoc.apps.drs.models import ProjectSpecs
import esgvoc.api.projects as projects

_LOGGER = logging.getLogger("drs")


def parse_project_specs(project_id: str) -> ProjectSpecs:
    project_specs = projects.find_project(project_id)
    if not project_specs:
        msg = f'Unable to find project {project_id}'
        _LOGGER.fatal(msg)
        raise ValueError(msg)
    try:
        result = ProjectSpecs(**project_specs)
    except Exception as e:
        msg = f'Unable to read specs in project {project_id}'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
    return result


if __name__ == "__main__":
    drs_specs = parse_project_specs('cmip6plus').drs_specs
    print(drs_specs[1])
    