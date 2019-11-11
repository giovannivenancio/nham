import docker
from utils import *

class VirtualizedInfrastructureManager():
    """
    Virtualized Infrastructure Manager implementation.
    """

    def __init__(self):
        self._docker = docker.from_env()

    def create_virtual_device(self, type, image, num_cpus, mem_size):
        """Create a virtual device."""

        container = self._docker.containers.run(
            image,
            detach=True,
            cap_add=['NET_ADMIN'],
            stdin_open=True,
            tty=True,
            cpu_count=num_cpus,
            mem_limit=mem_size)

        device = {
            'id': container.id,
            'short_id': container.short_id,
            'image': container.image.tags[0],
            'ip': self._docker.containers.get(container.id).attrs['NetworkSettings']['IPAddress'],
            'num_cpus': num_cpus,
            'mem_size': mem_size
        }

        insert_db('device', device['id'], device)

        return device

    def list_virtual_devices(self):
        """List all virtual devices."""

        devices = load_db('device')

        for id in devices:
            print "[container] [%s] [%s] [%s] [%s]" % (devices[id]['image'], id, devices[id]['ip'], self.get_status(id))

        return devices

    def get_virtual_device(self, v_id):
        """Get information from a specific device."""

        devices = load_db('device')

        for id in devices:
            if id == v_id:
                return devices[id]

    def get_status(self, id):
        """Get status of a virtual device."""

        return self._docker.containers.get(id).status

    def delete_virtual_device(self, id):
        """Delete a virtual device."""

        container = self._docker.containers.get(id)
        container.stop()
        container.remove()

        remove_db('device', id)

    def purge_devices(self):
        """Stop and delete all virtual devices."""

        for container in self._docker.containers.list():
            container.stop()

        self._docker.containers.prune()

        devices = load_db('device')

        for id in devices:
            try:
                remove_db('device', id)
            except:
                pass

    def exec_cmd(self, id, cmd):
        """Execute a command on the virtual device."""

        device = self._docker.containers.get(id)
        device.exec_run(cmd)
