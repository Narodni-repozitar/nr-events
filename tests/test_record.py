import uuid

from future.backports.urllib.parse import urlparse

from nr_events.record import PublishedEventRecord


def test_record(app, db, base_json, taxonomy_tree):
    pid = base_json["control_number"]
    record_id = uuid.uuid4()
    record = PublishedEventRecord.create(data=base_json, id_=record_id)
    url = record.canonical_url
    prs_url = urlparse(url)
    path_array = prs_url.path.split("/")[1:]
    assert path_array[-1] == pid
    assert path_array[0] == "events"
