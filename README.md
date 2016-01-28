Demo NAO program
================

This is the program for NAO used in the FOSDEM talk.

How to use
==========

* Clone this repository recursively:
```
$ git clone --recursive git@github.com:Alidron/demo-nao.git
```
* Copy some files on the robot:
```
scp -r alidron-env naoutil demo-alidron-nao.py start-demo-alidron-nao.sh nao@nao.local:
```
* Load the application from `Behaviour/AlidronDemo` in Choregraphe, and install it on the robot.
* ssh on the robot and start the demo script:
```
$ ssh nao@nao.local
$ ./start-demo-alidron-nao.sh
```

License and contribution policy
===============================

This project is licensed under LGPLv3.

To contribute, please, follow the [C4.1](http://rfc.zeromq.org/spec:22) contribution policy.
