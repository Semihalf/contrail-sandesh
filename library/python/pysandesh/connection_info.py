#
# Copyright (c) 2014 Juniper Networks, Inc. All rights reserved.
#

#
# Connection State 
#

import gevent

from gen_py.connection_info.constants import ConnectionTypeNames, \
    ConnectionStatusNames, ConnectivityStatusNames
from gen_py.connection_info.ttypes import ConnectionInfo, \
    ProcessConnectivityStatus

class ConnectionState(object):
    _CONN_INFO_INTVL = 60
    _sandesh = None 
    _connection_map = {}
    _hostname = None 
    _module_id = None
    _instance_id = None
    _status_cb = None
    _conn_info_timer = None
    _uve_type_cls = None
    _uve_data_type_cls = None

    @staticmethod
    def _conn_info_timer_expiry_handler():
        while True:
            conn_infos = ConnectionState._connection_map.values()
            (connectivity_status, message) = \
                ConnectionState._status_cb(conn_infos)
            process_conn_status = ProcessConnectivityStatus(
                module_id = ConnectionState._module_id,
                instance_id = ConnectionState._instance_id,
                status = ConnectivityStatusNames[connectivity_status],
                connection_infos = conn_infos) 
            uve_data = ConnectionState._uve_data_type_cls(
                name = ConnectionState._hostname,
                connection_status = [process_conn_status],
                description = message)
            uve = ConnectionState._uve_type_cls(data = uve_data,
                    sandesh = ConnectionState._sandesh)
            uve.send(sandesh = ConnectionState._sandesh)
            gevent.sleep(ConnectionState._CONN_INFO_INTVL)
    #end _conn_info_timer_expiry_handler
      
    @staticmethod
    def init(sandesh, hostname, module_id, instance_id, status_cb,
             uve_type_cls, uve_data_type_cls):
        ConnectionState._sandesh = sandesh
        ConnectionState._hostname = hostname
        ConnectionState._module_id = module_id
        ConnectionState._instance_id = instance_id
        ConnectionState._status_cb = status_cb
        ConnectionState._uve_type_cls = uve_type_cls
        ConnectionState._uve_data_type_cls = uve_data_type_cls
        if ConnectionState._conn_info_timer is None:
            ConnectionState._conn_info_timer = gevent.spawn_later(
                ConnectionState._CONN_INFO_INTVL,
                ConnectionState._conn_info_timer_expiry_handler)
    #end init

    @staticmethod     
    def update(conn_type, name, status, server_addrs, message):
        conn_key = (conn_type, name)
        conn_info = ConnectionInfo(type = ConnectionTypeNames[conn_type],
                                   name = name,
                                   status = ConnectionStatusNames[status],
                                   description = message,
                                   server_addrs = server_addrs)
        ConnectionState._connection_map[conn_key] = conn_info
    #end update

    @staticmethod
    def delete(conn_type, name):
        conn_key = (conn_type, name)
        ConnectionState._connection_map.pop(conn_key, 'None')
    #end delete

#end class ConnectionState
