import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Column, Field, Relationship, SQLModel

import cmipld.db as db
from cmipld.models.sqlmodel.mixins import IdMixin, PkMixin, TermKind


class DataDescriptor(SQLModel, PkMixin, IdMixin, table=True):
    __tablename__ = "data_descriptors"
    context: dict = Field(sa_column=sa.Column(JSON))
    terms: list["UTerm"] = Relationship(back_populates="data_descriptor")


class UTerm(SQLModel, PkMixin, IdMixin, table=True):
    __tablename__ = "uterms"
    specs: dict = Field(sa_column=sa.Column(JSON))
    kind: TermKind = Field(sa_column=Column(sa.Enum(TermKind)))
    data_descriptor_pk: int | None = Field(
        default=None, foreign_key="data_descriptors.pk"
    )
    data_descriptor: DataDescriptor = Relationship(back_populates="terms")


def univers_create_db():
    SQLModel.metadata.create_all(db.UNIVERS_DB_CONNECTION.get_engine())


if __name__ == "__main__":
    univers_create_db()
