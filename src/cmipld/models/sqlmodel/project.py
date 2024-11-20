import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Column, Field, Relationship, SQLModel

import cmipld.db as db
from cmipld.models.sqlmodel.mixins import IdMixin, PkMixin, TermKind


class Project(SQLModel, PkMixin, IdMixin, table=True):
    __tablename__ = "projects"
    specs: dict = Field(sa_column=sa.Column(JSON))
    collections: list["Collection"] = Relationship(back_populates="project")


class Collection(SQLModel, PkMixin, IdMixin, table=True):
    __tablename__ = "collections"
    data_descriptor_id: str
    context: dict = Field(sa_column=sa.Column(JSON))
    project_pk: int | None = Field(default=None, foreign_key="projects.pk")
    project: Project = Relationship(back_populates="collections")
    terms: list["PTerm"] = Relationship(back_populates="collection")


class PTerm(SQLModel, PkMixin, IdMixin, table=True):
    __tablename__ = "pterms"
    specs: dict = Field(sa_column=sa.Column(JSON))
    kind: TermKind = Field(sa_column=Column(sa.Enum(TermKind)))
    collection_pk: int | None = Field(default=None, foreign_key="collections.pk")
    collection: Collection = Relationship(back_populates="terms")


def create_drs_name_index():
    PTerm.__table_args__ = sa.Index(
        "drs_name_index", PTerm.__table__.c.specs["drs_name"]
    )


def project_create_db():
    create_drs_name_index()
    SQLModel.metadata.create_all(db.CMIP6PLUS_DB_CONNECTION.get_engine())


if __name__ == "__main__":
    project_create_db()
