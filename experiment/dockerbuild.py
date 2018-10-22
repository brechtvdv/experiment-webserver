import docker
from io import BytesIO
client = docker.from_env()


def build(image):
    return client.images.build(
        fileobj=BytesIO(image.tarfile.read()),
        custom_context=True,
        encoding='gzip',
        tag=image.full_tag_local
    )


def push(image):
    return client.images.push(image.full_tag_local)


def build_and_push(image):
    build(image)
    return push(image)
