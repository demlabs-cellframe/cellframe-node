{
  "network": {
    "name": "{{ network_name | default('stagenet') }}",
    "network_id": "{{ network_id | default('0x1234') }}",
    "consensus": "{{ consensus_type | default('esbocs') }}"
  },
  "topology": {
    "root_nodes": {
      "count": {{ root_nodes_count | default(3) }},
      "role": "root",
      "consensus_participation": true,
      "is_seed_node": true,
      "balancer_enabled": {{ balancer_enabled | default('true') | lower }},
      "description": "Root seed nodes - DAG-PoA validators for zerochain + ESBocs validators for main chain"
    },
    "master_nodes": {
      "count": {{ master_nodes_count | default(3) }},
      "role": "master",
      "consensus_participation": true,
      "is_seed_node": false,
      "description": "Master validator nodes - ESBocs consensus participants"
    },
    "full_nodes": {
      "count": {{ full_nodes_count | default(1) }},
      "role": "full",
      "consensus_participation": false,
      "is_seed_node": false,
      "description": "Full sync nodes - non-validator nodes for testing dynamic connection"
    }
  },
  "build": {
    "type": "{{ build_type | default('debug') }}",
    "cellframe_version": "{{ cellframe_version | default('latest') }}"
  },
  "network_settings": {
    "base_rpc_port": {{ base_rpc_port | default(8545) }},
    "base_p2p_port": {{ base_p2p_port | default(31337) }},
    "base_cf_port": {{ base_cf_port | default(7007) }},
    "base_http_port": {{ base_http_port | default(8079) }},
    "node_port": {{ node_port | default(8079) }},
    "base_ip": "{{ base_ip | default('172.20.0.10') }}",
    "subnet": "{{ subnet | default('172.20.0.0/16') }}"
  },
  "consensus": {
    "type": "{{ consensus_type | default('esbocs') }}",
    "min_validators": {{ min_validators | default(2) }},
    "new_round_delay": {{ new_round_delay | default(45) }},
    "collecting_level": {{ collecting_level | default(10.0) }},
    "auth_certs_prefix": "{{ auth_certs_prefix | default('stagenet.master') }}",
    "min_fee": "{{ min_fee | default('0.01') }}"
  },
  "balancer": {
    "enabled": {{ balancer_enabled | default('true') | lower }},
    "type": "{{ balancer_type | default('http') }}",
    "uri": "{{ balancer_uri | default('f0intlt4eyl03htogu') }}",
    "max_links_response": {{ max_links_response | default(10) }},
    "request_delay": {{ request_delay | default(20) }}
  },
  "features": {
    "monitoring": {{ monitoring_enabled | default('false') | lower }},
    "tests": {{ tests_enabled | default('false') | lower }},
    "crash_artifacts": {{ crash_artifacts_enabled | default('true') | lower }}
  }
}
