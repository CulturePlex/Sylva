from accounts.tests import UserAccountTest
from data.tests import MediaFileTest, MediaLinkTest
from engines.tests import InstanceNeo4jTestSuite, InstanceRexsterTestSuite
from graphs.tests import GraphTest, RelationshipTest
from schemas.tests import (SchemaTest, NodePropertyTest,
    RelationshipPropertyTest, NodeTypesTest, RelationshipTypesTest)

from user import UserTestCase
from dashboard import DashboardTestCase
from schema import SchemaTestCase
from dataNode import DataNodeTestCase
