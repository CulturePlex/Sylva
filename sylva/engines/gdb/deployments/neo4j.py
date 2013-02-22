import json

from boto.cloudformation import connect_to_region
from boto.exception import BotoServerError

from django.core.urlresolvers import reverse
from django.conf import settings

from engines.models import Instance
from engines.gdb.utils import generate_password


AWS_CLOUDFORMATION_REGION = getattr(settings, "AWS_CLOUDFORMATION_REGION",
                                    "us-east-1")
AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY


def deploy(request, user=None,
           instance_type=None, image_id=None, ebs_volume=None):
    user = user or request.user
    try:
        connection = connect_to_region(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_CLOUDFORMATION_REGION,
            is_secure=True,
        )
    except BotoServerError, e:
        raise Exception("Unable to connect to CloudFormation: %s"
                        % e.error_message)
    else:
        stack_name = u"sylvadb-{0}-{1}".format(user.username,
                                               generate_password(length=8))
        username = generate_password(length=14)
        password = generate_password(length=26, punctuation=True)
        activation = generate_password(length=50, punctuation=True)
        instance = Instance.objects.create(
            name=stack_name,
            username=username,
            plain_password=password,
            owner=user,
            activation=activation,
            activated=False,
        )
        reversed_url = reverse("instance_activate", args=(instance.id, ))
        web_hook = u"{0}{1}".format(request.get_host(), reversed_url)
        template = get_template(activation, instance_type, image_id,
                                ebs_volume)
        parameters = [
            ("AcceptOracleLicense", "true"),
            ("SSHKeyName", "neo4j_cert"),
            ("WebHookEndPoint", web_hook),
            ("Neo4jUserName", username),
            ("Neo4jPassword", password),
            ("AwsAvailabilityZone", AWS_CLOUDFORMATION_REGION + "d"),
        ]
        try:
            stack_id = connection.create_stack(
                stack_name=stack_name,
                template_body=template,
                template_url=None,
                parameters=parameters,
                notification_arns=[],
                disable_rollback=False,
                timeout_in_minutes=None,
                capabilities=None
            )
        except BotoServerError, e:
            raise Exception("Unable to create a CloudFormation stack '%s': %s"
                            % (stack_name, e.error_message))
        else:
            options = {
                "stack_id": stack_id
            }
            instance.options = json.dumps(options)
            instance.save()
            return instance


def get_template(activation, instance_type=None, image_id=None,
                 ebs_volume=None):
    if not instance_type:
        if settings.DEBUG:
            instance_type = "t1.micro"
        else:
            instance_type = "m1.large"
    if not image_id:
        # ubuntu-precise-12.04-amd64-server-20121218
        image_id = "ami-d726abbe"
        # Neo4j SylvaDB Public Instance, ubuntu-precise-12.04-amd64
        # image_id = "ami-6f7af906"
    if not ebs_volume:
        if settings.DEBUG:
            ebs_volume = "20"
        else:
            ebs_volume = "100"
    if settings.DEBUG:
        public_endpoint = "PublicDnsName"
    else:
        public_endpoint = "PublicIp"
    # CloudFormation template
    template = {
        "Description": "Neo4j on AWS - creates a stack and deploys Neo4j",
        "Parameters": {
            "AcceptOracleLicense": {
                "Description": "This parameter indicates that you accept the "
                               "terms of Oracle's License Agreement for Java",
                "Type": "String",
                "AllowedValues": ["true", "false"],
                "Default": "true"
            },
            "WebHookEndPoint": {
                "Description": "End point to POST the connection string after "
                               "machine is ready",
                "Type": "String"
            },
            "Neo4jUserName": {
                "Description": "Username for the Neo4j REST API",
                "Type": "String"
            },
            "Neo4jPassword": {
                "Description": "Password for the Neo4j REST API",
                "Type": "String",
                "NoEcho": "True"
            },
            "SSHKeyName": {
                "Description": "Name of the SSH key that you will use to "
                               "access the server (must be on AWS US-EAST)",
                "Type": "String",
                "Default": "NEO4J"
            },
            "AwsAvailabilityZone": {
                "Description": "Name of the AWS availability zone that you "
                               "will deploy into",
                "Type": "String",
                "AllowedValues": ["us-east-1a", "us-east-1b", "us-east-1c",
                                  "us-east-1d"],
                "Default": "us-east-1d"
            }
        },
        "Resources": {
            "Server": {
                "Type": "AWS::EC2::Instance",
                "Properties": {
                    "AvailabilityZone": {"Ref": "AwsAvailabilityZone"},
                    "DisableApiTermination": "FALSE",
                    "ImageId": image_id,
                    "InstanceType": instance_type,
                    "KeyName": {"Ref": "SSHKeyName"},
                    "Monitoring": "false",
                    "SecurityGroups": [
                        {
                            "Ref": "sgNeo4jServer"
                        }
                    ],
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "Neo4j on AWS for SylvaDB"
                        }
                    ],
                    "UserData": {"Fn::Base64": {"Fn::Join": ["", [
                        "#!/bin/bash -v\n",
                        "wget -O /var/tmp/go https://raw.github.com/neo4j-contrib/neo4j-puppet/master/go\n",
                        "chmod +x /var/tmp/go\n",
                        "sudo /var/tmp/go ", {"Ref": "AcceptOracleLicense"}, " ", {"Ref": "Neo4jUserName"}, " ", {"Ref": "Neo4jPassword"}, "\n",
                        # Template error: resource ElasticIP has missing or circular dependencies:
                        #"curl -X POST --data \"schema=", "http", "host=", {"Fn::GetAtt": ["Server", public_endpoint]}, "port=", "7474", "path=", "db/data", "activation=", activation, "\" ", {"Ref": "WebHookEndPoint"}, "\n"
                        "curl -X POST --data \"schema=", "http", "host=", "`curl http://169.254.169.254/latest/meta-data/public-ipv4`", "port=", "7474", "path=", "db/data", "activation=", activation, "\" ", {"Ref": "WebHookEndPoint"}, "\n"
                    ]]}},
                    "Volumes": [{
                        "VolumeId": {"Ref": "EBSVolume"},
                        "Device": "/dev/sdj"
                    }]
                }
            },
            "EBSVolume": {
                "Type": "AWS::EC2::Volume",
                "Properties": {
                    "AvailabilityZone": {"Ref": "AwsAvailabilityZone"},
                    "Size": ebs_volume
                }
            },
            "sgNeo4jServer": {
                "Type": "AWS::EC2::SecurityGroup",
                "Properties": {
                    "GroupDescription": "Neo4j Ports",
                    "SecurityGroupIngress": [
                        {
                            "IpProtocol": "tcp",
                            "FromPort": "22",
                            "ToPort": "22",
                            "CidrIp": "0.0.0.0/0"
                        },
                        {
                            "IpProtocol": "tcp",
                            "FromPort": "7474",
                            "ToPort": "7474",
                            "CidrIp": "0.0.0.0/0"
                        }
                    ]
                }
            }
        },
        "Outputs": {
            "Neo4jEndPoint": {
                "Value": {"Fn::Join": ["", ["http://", {"Fn::GetAtt": ["Server", public_endpoint]}, ":7474/db/data"]]},
                "Description": "This is the address of your Neo4j server, that your application will use."
            },
            "SshAccess": {
                "Value": {"Fn::Join": ["", ["ssh -i ", {"Ref": "SSHKeyName"}, ".pem -l ubuntu ", {"Fn::GetAtt": ["Server", public_endpoint]}]]},
                "Description": "This is how you gain remote access to "
                               "the machine."
            },
            "Note": {
                "Value": "Your stack is probably still building. "
                         "It takes 5-10 minutes to get Neo4j and dependencies "
                         "built.  Coffee time?",
                "Description": "Setting user expectations on timing."
            }
        },
        "AWSTemplateFormatVersion": "2010-09-09"
    }
    if public_endpoint == "PublicIp":
        template["Resources"]["ElasticIP"] = {
            "Type": "AWS::EC2::EIP",
            "Properties": {
                "InstanceId": {
                    "Ref": "Server"
                }
            }
        }
    return json.dumps(template)
