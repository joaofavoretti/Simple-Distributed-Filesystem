import zmq
import json
import pickle
import re

CONSTS_FILE_PATH = "../consts.json"

COMMANDS = {
    "UPLOAD": "UPLOAD",
    "HELP": "HELP",
    "EXIT": "EXIT"
}

REGEXES = {
    "UPLOAD": r"^upload\s+((/?[a-zA-Z0-9]+)+(\.[a-zA-Z0-9]+)?)\s+(([a-zA-Z0-9]+)+(\.[a-zA-Z0-9]+)?)$",
    "HELP": r"^help$",
    "EXIT": r"^exit$"
}

def valid_command(command_str, command_type):
    return re.search(REGEXES[command_type], command_str)

def parse_command(command_str, command_type):
    if command_type == COMMANDS["UPLOAD"]:
        match = re.search(REGEXES[command_type], command_str)

        file_name_origin = match.group(1)
        file_name_dest = match.group(4)

        return (command_type, file_name_origin, file_name_dest)

def main():
    global context, CONSTS

    context = zmq.Context()

    CONSTS = json.load(open(CONSTS_FILE_PATH, "r"))

    MS_IPV4 = CONSTS['metadata-server']['ipv4']
    MS_PORT = CONSTS['metadata-server']['port']

    ms_sock = context.socket(zmq.REQ)
    ms_sock.connect(f"tcp://{MS_IPV4}:{MS_PORT}")

    while True:
        command_str = input("> ")

        if valid_command(command_str, COMMANDS["HELP"]):
            print("Commands:")
            print("upload <file_path_origin> <file_name_dest>")

        elif valid_command(command_str, COMMANDS["EXIT"]):
            print("Exiting...")
            break

        elif valid_command(command_str, COMMANDS["UPLOAD"]):
            _, file_name_origin, file_name_dest = parse_command(command_str, COMMANDS["UPLOAD"])
            
            print(f"Uploading {file_name_origin} as {file_name_dest}")

            LOCATION_TO_STORE_REQ = CONSTS['operation-codes']['LOCATION_TO_STORE_REQ']

            location_to_store_req = {
                "code": LOCATION_TO_STORE_REQ,
                "file-name": file_name_dest
            }

            ms_sock.send(pickle.dumps(location_to_store_req))

            location_to_store_res = pickle.loads(ms_sock.recv())

            if location_to_store_res["status"] != "OK":
                print("Could not find a place to store the file")
                continue

            sn_ipv4 = location_to_store_res["ipv4"] # Storage Node IPv4
            sn_port = CONSTS['storage-nodes']['port']   # Storage Node Port

            print(f"Found a place to store the file: {sn_ipv4}:{sn_port}")

            sn_sock = context.socket(zmq.REQ)   # Storage Node Socket
            sn_sock.connect(f"tcp://{sn_ipv4}:{sn_port}")

            UPLOAD_FILE_REQ = CONSTS['operation-codes']['UPLOAD_FILE_REQ']

            upload_file_req = {
                "code": UPLOAD_FILE_REQ,
                "file-name": file_name_dest,
                "file-content": open(file_name_origin, "rb").read()
            }

            sn_sock.send(pickle.dumps(upload_file_req))


        else:
            print("Invalid command")


if __name__ == "__main__":
    main()
