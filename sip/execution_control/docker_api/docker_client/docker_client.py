# -*- coding: utf-8 -*-
"""Docker Client API."""

import re
import os
import logging
import docker
import yaml


LOG = logging.getLogger('SIP.EF.DC')


class DockerClient:
    """Docker Client Interface."""

    def __init__(self):
        """Initialise of the class."""
        # Create a docker client
        self._client = docker.from_env()

        # Store a flag to show whether we are on a manager node or a worker.
        self._manager = self._client.info()['Swarm']['ControlAvailable']

        # Docker low-level API
        self._api_client = docker.APIClient()

    ###########################################################################
    # Create functions
    ###########################################################################

    def create_services(self, compose_str: str) -> list:
        """Create new docker services.

        Args:
            compose_str (string): Docker compose 'file' string

        Return:
            service_names, list
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be run on '
                               'swarm manager nodes')

        # Initialise empty list
        services_ids = []

        try:
            service_config = yaml.load(compose_str)
            print(service_config)
            for service_name in service_config['services']:
                service_exist = self._client.services.list(
                    filters={'name': service_name})
                if not service_exist:
                    service_spec = self._parse_services(
                        service_config, service_name)
                    for s_spec in service_spec:
                        created_service = self._client.services.create(**s_spec)
                        # service_name = created_service.name
                        service_id = created_service.short_id
                        LOG.debug('Service created: %s', service_id)
                        services_ids.append(service_id)
                else:
                    LOG.debug('Services already exists')

        except yaml.YAMLError as exc:
            print(exc)

        # Returning list of services created
        return services_ids

    def create_volume(self, volume_name, driver_spec=None):
        """Create new docker volumes.

        Only the manager nodes can create a volume

        Args:
            volume_name (string): Name for the new docker volume
            driver_spec (string): Driver for the docker volume
        """
        # Default values
        if driver_spec:
            driver = driver_spec
        else:
            driver = 'local'

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be deleted '
                               'on swarm manager nodes')

        self._client.volumes.create(name=volume_name, driver=driver)

    ###########################################################################
    # Delete functions
    ###########################################################################

    def delete_service(self, service):
        """Removes/stops a docker service.

        Only the manager nodes can delete a service

        Args:
            service (string): Service name or ID
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be deleted '
                               'on swarm manager nodes')

        # Remove service
        self._api_client.remove_service(service)

    def delete_all_services(self):
        """Removes/stops a service.

        Only the manager nodes can delete a service
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be deleted '
                               'on swarm manager nodes')

        service_list = self.get_service_list()
        for services in service_list:
            # Remove all the services
            self._api_client.remove_service(services)

    def delete_all_volumes(self):
        """Remove all the volumes.

        Only the manager nodes can delete a volume
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Volumes can only be deleted '
                               'on swarm manager nodes')

        volume_list = self.get_volume_list()
        for volumes in volume_list:
            # Remove all the services
            self._api_client.remove_volume(volumes, force=True)

    def delete_volume(self, volume_name):
        """Removes/stops a docker volume.

        Only the manager nodes can delete a volume

        Args:
            volume_name (string): Name of the volume
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Volumes can only be deleted '
                               'on swarm manager nodes')

        # Remove volume
        self._api_client.remove_volume(volume_name)

    ###########################################################################
    # Get functions
    ###########################################################################

    def get_service_state(self, service_id: str) -> str:
        """Get the state of the service.

        Only the manager nodes can retrieve service state

        Args:
            service_id (str): Service id

        Returns:
            str, state of the service

        """
        # Get service
        service = self._client.services.get(service_id)

        # Get the state of the service
        for service_task in service.tasks():
            service_state = service_task['DesiredState']
        return service_state

    def get_node_list(self):
        """Get a list of nodes.

        Only the manager nodes can retrieve all the nodes

        Returns:
            list, all the ids of the nodes in swarm

        """
        # Initialising empty list
        nodes = []

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node '
                               'can retrieve all the nodes.')

        node_list = self._client.nodes.list()
        for n_list in node_list:
            nodes.append(n_list.id)
        return nodes

    def get_node_details(self, node_id):
        """Get details of a node.

        Only the manager nodes can retrieve details of a node

        Args:
            node_id (list): List of node ID

        Returns:
            dict, details of the node

        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can '
                               'retrieve node details.')

        node = self._client.nodes.get(node_id)
        return node.attrs

    def get_service_list(self):
        """Get a list of docker services.

        Only the manager nodes can retrieve all the services

        Returns:
            list, all the ids of the services in swarm

        """
        # Initialising empty list
        services = []

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can retrieve'
                               ' all the services.')

        service_list = self._client.services.list()
        for s_list in service_list:
            services.append(s_list.id)
        return services

    def get_service_name(self, service_id):
        """Get the name of the docker service.

        Only the manager nodes can retrieve service name

        Args:
            service_id (string): List of service ID

        Returns:
            string, name of the docker service

        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can retrieve all'
                               ' the services details.')

        service = self._client.services.get(service_id)
        return service.name

    def get_service_details(self, service_id):
        """Get details of a service.

        Only the manager nodes can retrieve service details

        Args:
            service_id (string): List of service id

        Returns:
            dict, details of the service

        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can retrieve all'
                               ' the services details.')

        service = self._client.services.get(service_id)
        return service.attrs

    def get_container_details(self, container_id_or_name):
        """Get details of a container.

        Args:
            container_id_or_name (string): docker container id or name

        Returns:
            dict, details of the container

        """
        container = self._client.containers.get(container_id_or_name)
        return container.attrs

    def get_volume_list(self):
        """Get a list of docker volumes.

        Only the manager nodes can retrieve all the volumes

        Returns:
            list, all the names of the volumes in swarm

        """
        # Initialising empty list
        volumes = []

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can retrieve'
                               ' all the services.')

        volume_list = self._client.volumes.list()
        for v_list in volume_list:
            volumes.append(v_list.name)
        return volumes

    def get_volume_details(self, volume_name):
        """Get details of the volume.

        Args:
            volume_name (string): Name of the volume

        Returns:
            dict, details of the volume

        """
        if volume_name not in self.get_volume_list():
            raise RuntimeError('No such volume found: ', volume_name)

        volume = self._client.volumes.get(volume_name)
        return volume.attrs

    ###########################################################################
    # Update functions
    ###########################################################################

    def update_labels(self, node_name, labels):
        """Update label of a node.

        Args:
            node_name (string): Name of the node.
            labels (dict): Label to add to the node
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can update '
                               'node details.')

        # Node specification
        node_spec = {'Availability': 'active',
                     'Name': node_name,
                     'Role': 'manager',
                     'Labels': labels}
        node = self._client.nodes.get(node_name)
        node.update(node_spec)

    ###########################################################################
    # Parsing functions
    ###########################################################################

    def _parse_services(self, service_config, service_name):
        """Parse the docker compose file.

        Args:
            service_config (dict): Service configurations from the compose file
            service_name (string): Name of the services

        Returns:
            dict, service specifications extracted from the compose file

        """
        # Initialising empty dictionary
        service_spec = {}

        service_spec['name'] = service_name
        for key, value in service_config['services'][service_name].items():
            if 'ports' in key:
                endpoint_spec = self._parse_ports(value)
                service_spec['endpoint_spec'] = endpoint_spec
            else:
                if 'volumes' in key:
                    volume_spec = self._parse_volumes(value)
                    service_spec['mounts'] = volume_spec
                else:
                    if 'deploy' in key:
                        self._parse_deploy(value, service_spec)
                    else:
                        if 'networks' in key:
                            network_spec = self._parse_networks(service_config)
                            service_spec['networks'] = network_spec
                        else:
                            service_spec[key] = value
        yield service_spec

    def _parse_deploy(self, deploy_values, service_spec):
        """Parse deploy key.

        Args:
            deploy_values (dict): deploy configuration values
            service_spec (dict): Service specification
        """
        # Initialising empty dictionary
        mode = {}

        for d_value in deploy_values:
            if 'restart_policy' in d_value:
                restart_spec = docker.types.RestartPolicy(
                    **deploy_values[d_value])
                service_spec['restart_policy'] = restart_spec
            if 'mode' in d_value:
                if 'replicas' in d_value:
                    mode[d_value] = deploy_values[d_value]
                else:
                    mode[d_value] = deploy_values[d_value]
            if 'resources' in d_value:
                resource_spec = self._parse_resources(
                    deploy_values, d_value)
                service_spec['resources'] = resource_spec

        # Setting the types
        mode_spec = docker.types.ServiceMode(**mode)
        service_spec['mode'] = mode_spec

    ###########################################################################
    # Static methods
    ###########################################################################

    @staticmethod
    def _parse_ports(port_values):
        """Parse ports key.

        Args:
            port_values (dict): ports configuration values

        Returns:
            dict, Ports specification which contains exposed ports

        """
        # Initialising empty dictionary
        endpoints = {}

        for port_element in port_values:
            target_port = port_element.split(':')
            for port in target_port:
                endpoints[int(port)] = int(port)

        # Setting the types
        endpoint_spec = docker.types.EndpointSpec(ports=endpoints)
        return endpoint_spec

    @staticmethod
    def _parse_volumes(volume_values):
        """Parse volumes key.

        Args:
            volume_values (dict): volume configuration values

        Returns:
            string, volume specification with mount source and container path

        """
        for v_values in volume_values:
            for v_key, v_value in v_values.items():
                if v_key == 'source':
                    if v_value == '.':
                        source = os.path.dirname(
                            os.path.abspath(__file__))
                    else:
                        source = v_value
                if v_key == 'target':
                    target = v_value
            volume_spec = [source + ':' + target]
            return volume_spec

    @staticmethod
    def _parse_resources(resource_values, resource_name):
        """Parse resources key.

        Args:
            resource_values (dict): resource configurations values
            resource_name (string): Resource name

        Returns:
            dict, resources specification

        """
        # Initialising empty dictionary
        resources = {}

        for r_values in resource_values[resource_name]:
            if 'limits' in r_values:
                for r_key, r_value in \
                        resource_values[resource_name][r_values].items():
                    if 'cpu' in r_key:
                        cpu_value = float(r_value) * 10 ** 9
                        cpu_key = r_key[:3] + '_limit'
                        resources[cpu_key] = int(cpu_value)
                    if 'mem' in r_key:
                        mem_value = re.sub('M', '', r_value)
                        mem_key = r_key[:3] + '_limit'
                        resources[mem_key] = int(mem_value) * 1048576
        resources_spec = docker.types.Resources(**resources)

        return resources_spec

    @staticmethod
    def _parse_networks(service_config):
        """Parse network key.

        Args:
            service_config (dict): Service configurations

        Returns:
            list, List of networks

        """
        # Initialising empty list
        networks = []

        for n_values in service_config['networks'].values():
            for n_key, n_value in n_values.items():
                if 'name' in n_key:
                    networks.append(n_value)
        return networks
