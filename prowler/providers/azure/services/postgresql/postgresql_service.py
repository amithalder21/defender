from dataclasses import dataclass

from azure.mgmt.rdbms.postgresql_flexibleservers import PostgreSQLManagementClient

from prowler.lib.logger import logger
from prowler.providers.azure.lib.service.service import AzureService


class PostgreSQL(AzureService):
    def __init__(self, audit_info):
        super().__init__(PostgreSQLManagementClient, audit_info)
        self.flexible_servers = self.__get_flexible_servers__()

    def __get_flexible_servers__(self):
        logger.info("PostgreSQL - Getting PostgreSQL servers...")
        flexible_servers = {}
        for subscription, client in self.clients.items():
            try:
                flexible_servers.update({subscription: []})
                flexible_servers_list = client.servers.list()
                for postgresql_server in flexible_servers_list:
                    resource_group = self.__get_resource_group__(postgresql_server.id)
                    require_secure_transport = self.__get_require_secure_transport__(
                        subscription, resource_group, postgresql_server.name
                    )
                    log_checkpoints = self.__get_log_checkpoints__(
                        subscription, resource_group, postgresql_server.name
                    )
                    log_disconnections = self.__get_log_disconnections__(
                        subscription, resource_group, postgresql_server.name
                    )
                    log_connections = self.__get_log_connections__(
                        subscription, resource_group, postgresql_server.name
                    )
                    connection_throttling = self.__get_connection_throttling__(
                        subscription, resource_group, postgresql_server.name
                    )
                    flexible_servers[subscription].append(
                        Server(
                            id=postgresql_server.id,
                            name=postgresql_server.name,
                            resource_group=resource_group,
                            require_secure_transport=require_secure_transport,
                            log_checkpoints=log_checkpoints,
                            log_connections=log_connections,
                            log_disconnections=log_disconnections,
                            connection_throttling=connection_throttling,
                        )
                    )
            except Exception as error:
                logger.error(
                    f"Subscription name: {subscription} -- {error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
                )
        return flexible_servers

    def __get_resource_group__(self, id):
        resource_group = id.split("/")[4]
        return resource_group

    def __get_require_secure_transport__(
        self, subscription, resouce_group_name, server_name
    ):
        client = self.clients[subscription]
        require_secure_transport = client.configurations.get(
            resouce_group_name, server_name, "require_secure_transport"
        )
        return require_secure_transport.value.upper()

    def __get_log_checkpoints__(self, subscription, resouce_group_name, server_name):
        client = self.clients[subscription]
        log_checkpoints = client.configurations.get(
            resouce_group_name, server_name, "log_checkpoints"
        )
        return log_checkpoints.value.upper()

    def __get_log_connections__(self, subscription, resouce_group_name, server_name):
        client = self.clients[subscription]
        log_connections = client.configurations.get(
            resouce_group_name, server_name, "log_connections"
        )
        return log_connections.value.upper()

    def __get_log_disconnections__(self, subscription, resouce_group_name, server_name):
        client = self.clients[subscription]
        log_disconnections = client.configurations.get(
            resouce_group_name, server_name, "log_disconnections"
        )
        return log_disconnections.value.upper()

    def __get_connection_throttling__(
        self, subscription, resouce_group_name, server_name
    ):
        client = self.clients[subscription]
        connection_throttling = client.configurations.get(
            resouce_group_name, server_name, "connection_throttle.enable"
        )
        return connection_throttling.value.upper()


@dataclass
class Server:
    id: str
    name: str
    resource_group: str
    require_secure_transport: str
    log_checkpoints: str
    log_connections: str
    log_disconnections: str
    connection_throttling: str
