import zmq
import pickle
import json

CONSTS_FILE_PATH = "./consts.json"

def main():
    global context, CONSTS
    
    CONSTS = json.load(open(CONSTS_FILE_PATH, "r"))
    
    MS_IPV4 = CONSTS['metadata-server']['ipv4']
    MS_PORT = CONSTS['metadata-server']['port']

    STORAGE_NODE_SIGN_IN_REQ = CONSTS['operation-codes']['STORAGE_NODE_SIGN_IN_REQ']
    STORAGE_NODE_SIGN_OUT_REQ = CONSTS['operation-codes']['STORAGE_NODE_SIGN_OUT_REQ']
    LOCATION_TO_STORE_REQ = CONSTS['operation-codes']['LOCATION_TO_STORE_REQ']

    storage_nodes = {}

    context = zmq.Context()

    sock = context.socket(zmq.REP)
    sock.bind(f"tcp://{MS_IPV4}:{MS_PORT}")

    print('Server started...', flush=True)

    while True:
        
        operation_req = pickle.loads(sock.recv())

        source = operation_req['ipv4'] if 'ipv4' in operation_req else 'Client App'
        print(f"""
        == Metadata Server - Received Request ==
        Code: {operation_req['code']}
        IP Address: {source}
        """, flush=True)

        if operation_req["code"] == STORAGE_NODE_SIGN_IN_REQ:
            sign_in_req = operation_req

            storage_nodes[sign_in_req["ipv4"]] = {
                "status": "ON",
                "file-list": sign_in_req["file-list"]
            }

            print(f"Received request from {sign_in_req['ipv4']} with file list {sign_in_req['file-list']}", flush=True)
            
            STORAGE_NODE_SIGN_IN_RES = CONSTS['operation-codes']['STORAGE_NODE_SIGN_IN_RES']

            sign_in_res = {
                "code": STORAGE_NODE_SIGN_IN_RES,
                "status": "OK"
            }
            sock.send(pickle.dumps(sign_in_res))
        
        elif operation_req["code"] == STORAGE_NODE_SIGN_OUT_REQ:
            sign_out_req = operation_req

            storage_nodes[sign_out_req["ipv4"]] = {
                "status": "OFF",
                "file-list": []
            }

            print(f"Received request from {sign_out_req['ipv4']} to sign out", flush=True)

            STORAGE_NODE_SIGN_OUT_RES = CONSTS['operation-codes']['STORAGE_NODE_SIGN_OUT_RES']

            sign_out_res = {
                "code": STORAGE_NODE_SIGN_OUT_RES,
                "status": "OK"
            }
            sock.send(pickle.dumps(sign_out_res))
        
        elif operation_req["code"] == LOCATION_TO_STORE_REQ:
            
            fewer_files_num = 0
            fewer_files_ipv4 = None

            for ipv4, storage_node in storage_nodes.items():
                if storage_node["status"] == "ON":
                    if fewer_files_ipv4 == None:
                        fewer_files_ipv4 = ipv4
                        fewer_files_num = len(storage_node["file-list"])
                    elif len(storage_node["file-list"]) < fewer_files_num:
                        fewer_files_ipv4 = ipv4
                        fewer_files_num = len(storage_node["file-list"])

            LOCATION_TO_STORE_RES = CONSTS['operation-codes']['LOCATION_TO_STORE_RES']

            location_to_store_res = None

            if fewer_files_ipv4 == None:
                location_to_store_res = {
                    "code": LOCATION_TO_STORE_RES,
                    "status": "ERROR",
                }
            else:
                location_to_store_res = {
                    "code": LOCATION_TO_STORE_RES,
                    "status": "OK",
                    "ipv4": fewer_files_ipv4
                }
            
            sock.send(pickle.dumps(location_to_store_res))


        else:
            operation_res ={
                "code": operation_req['code'],
                "status": "ERROR"
            }
            sock.send(pickle.dumps(operation_res))

        
if __name__ == "__main__":
    main()