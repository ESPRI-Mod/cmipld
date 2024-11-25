from sqlmodel import Session

from cmipld.apps.drs.models import ProjectSpecs


def parse_drs_specs(project_id: str, session: Session) -> ProjectSpecs:
    pass