"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EMBEDDING_DIM = 1024


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "folders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("folders.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.UniqueConstraint("owner_id", "name", "parent_id", name="uq_folder_owner_name_parent"),
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.UniqueConstraint("owner_id", "name", name="uq_tag_owner_name"),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("folder_id", sa.Integer(), sa.ForeignKey("folders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("venue", sa.String(500), nullable=True),
        sa.Column("doi", sa.String(255), nullable=True),
        sa.Column("semantic_scholar_id", sa.String(100), nullable=True),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("keywords", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("datasets", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("models_used", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("algorithms", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("metrics", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("problem_statement", sa.Text(), nullable=True),
        sa.Column("methodology", sa.Text(), nullable=True),
        sa.Column("results", sa.Text(), nullable=True),
        sa.Column("limitations", sa.Text(), nullable=True),
        sa.Column("conclusions", sa.Text(), nullable=True),
        sa.Column("future_work", sa.Text(), nullable=True),
        sa.Column("short_summary", sa.Text(), nullable=True),
        sa.Column("section_summaries", sa.JSON(), nullable=True),
        sa.Column("key_contributions", sa.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "status",
            sa.Enum("processing", "ready", "failed", name="document_status"),
            nullable=False,
            server_default="processing",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
    )
    op.create_index("ix_authors_name", "authors", ["name"])

    op.create_table(
        "document_authors",
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("author_order", sa.Integer(), server_default="0"),
    )

    op.create_table(
        "document_tags",
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("section", sa.String(255), nullable=True),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=True),
    )
    op.create_index("ix_chunks_document_id", "chunks", ["document_id"])
    op.execute(
        "CREATE INDEX ix_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )

    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("note", "highlight", "todo", "summary", name="note_type"), nullable=False, server_default="note"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("section_ref", sa.String(255), nullable=True),
        sa.Column("is_done", sa.Boolean(), server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notes_document_id", "notes", ["document_id"])

    op.create_table(
        "citation_relations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "relation",
            sa.Enum("cites", "cited_by", "similar", "recommended", name="citation_relation_type"),
            nullable=False,
        ),
        sa.Column("related_document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("external_paper_id", sa.String(100), nullable=True),
        sa.Column("external_title", sa.String(1000), nullable=True),
        sa.Column("external_authors", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("external_year", sa.Integer(), nullable=True),
        sa.Column("external_url", sa.String(1000), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_citation_relations_document_id", "citation_relations", ["document_id"])

    op.create_table(
        "saved_comparisons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_ids", sa.ARRAY(sa.Integer()), nullable=False),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "review_outlines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("document_ids", sa.ARRAY(sa.Integer()), nullable=False),
        sa.Column("themes", sa.JSON(), nullable=True),
        sa.Column("trends", sa.JSON(), nullable=True),
        sa.Column("gaps", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("outline", sa.JSON(), nullable=True),
        sa.Column("suggested_reading", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("review_outlines")
    op.drop_table("saved_comparisons")
    op.drop_table("citation_relations")
    op.drop_table("notes")
    op.drop_table("chunks")
    op.drop_table("document_tags")
    op.drop_table("document_authors")
    op.drop_table("authors")
    op.drop_table("documents")
    op.drop_table("tags")
    op.drop_table("folders")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS citation_relation_type")
    op.execute("DROP TYPE IF EXISTS note_type")
    op.execute("DROP TYPE IF EXISTS document_status")
