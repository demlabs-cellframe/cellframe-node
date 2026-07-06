{
  "network": {
    "name": "{{ network_name | default('stagenet') }}",
    "network_id": "{{ network_id | default('0x1234') }}",
    "consensus": "chipchain",
    "native_ticker": "{{ native_ticker | default('TCELL') }}"
  },
  "topology": {
    "root_nodes": {
      "count": 5,
      "role": "root",
      "consensus_participation": true,
      "is_seed_node": true,
      "balancer_enabled": true,
      "description": "Root nodes - ChipChain consensus validators for zerochain (3/5 consensus)"
    },
    "master_nodes": {
      "count": 3,
      "role": "master",
      "consensus_participation": true,
      "is_seed_node": false,
      "description": "Master validator nodes - ChipChain consensus participants for mainchain"
    },
    "full_nodes": {
      "count": 2,
      "role": "full",
      "consensus_participation": false,
      "is_seed_node": false,
      "description": "Full sync nodes - non-validator nodes"
    }
  },
  "network_settings": {
    "base_ip": "{{ base_ip | default('172.20.0.10') }}",
    "subnet": "{{ subnet | default('172.20.0.0/16') }}",
    "base_rpc_port": {{ base_rpc_port | default(8545) }},
    "base_p2p_port": {{ base_p2p_port | default(31337) }},
    "base_cf_port": {{ base_cf_port | default(7007) }},
    "base_http_port": {{ base_http_port | default(8079) }},
    "node_port": {{ node_port | default(8079) }}
  },
  "build": {
    "type": "{{ build_type | default('debug') }}",
    "cellframe_version": "{{ cellframe_version | default('latest') }}"
  },
  "consensus": {
    "type": "chipchain",
    "min_validators": 3,
    "new_round_delay": 15,
    "collecting_level": 10.0,
    "auth_certs_prefix": "{{ auth_certs_prefix | default(network_name ~ '.master') }}",
    "round_start_sync_timeout": 5,
    "round_attempts_max": 3,
    "round_attempt_timeout": 10,
    "consensus_debug": true
  },
  "balancer": {
    "enabled": true,
    "type": "http",
    "uri": "f0intlt4eyl03htogu",
    "max_links_response": 10,
    "request_delay": 20
  }
}
