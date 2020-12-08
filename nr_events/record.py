from flask import url_for
from invenio_records.api import Record
from oarepo_references.mixins import ReferenceEnabledRecordMixin
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin

from .constants import EVENTS_ALLOWED_SCHEMAS, EVENTS_PREFERRED_SCHEMA
from .marshmallow import EventsMetadataSchemaV1


class PublishedEventRecord(SchemaKeepingRecordMixin,
                           MarshmallowValidatedRecordMixin,
                           ReferenceEnabledRecordMixin,
                           Record):
    ALLOWED_SCHEMAS = EVENTS_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = EVENTS_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = EventsMetadataSchemaV1

    @property
    def canonical_url(self):
        return url_for('invenio_records_rest.events_item',
                       pid_value=self['control_number'], _external=True)
