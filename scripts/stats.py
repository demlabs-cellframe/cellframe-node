#!/usr/bin/env python3
# -*- coding: utf-8 -*- 


"""
Requirements:
    pip3 install paramiko
    pip3 install pandas

    grep in PATH
"""

import os
import io
import re
import sys
import json
import paramiko
import numpy
import pandas as pd
from subprocess import Popen, PIPE
from datetime import datetime


def make_regex():
    log_levels = [
        "INF",
        " \\* ",
        "ERR",
        "ATT",  # For restart detection
        #"DBG",
    ]
    categories = [
        "main",
        "chain_net",
        "dap_chain_net_srv_vpn",
        "dap_chain_net_srv_vpn_cdb_auth",
    ]
    log_levels_str = "|".join(log_levels)
    categories_str = "|".join(categories)

    return "\\[(%s)\\] \\[(%s)\\]" % (log_levels_str, categories_str)


def string_to_datetime(date_string):
    dt = datetime.strptime(date_string, '%m/%d/%y-%H:%M:%S')
    return numpy.datetime64(dt)


def parse_log(log_stream):
    datetime_pattern =       re.compile(r"\[(\d\d/\d\d/\d\d-\d\d:\d\d:\d\d)\]")
    mode_pattern =           re.compile(r"\[(\d\d/\d\d/\d\d-\d\d:\d\d:\d\d)\] \[ATT\] \[main\] \*\*\* (DEBUG|NORMAL) MODE \*\*\*")
    node_address_pattern =   re.compile(r"\[(\d\d/\d\d/\d\d-\d\d:\d\d:\d\d)\] \[ \* \] \[chain_net\] Parse node addr ([\d\w:]{22}) successfully")
    is_cdb_pattern =         re.compile(r"\[(\d\d/\d\d/\d\d-\d\d:\d\d:\d\d)\] \[ \* \] \[main\] Central DataBase \(CDB\) is initialized")
    cdb_login_pattern =      re.compile(r"\[(\d\d/\d\d/\d\d-\d\d:\d\d:\d\d)\] \[INF\] \[dap_chain_net_srv_vpn_cdb_auth\] Login: Successfuly logined user")
    cdb_register_pattern =   re.compile(r"\[(\d\d/\d\d/\d\d-\d\d:\d\d:\d\d)\] \[ \* \] \[dap_chain_net_srv_vpn_cdb_auth\] Registration: new user")
    node_connected_pattern = re.compile(r"\[(\d\d/\d\d/\d\d-\d\d:\d\d:\d\d)\] \[ \* \] \[chain_net\] Connected link")
    vpn_connect_pattern =    re.compile(r"\[(\d\d/\d\d/\d\d-\d\d:\d\d:\d\d)\] \[ \* \] \[dap_chain_net_srv_vpn\] VPN client address ([\d\.]+) leased")
    vpn_disconnect_pattern = re.compile(r"\[(\d\d/\d\d/\d\d-\d\d:\d\d:\d\d)\] \[DBG\] \[dap_chain_net_srv_vpn\] Unlease address ([\d\.]+)")

    def extract_datetime(log_Line):
        m = datetime_pattern.match(log_Line)
        if m:
            return string_to_datetime(m.groups()[0])

    def on_cbd_string(match, info):
        info["is_cdb"] = True

    def on_node_address_string(match, info):
        node_address = match.groups()[1]
        info["node_address"] = node_address

    def on_login_string(match, info):
        dt_str = match.groups()[0]
        dt = string_to_datetime(dt_str)
        info["cdb_logins"].append(dt)

    def on_register_string(match, info):
        dt_str = match.groups()[0]
        dt = string_to_datetime(dt_str)
        info["cdb_registrations"].append(dt)

    def on_node_connection_string(match, info):
        dt_str = match.groups()[0]
        dt = string_to_datetime(dt_str)
        info["node_connections"].append(dt)

    def on_vpn_connect_string(match, info):
        dt_str = match.groups()[0]
        dt = string_to_datetime(dt_str)
        some_id = match.groups()[1]
        info["connection_dates"].append(dt)
        info["connection_ids"].append(some_id)

    def on_vpn_disconnect_string(match, info):
        dt_str = match.groups()[0]
        dt = string_to_datetime(dt_str)
        some_id = match.groups()[1]
        info["disconnection_dates"].append(dt)
        info["disconnection_ids"].append(some_id)

    actions = [
        (is_cdb_pattern, on_cbd_string),
        (node_address_pattern, on_node_address_string),
        (cdb_login_pattern, on_login_string),
        (cdb_register_pattern, on_register_string),
        (node_connected_pattern, on_node_connection_string),
        (vpn_connect_pattern, on_vpn_connect_string),
        (vpn_disconnect_pattern, on_vpn_disconnect_string),
    ]

    print("Parsing logs")

    data = []
    current_info = None
    for line in log_stream:
        if mode_pattern.match(line) is not None:
            if current_info is not None:
                data.append(current_info)
            current_info = {
                "is_cdb": False,
                'node_address': '__UNKNOWN__',
                "cdb_logins": [],
                "cdb_registrations": [],
                "node_connections" : [],
                "connection_dates" : [],
                "connection_ids": [],
                "disconnection_dates" : [],
                "disconnection_ids": [],
            }
        else:
            for pattern, action in actions:
                m = pattern.match(line)
                if m is not None:
                    action(m, current_info)
    if current_info:
        data.append(current_info)

    print("Done parsing logs")

    return data

def local_run(log_path):
    regex_str = make_regex()
    proc = Popen(["grep", "-E", regex_str, log_path], stdout=PIPE, stderr=PIPE, stdin=PIPE)

    proc.stdin.close()

    data = parse_log(io.TextIOWrapper(proc.stdout))

    proc.wait()

    if proc.returncode != 0:
        print("Error code:", proc.returncode)
        print("Error msg:", proc.stderr.read())

    return proc.returncode, data


def make_filtering_cmd(log_path):
    regex_str = make_regex()
    return 'grep -E "%s" "%s"' % (regex_str, log_path)


def remote_run(log_path, server, username, password):
    cmd = make_filtering_cmd(log_path)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username, password=password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    ssh_stdin.close()

    data = parse_log(ssh_stdout)

    # TODO: error check?
    errcode = 0
    error_string = ssh_stderr.read()
    if error_string:
        print("Errors:", error_string)

    ssh.close()

    return errcode, data


def count_datetime_list(data, list_name):
    count_label = 'count'

    # Step #0: Filter irrelevant data out
    filtered_data = filter(lambda x: len(x[list_name]) > 0, data)

    # Step #1: Make dataframes
    dicts = map(lambda x: {'node_address': x['node_address'], list_name: x[list_name]}, filtered_data)
    dataframes = list(map(lambda x: pd.DataFrame(data=x), dicts))

    if len(dataframes) == 0:
        return []
    elif len(dataframes) == 1:
        df = dataframes[0]
    else:
        df = pd.concat(dataframes)

    # Step #2: Calculate stats
    days = df[list_name].dt.floor('D')
    count_by_day = df.groupby(['node_address', days]).count()
    count_by_day = count_by_day.rename(columns={list_name: count_label}).reset_index()

    months = count_by_day[list_name].dt.month_name()
    month_groups = count_by_day.groupby(['node_address', months])[count_label]

    result = month_groups.agg(['min', 'median', 'max'])
    result = result.reset_index().rename(columns={list_name: 'month'})

    # total
    result_total = count_by_day.groupby([months])[count_label].agg(['min', 'median', 'max'])
    result_total = result_total.reset_index().rename(columns={list_name: 'month'})
    result_total.insert(0, 'node_address', ['      ALL NODES      '])

    return result_total.append(result)


def duration_for_paired_events(data, left_dates_column, left_id_column, right_dates_column, right_id_column):
    count_label = 'count'

    filtered_data = list(filter(lambda x: len(x[left_dates_column]) > 0 and len(x[right_dates_column]) > 0, data))

    # TODO: check inconsistent data (if colum length != id length)

    dicts_left = map(lambda x: {'node_address': x['node_address'], left_dates_column: x[left_dates_column], left_id_column: x[left_id_column]}, filtered_data)
    dicts_right = map(lambda x: {'node_address': x['node_address'], right_dates_column: x[right_dates_column], right_id_column: x[right_id_column]}, filtered_data)
    dataframes_left = map(lambda x: pd.DataFrame(data=x), dicts_left)
    dataframes_right = map(lambda x: pd.DataFrame(data=x), dicts_right)

    # merging (joining)
    dataframes = []
    for df_left, df_right in zip(dataframes_left, dataframes_right):
        df = pd.merge(df_left, df_right, left_on=['node_address', left_id_column], right_on=['node_address', right_id_column])
        durations = map(lambda lr: (lr[1] - lr[0]).total_seconds(), zip(df[left_dates_column], df[right_dates_column]))
        df['durations'] = list(durations)
        df_small = df.drop([left_id_column, right_id_column, right_dates_column], axis=1)
        dataframes.append(df_small)

    if len(dataframes) == 0:
        return [], []
    if len(dataframes) == 1:
        df = dataframes[0]
    else:
        df = pd.concat(dataframes)

    # Durations
    months = df[left_dates_column].dt.month_name()
    month_groups = df.groupby(['node_address', months])['durations']

    result = month_groups.agg(['min', 'median', 'max'])
    result = result.reset_index().rename(columns={left_dates_column: 'month'})

    # total count
    result_total = df.groupby([months])['durations'].agg(['min', 'median', 'max'])
    result_total = result_total.reset_index().rename(columns={left_dates_column: 'month'})
    result_total.insert(0, 'node_address', ['      ALL NODES      '])

    return result_total.append(result)

def do_stats(data):
    def print_stats(label, stats):
        print()
        print()
        print(label)
        if len(stats) > 0:
            print(stats)
        else:
            print("NO DATA")

    cdb_data = list(filter(lambda x: x['is_cdb'], data))
    not_cdb_data = list(filter(lambda x: not x['is_cdb'], data))

    logins = count_datetime_list(cdb_data, 'cdb_logins')
    registrations = count_datetime_list(cdb_data, 'cdb_registrations')
    node_connections_cdb = count_datetime_list(cdb_data, 'node_connections')
    node_connections_not_cdb = count_datetime_list(not_cdb_data, 'node_connections')
    vpn_connection_count = count_datetime_list(not_cdb_data, 'connection_dates')
    #vpn_connection_durration = duration_for_paired_events(not_cdb_data, 'connection_dates', 'connection_ids', 'disconnection_dates', 'disconnection_ids')

    print_stats("[CDB] Authorization count:", logins)
    print_stats("[CDB] Registration count:", registrations)
    print_stats("[CDB] Node connections count:", node_connections_cdb)
    print_stats("[NOT CDB] Node connections count:", node_connections_not_cdb)
    print_stats("[NOT CDB] VPN connections count:", vpn_connection_count)
    #print_stats("[NOT CDB] VPN connections duration:", vpn_connection_durration)


def load_config():
    print("Loading config...")

    if not os.path.isfile("stats.cfg"):
        print("Config file 'stats.cfg' is missing.")
        exit(-1)

    with open("stats.cfg") as f:
        cfg = json.load(f)

    if "run" not in cfg:
        print('"run" key with value "local" or "remote" is missing')
        exit(-1)

    if cfg["run"] == "local":
        if "local_files" not in cfg:
            print('"local_files" key is missing')
            exit(-1)
    elif cfg["run"] == "remote":
        if "nodes" not in cfg:
            print('"nodes" key is missing')
            exit(-1)
        for node_info in cfg["nodes"]:
            for key in ["address", "username", "password", "logfile_path"]:
                if key not in node_info:
                    print('One of nodes does not contain', key, 'key')
                    exit(-1)
    else:
        print('"run" value must be "local" or "remote"')
        exit(-1)

    return cfg


def main():
    cfg = load_config()
    result_data = []

    if cfg["run"] == "remote":
        l = len(cfg["nodes"])
        for i, node_info in enumerate(cfg["nodes"]):
            print(i + 1, '/', l, "nodes")
            errcode, data = remote_run(node_info["logfile_path"], node_info["address"], node_info["username"], node_info["password"])
            if errcode == 0:
                result_data.extend(data)
    elif cfg["run"] == "local":
        l = len(cfg["local_files"])
        for i, log_path in enumerate(cfg["local_files"]):
            print(i + 1, '/', l, "files")
            errcode, data = local_run(log_path)
            if errcode == 0:
                result_data.extend(data)

    do_stats(result_data)


if __name__ == '__main__':
    main()


