import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator, String

# Custom UUID type for consistent handling
class GUID(TypeDecorator):
    """
Platform-independent GUID type.

Uses PostgreSQL's UUID type, otherwise uses
VARCHAR(36), storing as stringified hex values.
"""
    impl = String(36)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(str(value))
            return value
        else:
            # For SQLite and other dialects, convert to string
            if not isinstance(value, uuid.UUID):
                try:
                    value = uuid.UUID(str(value))
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid UUID value: {value}")
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            # For SQLite and other dialects, we get back a string
            if not isinstance(value, uuid.UUID):
                try:
                    value = uuid.UUID(value)
                except (ValueError, TypeError):
                    return value
            return value

# Helper function to generate UUIDs
def generate_uuid():
    return uuid.uuid4()

Base = declarative_base()
