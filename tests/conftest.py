from __future__ import absolute_import, print_function

import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import pytest
from flask import Flask, make_response, url_for
from flask_login import LoginManager, login_user
from flask_principal import RoleNeed, Principal, Permission
from flask_taxonomies.proxies import current_flask_taxonomies
from flask_taxonomies.term_identification import TermIdentification
from invenio_access import InvenioAccess
from invenio_accounts import InvenioAccounts
from invenio_accounts.models import User
from invenio_base.signals import app_loaded
from invenio_celery import InvenioCelery
from invenio_db import InvenioDB
from invenio_db import db as db_
from invenio_indexer import InvenioIndexer
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import InvenioJSONSchemas
from invenio_pidstore import InvenioPIDStore
from invenio_pidstore.providers.recordid import RecordIdProvider
from invenio_records import InvenioRecords, Record
from invenio_records_rest import InvenioRecordsREST
from invenio_records_rest.schemas.fields import SanitizedUnicode
from invenio_records_rest.utils import PIDConverter
from invenio_records_rest.views import create_blueprint_from_app
from invenio_search import InvenioSearch, RecordsSearch
from marshmallow import Schema
from oarepo_mapping_includes.ext import OARepoMappingIncludesExt
from oarepo_records_draft.ext import RecordsDraft
from oarepo_references import OARepoReferences
from oarepo_references.mixins import ReferenceEnabledRecordMixin
from oarepo_taxonomies.cli import init_db
from oarepo_taxonomies.ext import OarepoTaxonomies
from oarepo_validate import MarshmallowValidatedRecordMixin
from sqlalchemy_utils import database_exists, create_database, drop_database

# from invenio_nusl_theses import InvenioNUSLTheses
from tests.helpers import set_identity


class TestSchema(Schema):
    """Test record schema."""
    title = SanitizedUnicode()
    control_number = SanitizedUnicode()


class TestRecord(MarshmallowValidatedRecordMixin,
                 ReferenceEnabledRecordMixin,
                 Record):
    """Reference enabled test record class."""
    MARSHMALLOW_SCHEMA = TestSchema
    VALIDATE_MARSHMALLOW = True
    VALIDATE_PATCH = True

    @property
    def canonical_url(self):
        # SERVER_NAME = current_app.config["SERVER_NAME"]
        # return f"http://{SERVER_NAME}/api/records/{self['pid']}"
        return url_for('invenio_records_rest.recid_item',
                       pid_value=self['pid'], _external=True)


RECORDS_REST_ENDPOINTS = {
    'recid': dict(
        pid_type='nusl',
        pid_minter='nsul',
        pid_fetcher='nusl',
        default_endpoint_prefix=True,
        search_class=RecordsSearch,
        indexer_class=RecordIndexer,
        search_index='records',
        search_type=None,
        record_serializers={
            'application/json': 'oarepo_validate:json_response',
        },
        search_serializers={
            'application/json': 'oarepo_validate:json_search',
        },
        record_loaders={
            'application/json': 'oarepo_validate:json_loader',
        },
        record_class=TestRecord,
        list_route='/records/',
        item_route='/records/<pid(nusl):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        error_handlers=dict()
    )
}


@pytest.yield_fixture(scope="class")
def app():
    instance_path = tempfile.mkdtemp()
    app = Flask('testapp', instance_path=instance_path)

    app.config.update(
        JSONSCHEMAS_HOST="nusl.cz",
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        SERVER_NAME='127.0.0.1:5000',
        INVENIO_INSTANCE_PATH=instance_path,
        DEBUG=True,
        # in tests, api is not on /api but directly in the root
        PIDSTORE_RECID_FIELD='pid',
        FLASK_TAXONOMIES_URL_PREFIX='/2.0/taxonomies/',
        # RECORDS_REST_ENDPOINTS=RECORDS_REST_ENDPOINTS,
        CELERY_BROKER_URL='amqp://guest:guest@localhost:5672//',
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND='cache',
        CELERY_CACHE_BACKEND='memory',
        CELERY_TASK_EAGER_PROPAGATES=True,
        SUPPORTED_LANGUAGES=["cs", "en"],
        RECORDS_REST_ENDPOINTS=RECORDS_REST_ENDPOINTS
    )

    app.secret_key = 'changeme'
    print(os.environ.get("INVENIO_INSTANCE_PATH"))

    InvenioDB(app)
    OarepoTaxonomies(app)
    OARepoReferences(app)
    InvenioAccounts(app)
    InvenioAccess(app)
    Principal(app)
    InvenioJSONSchemas(app)
    InvenioSearch(app)
    InvenioIndexer(app)
    OARepoMappingIncludesExt(app)
    InvenioRecords(app)
    InvenioRecordsREST(app)
    InvenioCelery(app)
    # InvenioNUSLTheses(app)
    InvenioPIDStore(app)
    # Invenio Records Draft initialization
    RecordsDraft(app)
    app.url_map.converters['pid'] = PIDConverter

    # Celery
    print(app.config["CELERY_BROKER_URL"])

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def basic_user_loader(user_id):
        user_obj = User.query.get(int(user_id))
        return user_obj

    app.register_blueprint(create_blueprint_from_app(app))

    @app.route('/test/login/<int:id>', methods=['GET', 'POST'])
    def test_login(id):
        print("test: logging user with id", id)
        response = make_response()
        user = User.query.get(id)
        login_user(user)
        set_identity(user)
        return response

    # app.extensions['invenio-search'].mappings["test"] = mapping
    # app.extensions["invenio-jsonschemas"].schemas["test"] = schema

    app_loaded.send(app, app=app)

    with app.app_context():
        # app.register_blueprint(taxonomies_blueprint)
        print(app.url_map)
        yield app

    shutil.rmtree(instance_path)


@pytest.fixture(scope="class")
def db(app):
    """Create database for the tests."""
    dir_path = os.path.dirname(__file__)
    parent_path = str(Path(dir_path).parent)
    db_path = os.environ.get('SQLALCHEMY_DATABASE_URI', f'sqlite:////{parent_path}/database.db')
    os.environ["INVENIO_SQLALCHEMY_DATABASE_URI"] = db_path
    app.config.update(
        SQLALCHEMY_DATABASE_URI=db_path
    )
    if database_exists(str(db_.engine.url)):
        drop_database(db_.engine.url)
    if not database_exists(str(db_.engine.url)):
        create_database(db_.engine.url)
    db_.create_all()
    subprocess.run(["invenio", "taxonomies", "init"])
    runner = app.test_cli_runner()
    result = runner.invoke(init_db)
    if result.exit_code:
        print(result.output, file=sys.stderr)
    assert result.exit_code == 0
    yield db_

    # Explicitly close DB connection
    db_.session.close()
    db_.drop_all()


@pytest.fixture
def client(app, db):
    from flask_taxonomies.models import Base
    Base.metadata.create_all(db.engine)
    return app.test_client()


@pytest.fixture
def permission_client(app, db):
    app.config.update(
        FLASK_TAXONOMIES_PERMISSION_FACTORIES={
            'taxonomy_create': [Permission(RoleNeed('admin'))],
            'taxonomy_update': [Permission(RoleNeed('admin'))],
            'taxonomy_delete': [Permission(RoleNeed('admin'))],

            'taxonomy_term_create': [Permission(RoleNeed('admin'))],
            'taxonomy_term_update': [Permission(RoleNeed('admin'))],
            'taxonomy_term_delete': [Permission(RoleNeed('admin'))],
            'taxonomy_term_move': [Permission(RoleNeed('admin'))],
        }
    )
    from flask_taxonomies.models import Base
    Base.metadata.create_all(db.engine)
    return app.test_client()


@pytest.fixture
def tax_url(app):
    url = app.config['FLASK_TAXONOMIES_URL_PREFIX']
    if not url.endswith('/'):
        url += '/'
    return url


@pytest.fixture(scope="class")
def taxonomy(app, db):
    taxonomy = current_flask_taxonomies.create_taxonomy("test_taxonomy", extra_data={
        "title":
            {
                "cs": "test_taxonomy",
                "en": "test_taxonomy"
            }
    })
    db.session.commit()
    return taxonomy


@pytest.fixture(scope="class")
def taxonomy_tree(app, db, taxonomy):
    # accessRights
    id1 = TermIdentification(taxonomy=taxonomy, slug="c_abf2")
    term1 = current_flask_taxonomies.create_term(id1, extra_data={
        "title": {
            "cs": "otevřený přístup",
            "en": "open access"
        },
        "relatedURI": {
            "coar": "http://purl.org/coar/access_right/c_abf2",
            "vocabs": "https://vocabs.acdh.oeaw.ac.at/archeaccessrestrictions/public",
            "eprint": "http://purl.org/eprint/accessRights/OpenAccess"
        }
    })

    # resource type
    id2 = TermIdentification(taxonomy=taxonomy, slug="bakalarske_prace")
    term2 = current_flask_taxonomies.create_term(id2, extra_data={
        "title": {
            "cs": "Bakalářské práce",
            "en": "Bachelor’s theses"
        }
    })

    # institution
    id3 = TermIdentification(taxonomy=taxonomy, slug="61384984")
    term3 = current_flask_taxonomies.create_term(id3, extra_data={
        "title": {
            "cs": "Akademie múzických umění v Praze",
            "en": "Academy of Performing Arts in Prague"
        },
        "type": "veřejná VŠ",
        "aliases": ["AMU"],
        "related": {
            "rid": "51000"
        },
        "address": "Malostranské náměstí 259/12, 118 00 Praha 1",
        "ico": "61384984",
        "url": "https://www.amu.cz",
        "provider": True,
    })

    # language
    id4 = TermIdentification(taxonomy=taxonomy, slug="cze")
    term4 = current_flask_taxonomies.create_term(id4, extra_data={
        "title": {
            "cs": "čeština",
            "en": "Czech"
        }
    })

    # contributor
    id5 = TermIdentification(taxonomy=taxonomy, slug="supervisor")
    term5 = current_flask_taxonomies.create_term(id5, extra_data={
        "title": {
            "cs": "supervizor",
            "en": "supervisor"
        },
        "dataCiteCode": "Supervisor"
    })

    # funder
    id6 = TermIdentification(taxonomy=taxonomy, slug="ntk")
    term6 = current_flask_taxonomies.create_term(id6, extra_data={
        "title": {
            "cs": "Národní technická knihovna",
            "en": "National library of technology"
        },
        "funderISVaVaICode": "123456789"
    })

    # country
    id7 = TermIdentification(taxonomy=taxonomy, slug="cz")
    term7 = current_flask_taxonomies.create_term(id7, extra_data={
        "title": {
            "cs": "Česko",
            "en": "Czechia"
        },
        "code": {
            "number": "203",
            "alpha2": "CZ",
            "alpha3": "CZE"
        }
    })

    # relationship
    id8 = TermIdentification(taxonomy=taxonomy, slug="isversionof")
    term8 = current_flask_taxonomies.create_term(id8, extra_data={
        "title": {
            "cs": "jeVerzí",
            "en": "isVersionOf"
        }
    })

    # rights
    id9 = TermIdentification(taxonomy=taxonomy, slug="copyright")
    term9 = current_flask_taxonomies.create_term(id9, extra_data={
        "title": {
            "cs": "Dílo je chráněno podle autorského zákona č. 121/2000 Sb.",
            "en": "This work is protected under the Copyright Act No. 121/2000 Coll."
        }
    })

    # series
    id9 = TermIdentification(taxonomy=taxonomy, slug="maj")
    term9 = current_flask_taxonomies.create_term(id9, extra_data={
        "name": "maj",
        "volume": "1"
    })

    # subject
    id10 = TermIdentification(taxonomy=taxonomy, slug="psh3001")
    term10 = current_flask_taxonomies.create_term(id10, extra_data={
        "title": {
            "cs": "Reynoldsovo číslo",
            "en": "Reynolds number"
        },
        "reletedURI": ["http://psh.techlib.cz/skos/PSH3001"],
        "DateRevised": "2007-01-26T16:14:37"
    })

    id11 = TermIdentification(taxonomy=taxonomy, slug="psh3000")
    term11 = current_flask_taxonomies.create_term(id11, extra_data={
        "title": {
            "cs": "turbulentní proudění",
            "en": "turbulent flow"
        },
        "reletedURI": ["http://psh.techlib.cz/skos/PSH3000"],
        "DateRevised": "2007-01-26T16:14:37"
    })

    id12 = TermIdentification(taxonomy=taxonomy, slug="D010420")
    term12 = current_flask_taxonomies.create_term(id12, extra_data={
        "title": {
            "cs": "pentany",
            "en": "Pentanes"
        },
        "reletedURI": ["http://www.medvik.cz/link/D010420", "http://id.nlm.nih.gov/mesh/D010420"],
        "DateRevised": "2007-01-26T16:14:37",
        "DateCreated": "2007-01-26T16:14:37",
        "DateDateEstablished": "2007-01-26T16:14:37",
    })

    # studyField
    id13 = TermIdentification(taxonomy=taxonomy, slug="O_herectvi-alternativniho-divadla")
    term13 = current_flask_taxonomies.create_term(id13, extra_data={
        "title": {
            "cs": "Herectví alternativního divadla",
        },
        "AKVO": "8203R082"
    })

    # conference
    id14 = TermIdentification(taxonomy=taxonomy, slug="cze_conference")
    term14 = current_flask_taxonomies.create_term(id14, extra_data={
        "title": {
            "cs": "Česká konference",
            "en": "Czech conference"
        },
    })

    db.session.commit()


def get_pid():
    """Generates a new PID for a record."""
    record_uuid = uuid.uuid4()
    provider = RecordIdProvider.create(
        object_type='rec',
        object_uuid=record_uuid,
    )
    return record_uuid, provider.pid.pid_value


@pytest.fixture()
def base_json():
    return {
        "accessRights": [{
            "is_ancestor": False,
            "links": {
                "self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/c-abf2"
            }
        }],

        "control_number": "411100",
        "creator": [
            {
                "name": "Daniel Kopecký"
            }
        ],
        "dateIssued": "2010-07-01",
        "keywords": [
            {"cs": "1", "en": "1"},
            {"cs": "2", "en": "2"},
            {"cs": "3", "en": "3"},
        ],
        "language": [
            {
                "is_ancestor": False,
                "links": {
                    "self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cze"
                }
            }
        ],
        "provider": [
            {
                "is_ancestor": False,
                "links": {
                    "self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/61384984"
                }
            }
        ],
        "resourceType": [
            {
                "is_ancestor": False,
                "links": {
                    "self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/bakalarske-prace"
                }
            }
        ],
        "title": [{
            "cs": "Testovací záznam",
            "en": "Test record"
        }]
    }


@pytest.fixture()
def base_json_dereferenced():
    return {
        'accessRights': [{
            'is_ancestor': False,
            'links': {
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/c-abf2'
            },
            'relatedURI': {
                'coar': 'http://purl.org/coar/access_right/c_abf2',
                'eprint': 'http://purl.org/eprint/accessRights/OpenAccess',
                'vocabs':
                    'https://vocabs.acdh.oeaw.ac.at/archeaccessrestrictions/public'
            },
            'title': {'cs': 'otevřený přístup', 'en': 'open access'}
        }],
        'control_number': '411100',
        'creator': [{'name': 'Daniel Kopecký'}],
        'dateIssued': '2010-07-01',
        'keywords': [{'cs': '1', 'en': '1'},
                     {'cs': '2', 'en': '2'},
                     {'cs': '3', 'en': '3'}],
        'language': [{
            'is_ancestor': False,
            'links': {
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cze'
            },
            'title': {'cs': 'čeština', 'en': 'Czech'}
        }],
        'provider': [{
            'address': 'Malostranské náměstí 259/12, 118 00 Praha 1',
            'aliases': ['AMU'],
            'ico': '61384984',
            'is_ancestor': False,
            'links': {
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/61384984'
            },
            'provider': True,
            'related': {'rid': '51000'},
            'title': {
                'cs': 'Akademie múzických umění v Praze',
                'en': 'Academy of Performing Arts in Prague'
            },
            'type': 'veřejná VŠ',
            'url': 'https://www.amu.cz'
        }],
        'resourceType': [{
            'is_ancestor': False,
            'links': {
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/bakalarske-prace'
            },
            'title': {
                'cs': 'Bakalářské práce',
                'en': 'Bachelor’s theses'
            }
        }],
        'title': [{'cs': 'Testovací záznam', 'en': 'Test record'}]
    }


@pytest.fixture()
def base_event():
    return {
        "nameOriginal": {
            "cs": "Česká konference 2020",
            "en": "Czech conference 2020"
        },
        "nameAlternate": [{
            "cs": "Konference Česka 2020",
            "en": "Conference of Czechia 2020"
        }],
        "nameUnified": [{
            "links": {
                "self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cze-conference"
            }
        }],
        "date": "2019-12-23/2019-12-24",
        "location": {
            "place": "Prague",
            "country": [{
                "links": {
                    "self": "http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cz"
                }
            }]
        }
    }


@pytest.fixture()
def base_event_dereferenced():
    return {
        'date': '2019-12-23/2019-12-24',
        'location': {
            'country': [{
                'code': {
                    'alpha2': 'CZ',
                    'alpha3': 'CZE',
                    'number': '203'
                },
                'is_ancestor': False,
                'links': {
                    'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cz'
                },
                'title': {'cs': 'Česko', 'en': 'Czechia'}
            }],
            'place': 'Prague'
        },
        'nameAlternate': [{
            'cs': 'Konference Česka 2020',
            'en': 'Conference of Czechia 2020'
        }],
        'nameOriginal': {'cs': 'Česká konference 2020', 'en': 'Czech conference 2020'},
        'nameUnified': [{
            'is_ancestor': False,
            'links': {
                'self': 'http://127.0.0.1:5000/2.0/taxonomies/test_taxonomy/cze-conference'
            },
            'title': {
                'cs': 'Česká konference',
                'en': 'Czech conference'
            }
        }]
    }