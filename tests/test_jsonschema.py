from invenio_jsonschemas import current_jsonschemas
from invenio_records.api import _records_state
from marshmallow import pprint


def test_json(app, base_json, base_event):
    print("\n\n\n\n\n")
    print("START")
    print(app)
    print(current_jsonschemas.list_schemas())
    base_json["events"] = [base_event]
    _records_state.validate(base_json, "https://nusl.cz/schemas/nr_events/nr-events-v1.0.0.json")