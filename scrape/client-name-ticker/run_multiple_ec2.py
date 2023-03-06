import concurrent.futures

from octopus.aws.ec2 import EC2Manager
from octopus.db import PostgresqlManager

from dotenv import load_dotenv
import boto3

def create_ec2s(num_instances, timeout=60):
    import time

    start = time.time()
    elapsed = 0

    # create instances
    ec2m = EC2Manager() # this should include private_key_path
    ec2m.create_instances(
        instance_type="t2.micro",
        image_id='ami-07ba55ee4d4622f6f',
        max_count=num_instances,
        region_name="us-east-1",
        availability_zone="us-east-1b",
        name="efd-client-ticker",
        security_group_ids=["sg-02d751916ed2ede41"],
        keyname="octo-suyeol",  # fname of the .pem,
    )

    ec2 = boto3.resource("ec2", region_name="us-east-1")
    instance_ids = [instance.id for instance in ec2.instances.all() if instance.state['Name'] == "running"]

    while len(instance_ids) < num_instances and elapsed < timeout:
        instance_ids = [instance.id for instance in ec2.instances.all() if instance.state['Name'] == "running"]
        print("current ec2#:", len(instance_ids), "keep creating..")
        end = time.time()
        elapsed = end - start
        print(elapsed)                
    print("created: ", len(instance_ids), instance_ids)
    return instance_ids

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


def check_how_many_left():
    sql_check_how_many_left = """
    select count(*) from _sandbox_suyeol.client_ticker ct 
    where ticker is null
    """
    load_dotenv("/Users/syyun/Dropbox (MIT)/efd/.envlv", override=True)
    pm = PostgresqlManager(dotenv_path="/Users/syyun/Dropbox (MIT)/efd/.envlv")
    data = pm.execute_sql(sql=sql_check_how_many_left, fetchall=True, commit=False)
    how_many_left = data[0][0]
    return how_many_left


def send_command_for_disambiguation(instance_id, batch_size, n_th_instance):
    # load_dotenv("/Users/syyun/Dropbox (MIT)/efd/.envlv", override=True)
    ec2m = EC2Manager(env_path="/Users/syyun/Dropbox (MIT)/efd/.envlv", region_name="us-east-1")
    ssh_client = ec2m.ssh_to_instance(instance_id=instance_id)
    commands = [
        f"python3 ~/efd/scrape/client-name-ticker/get_ticker.py --batch_size {batch_size} --n_th_instance {n_th_instance}"
    ]
    ec2m.send_command_through_ssh(ssh=ssh_client, commands=commands)
    print("sent command to instance: ", instance_id, "batch_size: ", batch_size, "n_th_instance: ", n_th_instance)


if __name__ == "__main__":

    num_instances = 250
    how_many_left = check_how_many_left()  # check remaining jobs
    terminate_threshold = 50

    while how_many_left > terminate_threshold:
        instance_ids = create_ec2s(num_instances=num_instances, timeout=60)
        # ec2 = boto3.resource("ec2", region_name="us-east-1")
        # instance_ids = [instance.id for instance in ec2.instances.all() if instance.state['Name'] == "running"]
        import time
        time.sleep(120)

        batch_size = (how_many_left // len(instance_ids)) + 1
        print("batch_size", batch_size)

        print(instance_ids)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(instance_ids)
        ) as executor:
            executor.map(
                send_command_for_disambiguation,
                instance_ids,
                [batch_size] * len(instance_ids),
                [i for i in range(len(instance_ids))],
            )

        print("batch jobs done.")
        print("terminate.")

        terminate_ec2s()
        how_many_left = check_how_many_left()  # check remaining jobs

    print("all done.")