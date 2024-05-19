"""initial migration

Revision ID: a82a3fd10ff1
Revises: 
Create Date: 2024-05-13 10:31:04.203543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a82a3fd10ff1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    users = """
CREATE TABLE users (
    login VARCHAR PRIMARY KEY,
    wallet DECIMAL NOT NULL DEFAULT 0.0,
    email VARCHAR NOT NULL
);
"""

    examinations_results = """
CREATE TABLE examinations_results (
    id SERIAL PRIMARY KEY,
    examination_date DATE,
    analyzer VARCHAR,
    fk_user VARCHAR NOT NULL,
    leukocytes INTEGER,
    nitrite BOOLEAN,
    urobilinogen FLOAT,
    protein FLOAT,
    ph FLOAT,
    blood BOOLEAN,
    specific_gravity FLOAT,
    ascorbate FLOAT,
    ketone FLOAT,
    bilirubin FLOAT,
    glucose FLOAT,
    micro_albumin FLOAT,
    FOREIGN KEY (fk_user) REFERENCES users(login)
);
"""
    op.execute(users)
    op.execute(examinations_results)

def downgrade() -> None:
    op.execute("""DROP TABLE examinations_results;""")
    op.execute("""DROP TABLE users;""")
