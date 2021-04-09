from nr_events.fetchers import nr_events_id_fetcher
from nr_events.record import PublishedEventRecord


def test_nr_events_id_fetcher(app, db, base_json, taxonomy_tree):
    id_field = "control_number"
    data = base_json
    data["control_number"] = "1"
    record = PublishedEventRecord.create(data=data)
    fetched_id = nr_events_id_fetcher(record_uuid=record.id, data=data)
    assert fetched_id.pid_type == "nrevt"
    assert str(fetched_id.pid_value) == str(data[id_field])


def test_entry_points(app):
    assert 'nr_events' in app.extensions['invenio-pidstore'].fetchers.keys()
    assert 'dnrevt_fetcher' in app.extensions['invenio-pidstore'].fetchers.keys()
