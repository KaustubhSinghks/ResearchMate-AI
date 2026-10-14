from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Folder(Base):
    __tablename__ = "folders"
    __table_args__ = (UniqueConstraint("owner_id", "name", "parent_id", name="uq_folder_owner_name_parent"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_tag_owner_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class DocumentTag(Base):
    __tablename__ = "document_tags"

    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
