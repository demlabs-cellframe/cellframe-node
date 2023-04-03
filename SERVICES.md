# Configure your Cellframe node for sharing VPN service

## 1. Create a wallet
If you haven't created a wallet yet, you should do that now as the payments from sharing your connection for VPN service will be paid to your wallet. Open terminal and type in the following command:
```
cellframe-node-cli wallet new -w my_wallet
```
Where `my_wallet` is the name you want to use on your own wallet.

## 2. Install DNS
You need to have DNS server installed and configured on your system. Install bind9 with the following command:
```
apt -y install bind9
```
**NOTE: You don't need to do any type of configuration to your DNS server**

## 3. Set up IPv4 forwarding
To enable IPv4 forwarding, you need to edit `sysctl.conf` file. Open the file in nano with the command `sudo nano /etc/sysctl.conf` and find the following line:
```
#net.ipv4.ip_forward=1
```
Uncomment the line, so it will look like this:
```
net.ipv4.ip_forward=1
```
**NOTE: If your configuration file is missing this line for some reason, you may add it manually to the end of the file.**

Then press Ctrl+X, answer Y to "Save modified buffer" and press Enter. After you have saved the file, enable the new settings with command:
```
sysctl -p
```

## 4. Set up your Cellframe node for VPN sharing
For enabling VPN service share in Cellframe node, we need to edit Cellframe node configuration file. Use the command `sudo nano /opt/cellframe-node/etc/cellframe-node.cfg` to edit the configuration file with nano text editor and find the following part:
```
[srv_vpn]
#   Turn to true if you want to share VPN service from you node 
enabled=true
debug_more=false
# Grace period for service , 60 second by default
#grace_period=60 
#   List of loca security access groups. Built in: expats,admins,services,nobod>
network_address=10.11.12.0
network_mask=255.255.255.0
pricelist=[kelvpn-minkowski:100:KEL:3600:SEC:my_wallet]
```

**NOTE: This example has already been modified with KelVPN Minkowski settings. Your settings might look a bit different.**

Turn `enabled` parameter from `false` to `true` for enabling the VPN service sharing on your node. Default configuration for `network_address=10.11.12.0` and `network_mask=255.255.255.0` reserves 254 local addresses for VPN sharing and it should be enough, so those lines can stay untouched. However, you should keep these addresses in mind as they will be required in the firewall configuration part.

The `pricelist` line, on the other hand, needs some configuration. `pricelist` has a list of values which are split with colon (:).

1. `kelvpn-minkowski` Chain network name where token is issued. 
2. `100` is the price per unit
3. `KEL` Token ticker thats will be used for payments
4. `3600` units which has a price of 0.00001 like in our example above
5. `SEC` is a unit type. For ex:SEC for seconds, MB for megabytes or DAY for days
6. `mywallet` is the wallet name which you have created for receiving payments to.

In this particular configuration we see that the unit value is `3600`, price per unit is `100` and unit type is `SEC`. Therefore as 3600 seconds makes 1 hour, the price for 1 hour would be 100 KEL. Another example with megabytes would be with the following configuration: `kelvpn-minkowski:100:KEL:30:MB:mywallet0`, which shows you that for every 30MB of data, the payment would be 100 KEL.

After the consumption of each portion (time or amount of data), a check is issued for the client.

Each masternode owner himself determines how much he wants for the traffic provided. The client sees the receipt issued by the master node and signs it, if he agrees with the tariff.

## 5. Configuring firewall with NAT (Network Address Translation)
First of all, you need to figure out which network interface you are using for internet connection. To find that out, do `ip -brief address show` command in terminal to see what is your current network interface in use. The output could look something like this:
```
lo               UNKNOWN        127.0.0.1/8 ::1/128 
wlo1             UP             192.168.8.128/24 fd0c:8fff:407b:1f00:2fb1:faee:31ea:eeab/64 fd0c:8fff:407b:1f00:3126:6043:318a:924a/64 fe80::c4a4:34d2:657d:275d/64 
docker0          DOWN           172.17.0.1/16
```
On this particular output, we see that our network interface in use is `wlo1`.

You also need to check the available tunnel devices from your system with the command `ls /dev/net`. 

If you have only one `tun` device available on your system, you should use `tun0` as the tunnel device when configuring the firewall. However, if you have configured another VPN server for your system, you might have multiple tunnel devices available. So for example, if you have `tun, tun0, tun1, tun2` devices when doing the `ls /dev/net/` command, you should use `tun3` on the firewall configuration part.

## 6. Installing and configuring firewall

After you have checked your network interface and tunnel you will be using, it's time to configure Linux firewall (iptables). One easy way to configure that is to use `arno-iptables-firewall`.

I you have installed it already, you can simply reconfigure it with `sudo dpkg-reconfigure arno-iptables-firewall`. If you need to install it, just type in the command `sudo apt -y install arno-iptables-firewall` and it will ask you a few questions:

* Do you want to manage the firewall setup with debconf? 
  * You should answer yes.
* External network interfaces:
  * This is the network interface you checked with `ip -brief address show` command. In my case, that's my WiFi interface `wlo1`.
* Open external TCP-ports:
  * Cellframe node uses port 8079 so we'll use that. **NOTE: If you're running other services on your computer (for example like SSH port 22), you should open those ports too to access them!**
* Open external UDP-ports:
  * Same answer as above, 8079.
* Internal network interfaces:
  * Tunnel device which you will use. e.g. tun0.
* Internal subnets:
  * Network setting for internal subnets. IP / Mask is the same from `cellframe-node.cfg` VPN configuration part: `10.11.12.0/255.255.255.0`.

Now, the configurator will now ask you twice "Should the firewall be (re)started now?" Answer "No", as we need to continue the configuration. Next, we need to reconfigure `arno-iptables-firewall` with lower priority to set some other settings we need. Use command `sudo dpkg-reconfigure -plow arno-iptables-firewall` and you will be asked a few new questions:

**NOTE: When installing the package for the first time, installer will ask some same questions which you have already answered, you can safely press enter on these questions for moving forward.**

* Is DHCP used on external interfaces?
  * This is probably "Yes", if you are behind a router. However, if you're running on VPS, they usually use static IP. You should ask from your service provider, if you're unsure about this.
* Should the machine be pingable from outside the world?
  * Answer "Yes". Ping is used for measuring network speed.
* Do you want to enable NAT?
  * Answer "Yes", to access from internal network to Internet.
* Internal networks with access to external networks:
  * Use the same IP/Mask which are configured in `cellframe-node.cfg` VPN configuration: `10.11.12.0/255.255.255.0`.
* Should the firewall be (re)started now?
  * You can now safely answer "Yes" to restart the firewall.

## 6. Obtain your node address

First you need to publish you public IPv4 and/or IPv6 addresses (currently we only support IPv4). To get your public address in Mileena network, use the following command:
```
cellframe-node-cli net -net mileena get status
```
**NOTE: If `cellframe-node-cli` command is not recognized, it's possibly not added to your `$PATH`. If this happens, you can use it directly with the command `/opt/cellframe-node/bin/cellframe-node-cli`**

You should receive some information after you press enter:
```
Network "mileena" has state NET_STATE_ONLINE (target state NET_STATE_ONLINE), active links 4 from 3, cur node address 2B5E::139B::C995::6D71
```

No we can see that our node address in Mileena network is `2B5E::139B::C995::6D71`.

## 7. Publish IP address in node list

You can publish your own node address in node list with the following command:
```
cellframe-node-cli node add -net mileena -addr your_node_address -cell 0x0000000000000001 -ipv4 your_external_ip_address
```
Where `your_node_address` is the one which you received above (in this case: `2B5E::139B::C995::6D71`), and `your_external_ip_address` is your external IP address. Simple way to get your external IP address is to just Google "what is my IP".

So in this case, our command would look something like this:
```
cellframe-node-cli node add -net mileena -addr 2B5E::139B::C995::6D71 -cell 0x0000000000000001 -ipv4 109.240.91.130

```
***NOTE: Currently we use cell 0x0000000000000001 by default until autoselection of cell is implemented***

## 8. Create order for the VPN service

First take a look at the market and see what orders are already present with the following command:
```
cellframe-node-cli net_srv -net mileena order find -srv_uid 0x0000000000000001 -direction sell
```

It should print a similar list if you have synchronized your node (should happen automatically by default):
```
== Order 0xA9797360399BD75C0CA59F227ACF89AB1CF15088F1B092B0EE6B77AE2BD4B1BA ==
  version:          3
  direction:        SERV_DIR_SELL
  srv_uid:          0x0000000000000005
  price:            0.000000000000000001 (1)
  node_addr:        3E9E::B2C1::F2F2::7624
  node_location:    None - None
  tx_cond_hash:     0x0000000000000000000000000000000000000000000000000000000000000000
  ext:              0x0

== Order 0x6574FFA6C29166EA0E2F6D8B794EDF57E4F0DC3336EB343B8794C2803EB8B405 ==
  version:          3
  direction:        SERV_DIR_SELL
  srv_uid:          0x0000000000000005
  price:            0.000000000000000001 (1)
  node_location:    None - None
  tx_cond_hash:     0x0000000000000000000000000000000000000000000000000000000000000000
  ext:              0x0

== Order 0x2E633DEE16BCA16302F7C1FF238AE32C2ED8482B26A1EAB2EB1C7D91A8ED9E05 ==
  version:          3
  direction:        SERV_DIR_SELL
  srv_uid:          0x0000000000000005
  price:            0.000000000000000001 (1)
  node_location:    None - None
  tx_cond_hash:     0x0000000000000000000000000000000000000000000000000000000000000000
  ext:              0x0

```
Let's create our own order:
```
cellframe-node-cli net_srv -net mileena order create -direction sell -srv_uid 1 -srv_class PERM -price_unit 2 -price_token TMIL -price 100
```
Description of arguments:

* `-direction` is `buy` or `sell`, for VPN service publishing it has to be `sell`
* `-srv_uid` is the Service UID, for VPN service, set to 1
* `-price_unit`, set `2` for seconds, `1` for megabytes
* `-price_token` is the token ticker you would like to use
* `-price` is the price for one unit, price for one second in our example

**NOTE: You set price in configuration file for units, (3600 in our example) - With this command you set price for one single unit, one second for example.**

You can see more details about order operations with the command `cellframe-node-cli help net_srv`
