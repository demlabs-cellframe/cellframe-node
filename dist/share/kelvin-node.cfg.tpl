[network]
listen_address=0.0.0.0
listen_port=8003

[resources]
pid_path=/opt/kelvin-node/run/kelvin-node.pid
log_file=/opt/kelvin-node/log/kelvin-node.log

[www]
www_root=/opt/dapserver/www
main_url_enabled=true

[configure]
TTL_session_key=600

[blockchain]
network-type=testing
wallets=/opt/kelvin-node/var/wallets/
default-wallet=defaul
t