from octopus.aws.ec2 import EC2Manager
import boto3

def create_ec2s(num_instances):
    # create instances
    ec2m = EC2Manager() # env should include private_key_path
    ec2m.create_instances(
        instance_type="t2.micro",
        image_id='ami-07ba55ee4d4622f6f',
        max_count=num_instances,
        region_name="us-east-1",
        availability_zone="us-east-1a",
        name="efd-client-ticker",
        security_group_ids=["sg-02d751916ed2ede41"],
        keyname="octo-suyeol",  # fname of the .pem,
    )

    ec2 = boto3.resource("ec2", region_name="us-east-1")
    instance_ids = [instance.id for instance in ec2.instances.all() if instance.state['Name'] == "running"]

    while len(instance_ids) < num_instances:
        instance_ids = [instance.id for instance in ec2.instances.all() if instance.state['Name'] == "running"]
        print("current ec2#:", len(instance_ids), "keep creating..")

    print("created: ", len(instance_ids), instance_ids)
    return instance_ids


if __name__ == "__main__":
    num_instances = 1
    create_ec2s(num_instances=num_instances)
    pass