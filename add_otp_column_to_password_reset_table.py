from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'e3d19eaa729f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add the otp column to the password_reset table
    op.add_column('password_reset', sa.Column('otp', sa.String(length=6), nullable=False, server_default=''))


def downgrade():
    # Remove the otp column from the password_reset table
    op.drop_column('password_reset', 'otp')
