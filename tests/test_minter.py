import uuid

from invenio_pidstore.models import PersistentIdentifier

from nr_events.minters import nr_events_id_minter
from nr_events.record import PublishedEventRecord


def test_nr_events_id_minter(app, db, base_json, taxonomy_tree):
    data = base_json
    del data["control_number"]
    record_uuid = uuid.uuid4()
    minted_id = nr_events_id_minter(record_uuid=record_uuid, data=data)
    print("\n\nminted_id: ", minted_id)
    record = PublishedEventRecord.create(data=data, id_=record_uuid)
    print("\n\nRECORD: ", record)
    db.session.commit()
    pids = PersistentIdentifier.query.all()
    assert data["control_number"] == "1"
    assert pids[0].pid_value == "1"
    assert pids[0].pid_type == "nrevt"
    assert record["control_number"] == "1"


def test_entry_points(app):
    assert 'nr_events' in app.extensions['invenio-pidstore'].minters.keys()
    assert 'dnrevt_minter' in app.extensions['invenio-pidstore'].minters.keys()
