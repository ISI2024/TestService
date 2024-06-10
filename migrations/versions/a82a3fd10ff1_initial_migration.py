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
    login VARCHAR(50) PRIMARY KEY CHECK (LENGTH(login) > 1),
    wallet DECIMAL NOT NULL DEFAULT 0.0 CHECK (wallet >= 0),
    email VARCHAR(50) NOT NULL CHECK (LENGTH(email) > 1)
);
"""

    examinations_results = """
CREATE TABLE examinations_results (
    id SERIAL PRIMARY KEY,
    examination_date DATE,
    analyzer VARCHAR(50) CHECK (LENGTH(analyzer) > 1),
    fk_user VARCHAR NOT NULL,
    leukocytes VARCHAR(50) CHECK (LENGTH(leukocytes) > 1),
    nitrite VARCHAR(50) CHECK (LENGTH(nitrite) > 1),
    urobilinogen VARCHAR(50) CHECK (LENGTH(urobilinogen) > 1),
    protein VARCHAR(50) CHECK (LENGTH(protein) > 1),
    ph VARCHAR(50) CHECK (LENGTH(ph) > 1),
    blood VARCHAR(50) CHECK (LENGTH(blood) > 1),
    specific_gravity VARCHAR(50) CHECK (LENGTH(specific_gravity) > 1),
    ascorbate VARCHAR(50) CHECK (LENGTH(ascorbate) > 1),
    ketone VARCHAR(50) CHECK (LENGTH(ketone) > 1),
    bilirubin VARCHAR(50) CHECK (LENGTH(bilirubin) > 1),
    glucose VARCHAR(50) CHECK (LENGTH(glucose) > 1),
    micro_albumin VARCHAR(50) CHECK (LENGTH(micro_albumin) > 1),
    FOREIGN KEY (fk_user) REFERENCES users(login)
);
"""
    op.execute(users)
    op.execute(examinations_results)

def downgrade() -> None:
    op.execute("""DROP TABLE examinations_results;""")
    op.execute("""DROP TABLE users;""")
