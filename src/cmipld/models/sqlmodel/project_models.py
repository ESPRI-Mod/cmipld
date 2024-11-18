from sqlmodel import Field, SQLModel, Column, Relationship, create_engine  
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON

from cmipld.models.sqlmodel.mixins import PkMixin, IdMixin, TermKind
import cmipld.settings as settings


class Project(SQLModel, PkMixin, IdMixin, table=True):
    __tablename__ = 'projects'
    json_content: dict = Field(sa_column=sa.Column(JSON))
    collections: list['Collection'] = Relationship(back_populates='project')


class Collection(SQLModel, PkMixin, IdMixin, table=True):
    __tablename__ = 'collections'
    data_descriptor_id: str
    project_pk: int | None = Field(default=None, foreign_key='projects.pk')
    project: Project = Relationship(back_populates='collections')
    terms: list['PTerm'] = Relationship(back_populates='collection')


class PTerm(SQLModel, PkMixin, IdMixin, table=True):
    __tablename__ = 'pterms'
    json_content: dict = Field(sa_column=sa.Column(JSON))
    kind: TermKind = Field(sa_column=Column(sa.Enum(TermKind)))
    collection_pk: int | None = Field(default=None, foreign_key='collections.pk')
    collection: Collection = Relationship(back_populates='terms')


def create_drs_name_index():
    PTerm.__table_args__ = (sa.Index('drs_name_index', PTerm.__table__.c.json_content['drs_name']))


def project_create_db():  
    engine = create_engine(settings.PROJECT_SQLITE_URL, echo=False)
    create_drs_name_index()
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":  
    project_create_db()