
# -*- coding: utf-8 -*-
from contextlib import contextmanager
from html import escape
from threading import Timer
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Type, Union
from types import TracebackType

import pymqi
import configparser

from robot.api import logger
from robot.running.context import EXECUTION_CONTEXTS
from robot.running.timeouts import KeywordTimeout, TestTimeout
from robot.utils import ConnectionCache
from robot.libraries.BuiltIn import BuiltIn

class PyMQI(object):

    """
    Robot Framework library for operating IBM MQ via pyMQI.

    == Dependencies ==
    | pymqi | https://github.com/dsuch/pymqi | version >= 1.12 |
    | robot framework | http://robotframework.org |
    """

    DEFAULT_TIMEOUT = 900.0  # The default timeout for connecting
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    qmgr:          Optional[str] = None
    channel:       Optional[str] = None
    host:          Optional[str] = None
    port:          Optional[int] = None
    conn_info:     Optional[str] = None
    connection:    pymqi.QueueManager


    def __init__(self) -> None:
        """
        Check config.
        """
        try:
            config = configparser.ConfigParser()
            config.read('PyMQI.cfg')

            self.qmgr = config.get('IBM.MQ', 'mq_qmgr')
            self.channel       = config.get('IBM.MQ', 'mq_channel')
            self.host          = config.get('IBM.MQ', 'mq_host')
            self.port          = config.getint('IBM.MQ', 'mq_port')
            self.conn_info     = '%s(%s)' % (self.host, self.port)

            print('[PyMQI::PyMQI got default config:')
            print('qmgr = ',self.qmgr)
            print('channel       = ',self.channel)
            print('conn_info     = ',self.conn_info)
            print('')
            
        except configparser.Error as err:
            print('[PyMQI::PyMQI could not get the default config from PyMQI.cfg')
        

    def connect_in_client_mode(self, qmgr: str = None, channel: str = None, host:str = None, port: int = None) -> int:
        """
        Connection to IBM MQ, using client mode.

        *Args:*\n
            _qmgr       - queue manager name;\n
            _channel    - channel for connection;\n
            _host       - host name for connection;\n
            _port       - port used for connection;\n

        *Returns:*\n
            Returns ID of the new connection. The connection is set as active.

        *Example:*\n
            | Connect In Client Mode  |  'QM1'  | 'DEV.APP.SVRCONN' |  '127.0.0.1' | '1414'
        """

        try:
            if qmgr is None:
                qmgr = self.qmgr
            if channel is None:
                channel = self.channel
            if host is None:
                host = self.host
            if port is None:
                port = self.port
                
            print('[PyMQI::connect_in_client_mode]:: Connecting using : qmgr=[',qmgr,'], channel=[',channel,'], host=[',host,'], port=[',port,']...')
            self.conn_info = '%s(%s)' % (host, port)
            self.connection = pymqi.connect(qmgr, channel, self.conn_info)
            print('[PyMQI::connect_in_client_mode]:: Connecting established successfully.')
            print('')
            return 0
        except pymqi.MQMIError as err:
            raise Exception("[PyMQI::connect_in_client_mode] Error:", str(err))


    def connect_with_credencials(self, user: str, pwd: str, qmgr: str = None, channel: str = None, host:str = None, port: int = None) -> int:
        """
        Connection to IBM MQ, using credentials.

        *Args:*\n
            _qmgr       - queue manager name;\n
            _channel    - channel for connection;\n
            _host       - host name for connection;\n
            _port       - port used for connection;\n
            _user       - user name for connection;\n
            _pwd        - user password for connection;\n

        *Returns:*\n
            Returns ID of the new connection. The connection is set as active.

        *Example:*\n
            | Connect With Credentials |  'QM1'  | 'DEV.APP.SVRCONN' |  '127.0.0.1' | '1414' | 'scott' | 'tiger'
        """

        try:
            if qmgr is None:
                qmgr = self.qmgr
            if channel is None:
                channel = self.channel
            if host is None:
                host = self.host
            if port is None:
                port = self.port
                
            print('[PyMQI::connect_with_credencials]:: Connecting using : user=[',user,'], pwd=[',pwd,'], qmgr=[',qmgr,'], channel=[',channel, '], host=[',host,'], port=[',port,']...')
            self.conn_info = '%s(%s)' % (host, port)
            self.connection = pymqi.connect(qmgr, channel, self.conn_info, user, pwd)
            print('[PyMQI::connect_with_credencials]:: Connecting established successfully.')
            print('')
            return 0

        except pymqi.MQMIError as err:
            raise Exception("[PyMQI::connect_with_credencials] Error:", str(err))


    def disconnect(self) -> None:
        """
        Close active IBM MQ connection.

        *Example:*\n
            | Disconnect |
        """

        try:
            print('[PyMQI::disconnect]:: Start...')
            self.connection.disconnect()
            print('[PyMQI::disconnect]:: Ended successfully.')
            print('')

        except pymqi.MQMIError as err:
            raise Exception("[PyMQI::Disconnect] Error:", str(err))


    def purge_queue(self, queue_name: str) -> None:
        """
         Purge all message from a queue.

        *Args:*\n
            _queue_name_ - Name of the queue to purge;\n

        *Raises:*\n
            MQ Error: Error message according PyMQI.

        *Example:*\n
            Purge Queue | 'TEST.SERVICENAME.REPLY'
        """

        msg_cnt = 0
        try:
            print('[PyMQI::purge_queue]:: Start with queue_name=[',queue_name,']...')
            queue = pymqi.Queue(self.connection, queue_name)
            message = queue.get()
            while message is not None:
                msg_cnt += 1
                #print('[PyMQI::purge_queue]:: Purged message [', msg_cnt, ']: [', message.decode("utf-8"),']')
                message = queue.get()
            print('[PyMQI::purge_queue]:: Ended successfully with [',msg_cnt,'] messages.')
            print('')

        except pymqi.MQMIError as err:
            str_err = str(err)
            if (str_err.find('MQRC_NO_MSG_AVAILABLE') >= 0):
                print('[PyMQI::purge_queue]:: Ended with [',msg_cnt,'] messages.')
                print('')
            else:
                raise Exception("[PyMQI::purge_queue] Error:", str(err))


    def put_message(self, message: str, queue_name: str) -> None:
        """
         Put a message into a queue.

        *Args:*\n
            _message_    - COntent of messgae to put into queue;\n
            _queue_name_ - Name of the target queue;\n

        *Raises:*\n
            MQ Error: Error message according PyMQI.

        *Example:*\n
            |  Put Message |  'Hello World!' | 'TEST.SERVICENAME.REQUEST'
        """

        try:
            print('[PyMQI::put_message]:: Start with message=[', message, '], queue_name=[', queue_name,']...')
            queue = pymqi.Queue(self.connection, queue_name)
            queue.put(message.encode("utf-8"))
            print('[PyMQI::put_message]:: Ended successfully.')

        except pymqi.MQMIError as err:
            raise Exception("[PyMQI::Put Message] Error:", str(err))


    def put_message_from_file(self, file_path: str, queue_name: str) -> None:
        """
         Put a message from file into a queue.

        *Args:*\n
            _file_path_  - Path to a message file;\n
            _queue_name_ - Name of the target queue;\n

        *Raises:*\n
            MQ Error: Error message according PyMQI.

        *Example:*\n
            |  Put Messgae From File |  ${CURDIR}${/}message.dat | 'TEST.SERVICENAME.REQUEST'
        """

        try:
            print('[PyMQI::put_message_from_file]:: Start with file_path=[', file_path, '], queue_name=[', queue_name,']...')
            with open(file_path, "r") as messagefile:
                message = messagefile.read()
                queue = pymqi.Queue(self.connection, queue_name)
                queue.put(message.encode("utf-8"))
            print('[PyMQI::put_message_from_file]:: Ended successfully.')

        except pymqi.MQMIError as err:
            raise Exception("[PyMQI::Put Message From File] Error:", str(err))


    def get_message(self, queue_name: str) -> str:
        """
         Get a message from a queue.

        *Args:*\n
            _queue_name_ - Name of the target queue;\n

        *Raises:*\n
            MQ Error: Error message according PyMQI.

        *Example:*\n
            ${msg} = |  Get Message | 'TEST.SERVICENAME.REPLY'
        """

        try:
            print('[PyMQI::get_message]:: Start with queue_name=[', queue_name,']...')
            queue = pymqi.Queue(self.connection, queue_name)
            message = queue.get()
            print('[PyMQI::get_message]:: Ended successfully, returing with message=[', message.decode("utf-8"),'].')
            return message.decode("utf-8")

        except pymqi.MQMIError as err:
            str_err = str(err)
            if (str_err.find('MQRC_NO_MSG_AVAILABLE') >= 0):
                print('[PyMQI::get_message]:: Ended successfully with no message.')
            else:
                raise Exception("[PyMQI::get_message] Error:", str(err))


    def get_all_messages(self, queue_name: str) -> str:
        """
         Get all messages from a queue.

        *Args:*\n
            _queue_name_ - Name of the target queue;\n

        *Raises:*\n
            MQ Error: Error message according PyMQI.

        *Example:*\n
            ${msg} = |  Get All Messages | 'TEST.SERVICENAME.REPLY'
        """

        messages = ''
        msg_cnt = 0

        try:

            print('[PyMQI::get_all_messages]:: Start with queue_name=[', queue_name,']...')
            queue = pymqi.Queue(self.connection, queue_name)

            message = queue.get()
            messages = messages + message.decode("utf-8")

            while message is not None:
                messages = messages + ', '
                msg_cnt += 1
                #print('[PyMQI::purge_queue]:: Purged message [', msg_cnt, ']: [', message.decode("utf-8"),']')
                message = queue.get()
                messages = messages + message.decode("utf-8")

            print('[PyMQI::get_all_messages]:: Ended successfully with [',msg_cnt,'] messages, content=[', messages,'].')
            print('')            
            return messages

        except pymqi.MQMIError as err:
            str_err = str(err)
            if (str_err.find('MQRC_NO_MSG_AVAILABLE') >= 0):
                print('[PyMQI::get_all_messages]:: Ended successfully with [',msg_cnt,'] messages, content=[', messages,'].')
                return messages
            else:
                raise Exception("[PyMQI::get_all_messages] Error:", str(err))


    def get_message_into_file(self, queue_name: str, file_path: str) -> None:
        """
         Getting a message into file from a queue.

        *Args:*\n
            _queue_name_ - Name of the target queue;\n
            _file_path_  - Path to a message file;\n

        *Raises:*\n
            MQ Error: Error message according PyMQI.

        *Example:*\n
            |  Get Messgae Into File | 'TEST.SERVICENAME.REQUEST' |  ${CURDIR}${/}message.dat 
        """

        try:
            print('[PyMQI::get_message_into_file]:: Start with queue_name=[', queue_name,', file_path=[', file_path,']]...')
            with open(file_path, "w") as messagefile:
                queue = pymqi.Queue(self.connection, queue_name)
                message = queue.get()
                messagefile.write(message.decode("utf-8"))
            print('[PyMQI::get_message_into_file]:: Ended successfully.')

        except pymqi.MQMIError as err:
            str_err = str(err)
            if (str_err.find('MQRC_NO_MSG_AVAILABLE') >= 0):
                print('[PyMQI::get_message_into_file]:: Ended successfully with [',msg_cnt,'] messages.')
            else:
                raise Exception("[PyMQI::get_message_into_file] Error:", str(err))


    def get_all_messages_into_file(self, queue_name: str, file_path: str) -> None:
        """
         Getting all messages into file from a queue.

        *Args:*\n
            _queue_name_ - Name of the target queue;\n
            _file_path_  - Path to a message file;\n

        *Raises:*\n
            MQ Error: Error message according PyMQI.

        *Example:*\n
            |  Get All Messages Into File | 'TEST.SERVICENAME.REQUEST' |  ${CURDIR}${/}message.dat 
        """

        msg_cnt = 0
        try:
            print('[PyMQI::get_all_messages_into_file]:: Start with queue_name=[', queue_name,', file_path=[', file_path,']]...')
            with open(file_path, "w") as messagefile:
                queue = pymqi.Queue(self.connection, queue_name)
                message = queue.get()
                messagefile.write(message.decode("utf-8"))

                while message is not None:
                    msg_cnt += 1
                    message = queue.get()
                    messagefile.write(', ')
                    messagefile.write(message.decode("utf-8"))

            print('[PyMQI::get_all_messages_into_file]:: Ended successfully.')

        except pymqi.MQMIError as err:
            str_err = str(err)
            if (str_err.find('MQRC_NO_MSG_AVAILABLE') >= 0):
                print('[PyMQI::get_all_messages_into_file]:: Ended successfully with [',msg_cnt,'] messages.')
            else:
                raise Exception("[PyMQI::get_all_messages_into_file] Error:", str(err))


"""
print('Testing:')
print('')

print('Test step: Instantiate a pyMQI object and connect to a queuemanager...')
pq = PyMQI()
pq.connect_in_client_mode()
print('')

print('Test step: Purge a queue...')
pq.purge_queue('T7.SCHRKD.REQUEST')
print('')

print('Test step: Put a message into a queue in queuemanager and read it back...')
imsg = 'Hello world!'
pq.put_message(imsg, 'T7.SCHRKD.REPLY')
msgs = pq.get_all_messages('T7.SCHRKD.REPLY')
print('Message got back from queue: [', msgs, '].')
print('')

print('Test step: Put 3 message into a queue and read only the 1st one of them back...')
pq.put_message('Hello world_t1_1', 'T7.SCHRKD.REPLY')
pq.put_message('Hello world_t1_2', 'T7.SCHRKD.REPLY')
pq.put_message('Hello world_t1_3', 'T7.SCHRKD.REPLY')
msg = pq.get_message('T7.SCHRKD.REPLY')
print('Message got back from queue: [', msg, '].')
pq.purge_queue('T7.SCHRKD.REPLY')
print('')

print('Test step: Put 3 message into a queue and read all of them back in one step...')
pq.put_message('Hello world1_t2_1', 'T7.SCHRKD.REPLY')
pq.put_message('Hello world1_t2_2', 'T7.SCHRKD.REPLY')
pq.put_message('Hello world1_t2_3', 'T7.SCHRKD.REPLY')
msgs = pq.get_all_messages('T7.SCHRKD.REPLY')
print('Messages got back from queue: [', msgs, '].')
pq.purge_queue('T7.SCHRKD.REPLY')
print('')

print('Test step: Put 1 message into an input file, then write file content into a queue and read it back into an output file...')
ifmsg = 'Hello wWorld from file!'
fih = open("schrkd_input.msg", "w")
fih.write(ifmsg)
fih.close()
pq.put_message_from_file("schrkd_input.msg", 'T7.SCHRKD.REPLY')
pq.get_message_into_file('T7.SCHRKD.REPLY', "schrkd_output.msg")
print('Message got back from queue into file: [')
with open("schrkd_output.msg", "r+") as file1: 
    print(file1.read()) 
print('].')
pq.purge_queue('T7.SCHRKD.REPLY')
print('')

print('Test step: Put a message 3 times into an input file, then write file content into a queue (it must be 1 message), and read it back into an output file...')
ifmsg = 'Hello wWorld from file! '
fih = open("schrkd_input.msg", "w")
fih.write(ifmsg)
fih.write(ifmsg)
fih.write(ifmsg)
fih.close()
pq.put_message_from_file("schrkd_input.msg", 'T7.SCHRKD.REPLY')
pq.get_message_into_file('T7.SCHRKD.REPLY', "schrkd_output.msg")
print('Message got back from queue into file: [')
with open("schrkd_output.msg", "r+") as file1: 
    print(file1.read()) 
print('].')
pq.purge_queue('T7.SCHRKD.REPLY')
print('')

print('Test step: Put a message into an input file, then write file content into a queue 3 times (they must be 3 messages), and read only the 1st one back into an output file...')
ifmsg = 'Hello wWorld from file! '
fih = open("schrkd_input.msg", "w")
fih.write(ifmsg)
fih.close()
pq.put_message_from_file("schrkd_input.msg", 'T7.SCHRKD.REPLY')
pq.put_message_from_file("schrkd_input.msg", 'T7.SCHRKD.REPLY')
pq.put_message_from_file("schrkd_input.msg", 'T7.SCHRKD.REPLY')
pq.get_message_into_file('T7.SCHRKD.REPLY', "schrkd_output.msg")
print('Message got back from queue into file: [')
with open("schrkd_output.msg", "r+") as file1: 
    print(file1.read()) 
print('].')
pq.purge_queue('T7.SCHRKD.REPLY')
print('')

print('Test step: Put a message into an input file, then write file content into a queue 3 times (they must be 3 messages), and read the whole queue content back into an output file...')
ifmsg = 'Hello World from file! '
fih = open("schrkd_input.msg", "w")
fih.write(ifmsg)
fih.close()
pq.put_message_from_file("schrkd_input.msg", 'T7.SCHRKD.REPLY')
pq.put_message_from_file("schrkd_input.msg", 'T7.SCHRKD.REPLY')
pq.put_message_from_file("schrkd_input.msg", 'T7.SCHRKD.REPLY')
pq.get_all_messages_into_file('T7.SCHRKD.REPLY', "schrkd_output.msg")
print('Message got back from queue into file: [')
with open("schrkd_output.msg", "r+") as file1: 
    print(file1.read()) 
print('].')
pq.purge_queue('T7.SCHRKD.REPLY')
print('')

print('Test step: Disconnect from queuemanager...')
pq.disconnect()
print('')

"""
