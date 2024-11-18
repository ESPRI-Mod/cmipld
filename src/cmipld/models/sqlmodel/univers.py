from sqlmodel import Field, SQLModel, Column, Relationship, create_engine  
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON

from cmipld.models.sqlmodel.mixins import PkMixin, IdMixin, TermKind
import cmipld.utils.settings as settings


class DataDescriptor(SQLModel, PkMixin, IdMixin, table=True):
    __tablename__ = 'data_descriptors'
    # TODO: waiting for the file...
    #specs: dict = Field(sa_column=sa.Column(JSON))
    terms: list['UTerm'] = Relationship(back_populates='data_descriptor')


class UTerm(SQLModel, PkMixin, IdMixin, table=True):
    __tablename__ = 'uterms'
    specs: dict = Field(sa_column=sa.Column(JSON))
    kind: TermKind = Field(sa_column=Column(sa.Enum(TermKind)))
    data_descriptor_pk: int | None = Field(default=None, foreign_key='data_descriptors.pk')
    data_descriptor: DataDescriptor = Relationship(back_populates='terms')


def univers_create_db():  
    engine = create_engine(settings.UNIVERS_SQLITE_URL, echo=False)
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":  
    univers_create_db()