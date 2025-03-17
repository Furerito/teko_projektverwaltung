"""Phase status ist jetzt das selbe Enum wie in Projekt

Revision ID: 2afc93328ded
Revises: 2f0a840d1d0b
Create Date: 2025-03-09 12:46:56.634902
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '2afc93328ded'
down_revision = '2f0a840d1d0b'
branch_labels = None
depends_on = None

def upgrade():
    # 1) Statuswerte bereinigen, damit PostgreSQL sie casten kann
    op.execute("""
    UPDATE projektphase
    SET status = 'Geplant'
    WHERE status NOT IN ('Geplant','InBearbeitung','Pausiert','Abgeschlossen','Abgebrochen')
    """)

    # 2) Optional: alte Tabelle 'users' droppen (nur wenn du sie wirklich nicht mehr brauchst)
    op.drop_table('users')

    # 3) Spalte 'status' von VARCHAR auf Enum umstellen, mit postgresql_using
    with op.batch_alter_table('projektphase', schema=None) as batch_op:
        batch_op.alter_column(
            'status',
            existing_type=sa.VARCHAR(length=50),
            type_=sa.Enum('Geplant','InBearbeitung','Pausiert','Abgeschlossen','Abgebrochen',
                          name='projektstatusenum'),
            existing_nullable=False,
            postgresql_using="status::text::projektstatusenum"
        )


def downgrade():
    # 1) Spalte 'status' zurückwandeln zu VARCHAR(50)
    with op.batch_alter_table('projektphase', schema=None) as batch_op:
        batch_op.alter_column(
            'status',
            existing_type=sa.Enum('Geplant','InBearbeitung','Pausiert','Abgeschlossen','Abgebrochen',
                                  name='projektstatusenum'),
            type_=sa.VARCHAR(length=50),
            existing_nullable=False,
            postgresql_using="status::text"
        )

    # 2) Die zuvor gedroppte Tabelle 'users' wiederherstellen (falls gewünscht)
    op.create_table('users',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('username', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('password', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column('otp_secret', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.Column('two_factor_enabled', sa.BOOLEAN(), server_default=sa.text('false'),
                  autoincrement=False, nullable=True),
        sa.Column('two_factor_verified', sa.BOOLEAN(), server_default=sa.text('false'),
                  autoincrement=False, nullable=True),
        sa.Column('is_superuser', sa.BOOLEAN(), server_default=sa.text('false'),
                  autoincrement=False, nullable=True),
        sa.Column('account_locked', sa.BOOLEAN(), server_default=sa.text('false'),
                  autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='users_pkey'),
        sa.UniqueConstraint('username', name='users_username_key')
    )
