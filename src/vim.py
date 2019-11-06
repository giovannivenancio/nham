import docker

class VirtualizedInfrastructureManager():
    """
    Virtualized Infrastructure Manager implementation.
    """

    def __init__(self):
        self._docker = docker.from_env()

    def create_virtual_device(self, type, image, cpu_count, mem_limit):
        """Create a virtual device."""

        container = self._docker.containers.run(
            image,
            detach=True,
            stdin_open=True,
            tty=True,
            cpu_count=cpu_count,
            mem_limit=mem_limit)

        print "Container %s created" % container.id

        return container.id

    def list_virtual_devices(self):
        """List all virtual devices."""

        print "---\nListing virtual devices:\n"
        for (num, container) in enumerate(self._docker.containers.list(), start=1):
          print "%d. [container] [%s] [%s] [%s] [%s]" % (num, container.image.tags[0], container.short_id, container.attrs['NetworkSettings']['IPAddress'] , container.status)
        print "---\n"

    def delete_virtual_device(self, id):
        """Delete a virtual device."""

        print "Deleting container %s" % id

        container = self._docker.containers.get(id)
        container.stop()
        container.remove()

    def purge_devices(self):
        """Stop and delete all virtual devices."""

        print "Purging all virtual devices..."
        for container in self._docker.containers.list():
            print container.id
            container.stop()
        self._docker.containers.prune()

    def get_virtual_device(self, id):
        """."""
        pass
