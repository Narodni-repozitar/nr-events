from invenio_records.api import Record
from nr_common.record import CanonicalUrlMixin
from oarepo_references.mixins import ReferenceEnabledRecordMixin
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin

from .constants import EVENTS_ALLOWED_SCHEMAS, EVENTS_PREFERRED_SCHEMA
from .marshmallow import EventsMetadataSchemaV1


class PublishedEventRecord(SchemaKeepingRecordMixin,
                           MarshmallowValidatedRecordMixin,
                           ReferenceEnabledRecordMixin,
                           CanonicalUrlMixin,
                           Record):
    ALLOWED_SCHEMAS = EVENTS_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = EVENTS_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = EventsMetadataSchemaV1

    @property
    def canonical_url(self):
        return self.get_canonical_url('invenio_records_rest.events_item',
                                      pid_value=self['control_number'], _external=True)
