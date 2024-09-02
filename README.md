# cellframe-node

[Cellframe Node usage Wiki](https://wiki.cellframe.net/en/soft)

## This guide will work on Debian/Ubuntu

### Build from sources:

#### Linux Prerequsites 

To successfully complete of the build, you need to have the following packages to be installed 
(packages are named as in Debian GNU/Linux 10 "buster", please found the corresponding packages for your distribution):


* libsqlite3-dev
* libmagic-dev
* libz-dev
* traceroute
* build-essential
* cmake
* dpkg-dev
* debconf-utils

Please use the command below to install dependencies listed above
```
sudo apt-get install build-essential cmake dpkg-dev libz-dev libmagic-dev libsqlite3-dev traceroute debconf-utils xsltproc
```

#### MacOS Prerequsites 

Install latest XCode from App Store or directly from official Apple site.
Install Homebrew from brew.sh, if you have Apple Sillicon chipset pls setup it to /opt/homebrew as recommendent on the Homebrew site.
Then install cmake and sqlite
```
brew install cmake sqlite3 zlib
```

Generaly thats all what you need


#### Get all cellframe-node sources

This command fetch sources from gitlab and build them. 
  ```
  git clone https://gitlab.demlabs.net/cellframe/cellframe-node.git --recursive
  ```

#### Build cellframe using cmake framework
Get into directory with cellframe-node and execute the following commands
  ```
  mkdir build
  cd build
  cmake ../
  make -j$(nproc)
  ```
*-j$(nproc)* nrpoc parameter depends on your machine capacity - number of processor cores.
As a result, you should be able to fine make files in your build folder which will be used by cpack command to create an installation package.

#### Build cellframe-node packages for MacOS
Right now you can just type ```make install``` and it will install all the files in your system at /Applications/CellFrameNode.app

#### Build cellframe-node package for Linux
Use the following command ```cpack``` from the build directory to create cellframe-node installation package:

```
cpack
```

##### Install from local package
If everyting went well you should be able to find the following file in your build folder ```cellframe-node-5.2-0-Debian-21.10-amd64-impish-dbg.deb``` 

Please use ```dpkg``` command to install it:
```
sudo dpkg -i ./cellframe-node-5.2-0-Debian-21.10-amd64-impish-dbg.deb
```

In some cases there is a following command required to be executed
```
sudo apt --fix-broken install
```

##### Install from DemLabs official public repository

* Create file /etc/apt/sources.list.d/demlabs.list with command ```sudo nano /etc/apt/sources.list.d/demlabs.list``` with one line below 

* For Debian 11:
  ```
  deb https://debian.pub.demlabs.net/public bullseye main
  ```
* For Debian 10:
  ```
  deb https://debian.pub.demlabs.net/public buster main
  ```
* For Debian 9:
  ```
  deb https://debian.pub.demlabs.net/public stretch main
  ```
* For Ubuntu 18 (Bionic):
  ```
  deb https://debian.pub.demlabs.net/public bionic main 
  ```
* Then download public signature and install it:
  ```
  wget https://debian.pub.demlabs.net/public/public-key.gpg
  sudo apt-key add public-key.gpg
  ```
* Then update your apt cache and install the package (apt-transport-https should be installed):
  ```
  sudo apt-get update
  sudo apt-get install cellframe-node
  ```

During installation it asks some questions

#### Debian package questions
All this could be changed after in configs


* Auto online
If true, the node goes online after he starts and then try to keep this state automatically 

* Debug mode
If true - produce more log output in files. Suggested to set ```true``` until the testing period 

* Debug stream headers
Dump stream headers in logs, set it ```true``` only if you want to get more debug information about stream packages passing through. Suggested ```false``` for almost everybody

* Accept connections
Enable/disable listening network address. Set ```false``` if you don't want to accept network connections to your node

* Server address
Network address used for listentning. Set ```0.0.0.0``` if you want to listen all network interfaces on your computer

* Server port (optional, usually don't ask)
Server port, 8079 by default but sometimes better to set it to ```80``` or ```443``` to masquarade service as web service. 

* Subzero: Enable network
Set ```true``` if you want to connect your node with ```Subzero``` (testnet)

* Mileena: Node type (role)
Select node type (or node role) from suggested list with short descriptions. By default suggested to select ```full``` (testnet)

* Minkowski: Enable network
Set ```true``` if you want to connect your node with ```Minkowski``` (KelVPN testnet)

* Bacbone: Enable network
Set ```true``` if you want to connect your node with ```Backbone``` (Mainnet)


### How to configure VPN service share
To share VPN service you must have a node with master role.
#### Node base configuration
Open ```/opt/cellframe-node/etc/cellframe-node.cfg``` with command ```sudo nano /opt/cellframe-node/etc/cellframe-node.cfg``` and find next section:

```
# VPN stream channel processing module
[srv_vpn]
#   Turn to true if you want to share VPN service from you node
enabled=true
#   List of local security access groups. Built in: expats,admins,services,nobody,everybody
network_address=10.11.12.0
network_mask=255.255.255.0
net=KelVPN
wallet_addr=
receipt_sign_cert=my_awesome_cert
```

Turn ```enabled``` parameter to ```true``` thats enable VPN service on your node. Then, the next lines ```network_address``` and ```network_mask``` usually you don't need to touch. Default configuration reserves network addresses for 254 connections at one time, if you have more - change network mask to smth like ```255.255.0.0``` and network address to ```10.11.0.0``` thats gives you 4095 local addresses. 
Thats important - all the addresses are local and used only inside virtual private network (VPN). For this address and mask also should be configured OS - should be present DNS server, switched on IP4 forwarding and configured NAT. Example of such configurations are below.
The next line ```net``` sets the name of the network on which the service will be shared.
Line ```wallet_addr``` sets the address of the wallet to which the payment for the service sharing will be sent.
Line ```receipt_sign_cert``` sets the name of the certificate for signing receipts. Must match the master node certificate.

#### Pricelist config
To set the price for VPN services, you need to create an order with the corresponding values. An example of creating an order will be presented below. If you do not create an order and enable VPN sharing the service will not start. To share service for free turn ```allow_free_srv``` parameter in ```[srv_vpn]``` section to ```true``` and create order with zero price.

#### DNS server install

Install DNS server, it could be any other than Bind9 but for example we will use exactly thats one - did we test this with any other? at a least a couple of others?

```sudo apt-get install bind9```

#### Switch on IPv4 forwarding 

Open ```/etc/sysctl.conf``` with command ```sudo nano /etc/sysctl.conf``` and find line 
```
# Uncomment the next line to enable packet forwarding for IPv4
#net.ipv4.ip_forward=1
```

Uncomment ```net.ipv4.ip_forward=1``` as the comment above suggests. Then after you've changed them and saved changes, implement them with:
```
sudo sysctl -p
```
Then after reboot they will be implemented automatically - do we need to specify a reboot command?


#### Configuring firewall with NAT

Easiest way is to install ```arno-iptables-firewall``` with the next command:
```
sudo apt-get install arno-iptables-firewall
```
It would ask next questions:

*  `Do you want to manage the firewall setup with debconf` answer `Yes`
*  `External network interfaces` answer with you network interface thats used for internet access. Usually its `eth0` or `wifi0` but could be different, examine you network configuration first.
*  `Open external TCP-ports` answer `8079` or what the port do you configured for cellframe node when it was installed
*  `Open external UDP-ports:` answer same as in previous
*  `Internal network interfaces` answer `tun0` if you haven't configured any other VPN servers. If they are - find what the tunnel number is biggest and list all of them here with your tunnel name (`tun<max number plus 1>` )
*  `Internal subnets ` here should be network_adddres/network_mask from VPN service configuration, ```10.11.12.0/255.255.255.0``` in our example
*  `Should be restarted` answer `No` becase we need some more configs

Now lets increase config ask level and reconfigure the package with the next command:
```
sudo dpkg-reconfigure -plow arno-iptables-firewall
``` 

For answers where you'll see right answers just press enter to skip them. Then the next questions should appears:
* `Is DHCP used on external interfaces? ` usually answer `Yes`, answer `No` only if you have static network configuration for external connections
* `Should the machine be pingable from the outside world?` answer `Yes` because we use pings for network speed measurements
* `Do you want to enable NAT? ` answer `Yes`
* `Internal networks with access to external networks:` here you list internal networks again, ```10.11.12.0/255.255.255.0``` in our example
* `Should the firewall be (re)started now?` now answer `Yes` and have everything ready for routing


### How to run 

If the node is installed in your system you need only to check it if its runned on your system
```
  sudo service cellframe-node status
```
And if its not runned - start it. Start after reboot should be automaticaly executed.
```
  sudo service cellframe-node start
```

To stop it use the next command:
```
  sudo service cellframe-node stop
```

### How to publish service in network 


#### Obtain node address
First you need to publish you public IPv4 and/or IPv6 addresses (for current moment we support only IPv4)

```
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net minkowski get status
```

It should print smth like this
```
Network "minkowski" has state NET_STATE_SYNC_CHAINS (target state NET_STATE_ONLINE), active links 3 from 4, cur node address 374C::CEB5::6740::D93B
```

#### Publish IP address in nodelist

Look at the end of address, thats you node address, ```374C::CEB5::6740::D93B``` use it to update information about your node, as in example below:
```
sudo /opt/cellframe-node/bin/cellframe-node-cli node add -net minkowski -addr 374C::CEB5::6740::D93B -cell 0x0000000000000001 -ipv4 5.89.17.176
```

Here is cell `0x0000000000000001` used by default until we haven't finished cell autoselection. Then ipv4 address is `5.89.17.176` replace it with your public IPv4 address. Same could be added ipv6 address with argument `-ipv6`


#### Create order for VPN service 

To say world that you have VPN service you need to place order. First lets see the market, what orders are already present:
```
sudo /opt/cellframe-node/bin/cellframe-node-cli net_srv -net KelVPN order find -srv_uid 0x0000000000000001 -direction sell
```

It should print list if you've syncronized well before (should happens automatically by default)
Anyway, lets create our order, changing price in it if you see in list thats market changed and you need to change prices as well.
Here is exmaple based on our pricelist in previous examples:
```sudo /opt/cellframe-node/bin/cellframe-node-cli net_srv -net KelVPN order create -direction sell -srv_uid 1 -price_unit SEC -price_token KEL -price 100 -units 3600 -node_addr 374C::CEB5::6740::D93B -cert my_awesome_cert -region Russia -continent Europe```

And then you just wait some for network synchronisation and your order will see everybody. Next restart your node. Provide the hash of your order to the network administrator so that your node appears in the clients list of servers.


Description of arguments
* ```-direction``` buy or sell, for VPN service publishing it must be ```sell```
* ```-srv_uid``` Service UID, for VPN service set ```1```
* ```-price_unit``` Set SEC for Seconds
* ```-price_token``` Token ticker
* ```-units``` The number of units in one portion of the service, in this example 3600 seconds
* ```-price``` Price for the number of units specified in the parameter -units. In this example 100 datoshi for 3600 seconds of service. To share VPN service for free set this field to 0.
* ```-node_addr``` Address of node
* ```-cert``` Certificate of master node
* ```-region``` The region in which the node is located
* ```-continent```  The continent in which the node is located

More details about order operations you could find with call ```sudo /opt/cellframe-node/bin/cellframe-node-cli help net_srv```
More details about cellframe node commands in call ```sudo /opt/cellframe-node/bin/cellframe-node-cli help```

# SubZero testnet

## Create wallet and token request

1. Install node according instructions above.
2. Create wallet
   
```
    cellframe-node-cli wallet new -w subzero_wallet
    Wallet 'subzero_wallet' (type=sig_dil) successfully created
```

3. Get wallet address:
   
```
cellframe-node-cli wallet info -w subzero_wallet -net subzero 
addr: mJUUJk6Yk2gBSTjcDHXxAerggncSK7DP8ZViVG2zrtbuW6uiCtTvXXn9kdcoBadGeBiujC7VsfemGv5BLbq2zcxoCR8GVRKfCmLtaedd
network: subzero
balance: 0
```

4. Send wallet address and request for tCELL amount of money to telegram channel: t.me/cellframe_dev_en
5. Waiting for answer from admin and execute command for network chains and gdb syncronization:

```cellframe-node-cli net sync all -net subzero```

6. See wallet balance:
   
```
cellframe-node-cli wallet info -w subzero_wallet -net subzero 
wallet: subzero_wallet
addr: mJUUJk6Yk2gBSTjcDHXxAerggncSK7DP8ZViVG2zrtbuW6uiCtTvXXn9kdcoBadGeBiujC7VsfemGv5BLbq2zcxoCR8GVRKfCmLtaedd
network: subzero
balance:
	5500000.000000000 (5500000000000000) tCELL
```

## Balance replenishment 

If you want increase amount of tCell on your wallet, you can wrote about it to SubZero admin.

## Tokens transfer

1. You can transfer tokens from your wallet to other wallet. For doing this you need to know address of 2nd wallet. Execute command

```
cellframe-node-cli tx_create -net subzero -chain support -from_wallet subzero_wallet -to_addr rTDbDdeStfpodpLUevvYaxJBh2k739fjwusqtmAU72VoUCm88ERPw555jHXtrkoEGJfYEZ7Mmwssc3ajijG9eEqEZxV2FmZvYcvnAVZz -value 32100000
        transfer=Ok
        tx_hash=0x4E6D540F86CD46CBFA551F219A04BA2248FF474BB795EB5B2C524299458AD709
```

- to_addr - address of 2nd wallet (you can see it using command ```cellframe-node-cli wallet info -w <wallet_name> -net subzero ```)
- value - amount of tokens

2. Execute command for database syncing

```cellframe-node-cli net sync all -net subzero```

3. Waiting for a while root node have processed you request
4. Don't create more then one request on balance changing, until you get confirmation about processing current request. That requests will not be processed (it can be fixed in future)
      
and see your updated balance

```cellframe-node-cli wallet info -w subzero_wallet -net subzero``` 

# Node notes

1. Token declaration operations, executing on node client (token_decl command) will be approved manually.
2. Token emission operations (token_emit command) will be processing automatically only for token owners.
3. Transactions (tx_create command) will be automatically processing as usual.

#### Remove cellframe-node

In order to remove cellframe-node, use the following command
```
sudo apt-get remove cellframe-node
```
