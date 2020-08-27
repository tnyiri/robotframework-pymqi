*** Settings ***
Library    OperatingSystem
Library    String
Library    PyMQI     

*** Testcases ***

Test01
	[Documentation]     Using pmqi_wrapper.cfg to connect to queuemanager with default values
	Log    \nTesting PyMQI wrapper robotframework library\n                                   console=yes
	Log     Using pmqi_wrapper.cfg to connect to queuemanager with default values             console=yes
	PyMQI.Connect In Client Mode

Test02
	[Documentation]     Purge a queue
	Log    Test step: Purge a queue...\n'                                                     console=yes
	PyMQI.Purge Queue    %{ENV}.SVC1.REQUEST

Test03
	[Documentation]     Put / get
	Log    Test step: Put a message into a queue in queuemanager and read it back             console=yes
	${imsg}=    Set Variable    Hello world!
	PyMQI.Put Message    ${imsg}    %{ENV}.SVC1.REPLY
	${msg} =    PyMQI.Get Message    %{ENV}.SVC1.REPLY
	Log    Message got back from queue: [${msg}].                                            console=yes

Test04
	[Documentation]     Put n, get 1
	Log    Test step: Put 3 message into a queue and read only the 1st one of them back       console=yes
	PyMQI.Put Message    Hello world_t1_1    %{ENV}.SVC1.REPLY
	PyMQI.Put Message    Hello world_t1_2    %{ENV}.SVC1.REPLY
	PyMQI.Put Message    Hello world_t1_3    %{ENV}.SVC1.REPLY
	${msg} =    PyMQI.Get Message    %{ENV}.SVC1.REPLY	
	Log    Message got back from queue: [${msg}].                                             console=yes
	PyMQI.Purge Queue    %{ENV}.SVC1.REPLY

Test05
	[Documentation]     Put n, get all
	Log    Test step: Put 3 message into a queue and read all of them back in one step...     console=yes
	PyMQI.Put Message    Hello world1_t2_1    %{ENV}.SVC1.REPLY
	PyMQI.Put Message    Hello world1_t2_2    %{ENV}.SVC1.REPLY
	PyMQI.Put Message    Hello world1_t2_3    %{ENV}.SVC1.REPLY
	${msgs} =     PyMQI.Get All Messages    %{ENV}.SVC1.REPLY
	Log    Message got back from queue: [${msgs}].                                            console=yes
	PyMQI.Purge Queue    %{ENV}.SVC1.REPLY

Test06
	[Documentation]    Put msg into file, read file into queue, get content back from queue  
	Log    \nTest step: Put a message into file, write file content into a queue,             console=yes
	Log    and read it back into an output file...                                            console=yes
	${ifmsg} =    Set Variable    Hello World from file!
	Create File  schrkd_input.msg    ${ifmsg}
	PyMQI.Put Message From File    schrkd_input.msg    %{ENV}.SVC1.REPLY
	PyMQI.Get Message Into File    %{ENV}.SVC1.REPLY    schrkd_output.msg
	Log    Message got back from queue into file:                                             console=yes
	${File}=    Get File    schrkd_output.msg
	@{list}=    Split to lines  ${File}     
	:FOR    ${line}    IN    @{list}
	\   Log    ${line}	
	PyMQI.Purge Queue    %{ENV}.SVC1.REPLY

Test07
	[Documentation]    Put messages into file, read file into queue, get all content back from queue  
	Log    \nTest step: Put a message 3 times into an input file, then write file content    console=yes
	Log    into a queue (it must be 1 message), and read it back into an output file...      console=yes
	${ifmsg} =     Set Variable    Hello World from file!
	Create File  schrkd_input.msg    ${ifmsg} ${ifmsg} ${ifmsg}
	PyMQI.Put Message From File    schrkd_input.msg    %{ENV}.SCHRKD.REPLY
	PyMQI.Get Message Into File    %{ENV}.SVC1.REPLY    schrkd_output.msg
	Log    Message got back from queue into file:                                             console=yes
	${File} =    Get File    schrkd_output.msg
	@{list} =    Split to lines  ${File}     
	:FOR    ${line}    IN    @{list}
	\   Log    ${line}	                                                                          console=yes
	PyMQI.Purge Queue    %{ENV}.SVC1.REPLY

Test08
	[Documentation]    Put messages from file into queue and read the first one into file
	Log    \nTest step: Put a message into an input file, then write file content into a      console=yes
	Log    queue 3 times (they must be 3 messages), and read only the 1st one back into       console=yes
	Log    an output file...                                                                  console=yes 
	${ifmsg} =     Set Variable    Hello World from file!
	Create File  schrkd_input.msg    ${ifmsg} ${ifmsg} ${ifmsg}
	PyMQI.Put Message From File    schrkd_input.msg    %{ENV}.SVC1.REPLY
	PyMQI.Put Message From File    schrkd_input.msg    %{ENV}.SVC1.REPLY
	PyMQI.Put Message From File    schrkd_input.msg    %{ENV}.SVC1.REPLY
	PyMQI.Get Message Into File    %{ENV}.SVC1.REPLY    schrkd_output.msg
	Log    Message got back from queue into file:                                             console=yes
	${File} =    Get File    schrkd_output.msg
	@{list} =    Split to lines  ${File}     
	:FOR    ${line}    IN    @{list}
	\   Log    ${line}	                                                                          console=yes
	PyMQI.Purge Queue    %{ENV}.SVC1.REPLY

Test09
	[Documentation]    Put messages from file into queue and read all content into file
	Log    \nTest step: Put a message into an input file, then write file content into a      console=yes
	Log    queue 3 times (they must be 3 messages), and read all of them back into            console=yes
	Log    an output file...                                                                  console=yes 
	${ifmsg} =    Set Variable    Hello World from file!
	Create File  schrkd_input.msg    ${ifmsg} ${ifmsg} ${ifmsg}
	PyMQI.Put Message From File    schrkd_input.msg    %{ENV}.SVC1.REPLY
	PyMQI.Put Message From File    schrkd_input.msg    %{ENV}.SVC1.REPLY
	PyMQI.Put Message From File    schrkd_input.msg    %{ENV}.SVC1.REPLY
	PyMQI.Get All Messages Into File    %{ENV}.SVC1.REPLY    schrkd_output.msg
	Log    Message got back from queue into file:                                             console=yes
	${File} =    Get File    schrkd_output.msg
	@{list} =    Split to lines  ${File}     
	:FOR    ${line}    IN    @{list}
	\   Log     ${line}	                                                                      console=yes
	PyMQI.Purge Queue    %{ENV}.SVC1.REPLY

Test10
	[Documentation]    Disconnect from queue manager
	Log     Disconnect from queue manager                                                     console=yes
	PyMQI.Disconnect
