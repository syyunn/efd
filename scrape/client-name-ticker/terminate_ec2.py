import concurrent.futures


def terminate_ec2(instance_id):
    import boto3
    ec2 = boto3.resource("ec2")
    instance = ec2.Instance(instance_id)
    print(instance.terminate())


def terminate_ec2s():
    import boto3
    ec2 = boto3.resource("ec2", region_name="us-east-1")
    instance_ids = [instance.id for instance in ec2.instances.all() if instance.state['Name'] == "running"]

    while len(instance_ids) > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            executor.map(
                terminate_ec2,
                instance_ids,
            )
        instance_ids = [instance.id for instance in ec2.instances.all() if instance.state['Name'] == "running"]

    print("terminated all instances.")


if __name__ == "__main__":
    terminate_ec2s()
    pass