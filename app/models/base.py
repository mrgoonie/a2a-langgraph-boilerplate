import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator

# Custom UUID type for consistent handling
class GUID(TypeDecorator):
    """
Platform-independent GUID type.

Uses PostgreSQL's UUID type, otherwise uses
VARCHAR(36), storing as stringified hex values.
"""
    impl = UUID
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value).hex
            else:
                return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value

# Helper function to generate UUIDs
def generate_uuid():
    return uuid.uuid4()

Base = declarative_base()
