import zmq
import netifaces
import os
import json
import socket
import pickle
import time
import random

DB_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), socket.gethostname())

CONSTS_FILE_PATH = "./consts.json"

ERROR_CODE = {
    "SIGN_IN_FAILED": -1,
    "SIGN_OUT_FAILED": -2,
    "OPERATION_CODE_ERROR": -3
}

def get_main_interface_ip():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        if interface == "lo":
            continue
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            return addrs[netifaces.AF_INET][0]["addr"]

def sign_in_metadata_server():
    global context, CONSTS

    MS_IPV4 = CONSTS['metadata-server']['ipv4']
    MS_PORT = CONSTS['metadata-server']['port']

    STORAGE_NODE_SIGN_IN_REQ = CONSTS['operation-codes']['STORAGE_NODE_SIGN_IN_REQ']
    STORAGE_NODE_SIGN_IN_RES = CONSTS['operation-codes']['STORAGE_NODE_SIGN_IN_RES']

    context = zmq.Context()

    ms_sock = context.socket(zmq.REQ)
    ms_sock.connect(f"tcp://{MS_IPV4}:{MS_PORT}")

    sign_in_req = {
        "code": STORAGE_NODE_SIGN_IN_REQ,
        "ipv4": get_main_interface_ip(),
        "file-list": set(os.listdir(DB_DIR))
    }
    ms_sock.send(pickle.dumps(sign_in_req))
    
    # Wait for reply from server with confirmation
    operation_res = pickle.loads(ms_sock.recv())

    if operation_res['code'] != STORAGE_NODE_SIGN_IN_RES:
        print("Expected sign in response from server, but got something else", flush=True)
        exit(ERROR_CODE["OPERATION_CODE_ERROR"])

    if operation_res['status'] != "OK":
        print("Sign in failed", flush=True)
        exit(ERROR_CODE["SIGN_IN_FAILED"])

    ms_sock.close()

def sign_out_metadata_server():
    global context, CONSTS

    MS_IPV4 = CONSTS['metadata-server']['ipv4']
    MS_PORT = CONSTS['metadata-server']['port']

    STORAGE_NODE_SIGN_OUT_REQ = CONSTS['operation-codes']['STORAGE_NODE_SIGN_OUT_REQ']
    STORAGE_NODE_SIGN_OUT_RES = CONSTS['operation-codes']['STORAGE_NODE_SIGN_OUT_RES']

    context = zmq.Context()

    ms_sock = context.socket(zmq.REQ)
    ms_sock.connect(f"tcp://{MS_IPV4}:{MS_PORT}")

    sign_out_req = {
        "code": STORAGE_NODE_SIGN_OUT_REQ,
        "ipv4": get_main_interface_ip()
    }
    ms_sock.send(pickle.dumps(sign_out_req))
    
    # Wait for reply from server with confirmation
    operation_res = pickle.loads(ms_sock.recv())

    if operation_res['code'] != STORAGE_NODE_SIGN_OUT_RES:
        print("Expected sign out response from server, but got something else", flush=True)
        exit(ERROR_CODE["OPERATION_CODE_ERROR"])

    if operation_res['status'] != "OK":
        print("Sign out failed", flush=True)
        exit(ERROR_CODE["SIGN_OUT_FAILED"])

    ms_sock.close()

def main():
    global context, CONSTS

    # Setup database directory
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    # Setup zmq context
    context = zmq.Context()

    CONSTS = json.load(open(CONSTS_FILE_PATH, "r"))

    UPLOAD_FILE_REQ = CONSTS['operation-codes']['UPLOAD_FILE_REQ']

    sign_in_metadata_server()

    SN_IPV4 = get_main_interface_ip()
    SN_PORT = CONSTS['storage-nodes']['port']

    sock = context.socket(zmq.REP)
    sock.bind(f"tcp://{SN_IPV4}:{SN_PORT}")

    while True:

        operation_req = pickle.loads(sock.recv())
        
        source = operation_req['ipv4'] if 'ipv4' in operation_req else 'Client App'
        print(f"""
        == Storage Node - Received Request ==
        Code: {operation_req['code']}
        Source: {source}
        File: {operation_req['file-name']}
        """, flush=True)

        if operation_req['code'] == UPLOAD_FILE_REQ:
            file_name = operation_req['file-name']
            file_path = os.path.join(DB_DIR, file_name)

            if os.path.exists(file_path):
                operation_res = {
                    "code": operation_req['code'],
                    "status": "FILE EXISTS"
                }
                sock.send(pickle.dumps(operation_res))
                continue

            with open(file_path, "wb") as file:
                file.write(operation_req['file-content'])

            operation_res = {
                "code": operation_req['code'],
                "status": "OK"
            }
            sock.send(pickle.dumps(operation_res))

        else:
            operation_res = {
                "code": operation_req['code'],
                "status": "ERROR"
            }
            sock.send(pickle.dumps(operation_res))


    sign_out_metadata_server()


    

if __name__ == "__main__":
    main()
