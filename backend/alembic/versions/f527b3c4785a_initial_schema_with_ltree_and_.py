"""initial_schema_with_ltree_and_partitioning

Revision ID: f527b3c4785a
Revises: 
Create Date: 2025-12-23 09:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f527b3c4785a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS ltree')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # 2. Create Questions Table
    op.create_table('questions',
        sa.Column('question_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=False),
        sa.Column('content_stem', sa.Text(), nullable=False),
        sa.Column('content_metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
        sa.Column('answer_key', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('difficulty_index', sa.Float(), server_default='0.5', nullable=True),
        sa.Column('discrimination', sa.Float(), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=True),
        sa.Column('status', sa.String(length=20), server_default='draft', nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('question_id'),
        sa.CheckConstraint("question_type IN ('mcq', 'short_answer', 'essay', 'matching')", name='check_question_type'),
        sa.CheckConstraint("status IN ('draft', 'review_pending', 'active', 'flagged', 'archived')", name='check_status'),
        sa.CheckConstraint("difficulty_index BETWEEN 0 AND 1", name='check_difficulty')
    )
    op.create_index('idx_questions_status', 'questions', ['status'])
    op.create_index('idx_questions_difficulty', 'questions', ['difficulty_index'])

    # 3. Create Curriculum Nodes (Ltree)
    op.create_table('curriculum_nodes',
        sa.Column('node_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('path', sa.types.UserDefinedType(name='ltree'), nullable=False), # Custom Type
        sa.Column('standard_code', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('node_id')
    )
    op.create_index('curriculum_path_gist_idx', 'curriculum_nodes', ['path'], postgresql_using='gist')
    op.create_index('curriculum_path_idx', 'curriculum_nodes', ['path'], unique=True)

    # 4. Create Tags Table
    op.create_table('tags',
        sa.Column('tag_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('tag_type', sa.String(length=50), nullable=False),
        sa.Column('parent_tag_id', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
        sa.ForeignKeyConstraint(['parent_tag_id'], ['tags.tag_id'], ),
        sa.PrimaryKeyConstraint('tag_id'),
        sa.CheckConstraint("tag_type IN ('concept', 'cognitive_level', 'source', 'skill', 'custom')", name='check_tag_type')
    )

    # 5. Junction Tables
    op.create_table('question_tags',
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), server_default='1.0', nullable=True),
        sa.Column('auto_tagged', sa.Boolean(), server_default='False', nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.question_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.tag_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('question_id', 'tag_id')
    )

    op.create_table('question_curriculum',
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('node_id', sa.Integer(), nullable=False),
        sa.Column('relevance_score', sa.Float(), server_default='1.0', nullable=True),
        sa.ForeignKeyConstraint(['node_id'], ['curriculum_nodes.node_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.question_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('question_id', 'node_id')
    )

    # 6. Attempt Logs (Partitioned)
    # Note: Alembic doesn't natively support creating partitioned tables easily via standard DDL objects yet in some versions,
    # so we use op.execute logic for the master table and partitions.
    
    op.execute("""
        CREATE TABLE attempt_logs (
            log_id BIGSERIAL,
            user_id UUID NOT NULL,
            question_id UUID REFERENCES questions(question_id),
            quiz_session_id UUID,
            response_data JSONB NOT NULL,
            is_correct BOOLEAN NOT NULL,
            score FLOAT NOT NULL,
            time_taken_ms INTEGER,
            device_info JSONB,
            attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            PRIMARY KEY (log_id, attempted_at)
        ) PARTITION BY RANGE (attempted_at);
    """)

    # Create initial partition for 2025
    op.execute("""
        CREATE TABLE attempt_logs_2025_01 PARTITION OF attempt_logs
        FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
    """)
    
    op.execute("CREATE INDEX idx_logs_user_question ON attempt_logs(user_id, question_id)")
    op.execute("CREATE INDEX idx_logs_attempted_at ON attempt_logs(attempted_at)")

    # 7. Versioning Trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION update_question_version()
        RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.content_stem != NEW.content_stem OR OLD.answer_key != NEW.answer_key THEN
                NEW.version = OLD.version + 1;
                NEW.updated_at = NOW();
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER question_version_trigger
        BEFORE UPDATE ON questions
        FOR EACH ROW EXECUTE FUNCTION update_question_version();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS question_version_trigger ON questions")
    op.execute("DROP FUNCTION IF EXISTS update_question_version")
    op.execute("DROP TABLE IF EXISTS attempt_logs_2025_01") 
    op.execute("DROP TABLE IF EXISTS attempt_logs")
    op.drop_table('question_curriculum')
    op.drop_table('question_tags')
    op.drop_table('tags')
    op.drop_table('curriculum_nodes')
    op.drop_table('questions')
    op.execute('DROP EXTENSION IF EXISTS ltree')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
