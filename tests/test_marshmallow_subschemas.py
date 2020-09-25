from nr_events.marshmallow.subschemas import Events


class TestEventsSchema:
    def test_schema_1(self, app, db, taxonomy_tree, base_json, base_json_dereferenced, base_event,
                      base_event_dereferenced):
        test_schema = Events()

        result = test_schema.load(base_event)
        assert result == base_event_dereferenced
