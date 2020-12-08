from invenio_pidstore.models import PersistentIdentifier

from nr_events.minters import nr_events_id_minter
from tests.conftest import TestRecord


def test_nr_id_minter(app, db):
    data = {
        "title": "Test",
        "resourceType": [
            {
                "is_ancestor": False,
                "links": {
                    "self": "https://example.com/taxonomies/parent/conference-materials"
                }
            }
        ]
    }
    record = TestRecord.create(data=data)
    minted_id = nr_events_id_minter(record_uuid=record.id, data=data)
    db.session.commit()
    pids = PersistentIdentifier.query.all()
    assert data["control_number"] == "1"
    assert pids[0].pid_value == "1"
    assert pids[0].pid_type == "nrevt"


def test_entry_points(app):
    assert 'nr_events' in app.extensions['invenio-pidstore'].minters.keys()
    assert 'dnrevt_minter' in app.extensions['invenio-pidstore'].minters.keys()
