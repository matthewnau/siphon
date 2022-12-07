#!flask/bin/python
from siphon import app
if __name__ == '__main__':
	app.run(host='192.168.1.2',port=80,debug=True)
	#This sets the server to the ip of the computer, not adding it makes it loopback.
	#To make a specific ip, set it statically on here such as host='172.16.31.24.'
	#You can change the port.