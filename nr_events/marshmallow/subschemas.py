from nr_common.marshmallow.fields import DateRange
from nr_common.marshmallow.subschemas import TitledMixin, PublicationPlaceSchema
from invenio_records_rest.schemas import StrictKeysMixin
from marshmallow.fields import List, Nested
from oarepo_multilingual.marshmallow import MultilingualStringV2
from oarepo_taxonomies.marshmallow import TaxonomyField


class Events(StrictKeysMixin):
    nameOriginal = MultilingualStringV2(required=True)
    nameAlternate = List(MultilingualStringV2())
    nameUnified = TaxonomyField(mixins=[TitledMixin])
    date = DateRange(required=True)
    location = Nested(PublicationPlaceSchema())
