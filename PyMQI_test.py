# Pre-requisite:
# export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/mqm/lib64"

import PyMQI

print('Testing PyMQI wrapper python library')
print('')

print('Test step: Instantiate a pyMQI object and connect to a queuemanager...')
pq = PyMQI.PyMQI()
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
