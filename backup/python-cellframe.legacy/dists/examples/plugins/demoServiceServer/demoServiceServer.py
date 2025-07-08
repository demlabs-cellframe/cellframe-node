from DAP.Core import logIt
from CellFrame.Network import Net, Service, ServiceUID

def requested(srv, usage_id, client_remote, data):
    logIt.info("[server] func requested")
    return 0

def response_success(srv, usage_id, client_remote, data):
    logIt.notice("[server] func response success")
    return 0

def response_error(srv, usage_id, client_remote, data):
    logIt.warning("[server] func response error")

def next_success(srv, usage_id, client_remote, data):
    logIt.notice("[server] func next success")
    return 0

def custom_data(srv, usage_id, client_remote, data):
    logIt.notice("[server] Input data: " + data.decode("utf-8"))
    return data


def init():
    logIt.notice("Init demoServer")
    ch_uid = ServiceUID(123)
    srv_object = Service(
        ch_uid,
        "py_service",
        requested,
        response_success,
        response_error,
        next_success,
        custom_data
    )
    return 0
