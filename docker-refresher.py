import subprocess


def docker_refresher():
    # build the Docker image
    build_command = "docker build ."
    output = subprocess.check_output(
        build_command,
        shell=True,
        text=True,
        encoding="utf-8",
        stderr=subprocess.STDOUT,
    )
    print(output)

    # extract the image id
    image_id = (
        output.split("writing image")[1]
        .split("\n")[0]
        .strip()
        .split("sha256:")[1]
        .strip()
        .split("done")[0]
        .strip()
    )
    print(image_id)

    # tag the image
    tag_command = f"docker tag {image_id} ronnytec/nuclei:latest"
    pusher = subprocess.check_output(
        tag_command,
        shell=True,
        encoding="utf-8",
        stderr=subprocess.STDOUT,
    )
    print(pusher)
    # push the image
    push_command = "docker push ronnytec/nuclei:latest"
    subprocess.call(push_command, shell=True)

    # build the Docker Compose containers
    build_compose_command = "docker-compose build"
    subprocess.call(build_compose_command, shell=True)

    # run the Docker Compose containers
    run_compose_command = "docker-compose up"
    subprocess.call(run_compose_command, shell=True)


if __name__ == "__main__":
    docker_refresher()
