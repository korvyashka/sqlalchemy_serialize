import unittest

from sqlalchemy_serializer.session import create_session, engine
from sqlalchemy_serializer import metadata

from .models import Guild
from .serializers import (
    GuildSimpleSerializer, GuildCustomSerializer,
    GuildHybridSerializer, gold_and_level,
    GuildModelSerializer, GuildModelSerializerOffHybrid
)


class BaseTest(unittest.TestCase):
    def setUp(self):
        metadata.create_all(engine)

    def tearDown(self):
        metadata.drop_all(engine)


class TestSerializer(BaseTest):
    def test_common_fields(self):
        with create_session() as session:
            acc1 = Guild(
                name='test1',
                max_members=2
            )
            acc2 = Guild(
                name='test2',
                max_members=2
            )

            session.add(acc1)
            session.add(acc2)
            session.commit()

            serializer = GuildSimpleSerializer()

            data = session.query(
                *serializer.get_query_fields()
            ).all()

            serialized = map(serializer.to_dict, data)
            self.assertIn(acc1.to_dict(), serialized)
            self.assertIn(acc2.to_dict(), serialized)

    def test_extra_fields(self):
        with create_session() as session:
            acc1 = Guild(
                name='test1',
                max_members=1
            )
            acc2 = Guild(
                name='test2',
                max_members=4
            )

            session.add(acc1)
            session.add(acc2)
            session.commit()

            serializer = GuildSimpleSerializer(
                extra_fields=[
                    (Guild.max_members == 1).label('single_guild')
                ]
            )
            data = session.query(
                *serializer.get_query_fields()
            ).all()

            serialized = map(serializer.to_dict, data)
            acc1_dict = acc1.to_dict()
            acc1_dict['single_guild'] = True
            acc2_dict = acc2.to_dict()
            acc2_dict['single_guild'] = False
            self.assertIn(acc1_dict, serialized)
            self.assertIn(acc1_dict, serialized)

    def test_hybrid_fields(self):
        with create_session() as session:
            acc2 = Guild(
                name='test2',
                max_members=4
            )

            session.add(acc2)
            session.commit()

            serializer = GuildHybridSerializer()
            data = session.query(
                *serializer.get_query_fields()
            ).first()

            serialized = serializer.to_dict(data)
            acc2_dict = acc2.to_dict_with_hybrid()
            self.assertEqual(acc2_dict, serialized)

    def test_custom_fields(self):
        with create_session() as session:
            acc2 = Guild(
                name='test2',
                max_members=4
            )

            session.add(acc2)
            session.commit()

            serializer = GuildCustomSerializer()
            data = session.query(
                *serializer.get_query_fields()
            ).first()

            serialized = serializer.to_dict(data)
            acc2_dict = acc2.to_dict()

            acc2_dict['gold_and_level'] = gold_and_level(acc2_dict)
            self.assertEqual(acc2_dict, serialized)
    # test extra_hybrid
    # test join
    # test serialize field in Serializator class


class TestModelSerializer(BaseTest):
    def test_model_serializer(self):
        with create_session() as session:
            acc1 = Guild(
                name='test1',
                max_members=2
            )
            acc2 = Guild(
                name='test2',
                max_members=2
            )

            session.add(acc1)
            session.add(acc2)
            session.commit()

            serializer = GuildModelSerializer()

            # Test with get fields
            data = session.query(
                *serializer.get_query_fields()
            ).all()

            serialized = map(serializer.to_dict, data)
            self.assertIn(acc1.to_dict_with_hybrid(), serialized)
            self.assertIn(acc2.to_dict_with_hybrid(), serialized)

            # Test with model query
            data = session.query(Guild).all()

            serialized = map(serializer.to_dict, data)
            self.assertIn(acc1.to_dict_with_hybrid(), serialized)
            self.assertIn(acc2.to_dict_with_hybrid(), serialized)

    def test_model_serializer_off_hybrid_inspection(self):
        with create_session() as session:
            acc1 = Guild(
                name='test1',
                max_members=2
            )
            acc2 = Guild(
                name='test2',
                max_members=2
            )

            session.add(acc1)
            session.add(acc2)
            session.commit()

            serializer = GuildModelSerializer(to_inspect_fields=False)

            # Test with get fields
            data = session.query(
                Guild
            ).all()

            serialized = map(serializer.to_dict, data)
            acc1_dict = acc1.to_dict()
            acc1_dict['is_rich'] = False
            acc2_dict = acc2.to_dict()
            acc2_dict['is_rich'] = False
            self.assertIn(acc1_dict, serialized)
            self.assertIn(acc2_dict, serialized)

            serializer = GuildModelSerializerOffHybrid()

            # Test with get fields
            data = session.query(
                Guild
            ).all()

            serialized = map(serializer.to_dict, data)
            self.assertIn(acc1.to_dict(), serialized)
            self.assertIn(acc2.to_dict(), serialized)
    # test with simple fields switched off inspection
    # test hybrid fields without label

if __name__ == '__main__':
    unittest.main()
