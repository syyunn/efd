from octopus.aws.ec2 import EC2Manager
import concurrent.futures


def create_ec2s(expected_num_instances):
    # create instances
    ec2m = EC2Manager()
    instance_ids = ec2m.create_instances(
        instance_type="t2.micro",
        # image_id="ami-0ab6b4313021f7163",
        # image_id="ami-0166532ac78b7d5e0",
        image_id='ami-0071129ccb8fbc15a',
        max_count=expected_num_instances,
        region_name="ap-northeast-2",
        availability_zone="ap-northeast-2c",
        name="disam-clients-by-requests",
        security_group_ids=["sg-0800b788931857e3e"],
        keyname="lv-suyeol-aws",  # fname of the .pem # 
    )
    print("created: ", len(instance_ids), instance_ids)


def terminate_ec2(instance_id):
    import boto3
    ec2 = boto3.resource("ec2")
    instance = ec2.Instance(instance_id)
    print(instance.terminate())


def terminate_ec2s():
    # terminate all instances in the default region
    import boto3

    ec2 = boto3.resource("ec2")
    instance_ids = [instance.id for instance in ec2.instances.all()]
    ec2 = boto3.resource("ec2")

    for id in instance_ids:
        instance = ec2.Instance(id)
        print(instance.terminate())


if __name__ == "__main__":
    num = 1
    create_ec2s(num)
    # terminate_ec2s()

    import boto3
    ec2 = boto3.resource("ec2")
    instance_ids = [instance.id for instance in ec2.instances.all() if instance.state['Name'] == "running"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(instance_ids)) as executor:
        executor.map(
            terminate_ec2,
            instance_ids,
        )