from grpc_tools import protoc
import os, shutil


PROTOFILE = "./resources/api/message.proto"

def _clean(location: str):
    print("cleaning up")
    try:
        if os.path.exists(location) and os.path.isdir(location):
            shutil.rmtree(location)
            print("cleaned")
        else:
            print(f"Location {location} does not exist or is not a directory")
    except Exception as e:
        print(f"Error cleaning up {location}: {e}")


def _create_init(location: str):
    print("creating init file")
    with open(f"{location}/__init__.py", "w") as _:
        # only there to create the empty file
        pass


def _fix_imports(file_path: str, old_import: str, new_import: str):
    with open(file_path, "r") as file:
        content = file.read()
    content = content.replace(old_import, new_import)
    with open(file_path, "w") as file:
        file.write(content)


def _generate_client():
    _clean("./scratchy_pad_client/api")
    print("generating for client")
    command = [
        "grpc_tools.protoc",
        "-I./resources",
        "--python_out=./scratchy_pad_client",
        "--grpc_python_out=./scratchy_pad_client",
        PROTOFILE
    ]
    protoc.main(command)
    _create_init("./scratchy_pad_client/api")
    print("client file generated")


def _generate_server():
    _clean("./scratchy_pad_app/api")
    print("generating for server")
    command = [
        "grpc_tools.protoc",
        "-I./resources",
        "--python_out=./scratchy_pad_app",
        "--grpc_python_out=./scratchy_pad_app",
        PROTOFILE
    ]
    protoc.main(command)
    _fix_imports(
        "./scratchy_pad_app/api/message_pb2_grpc.py",
        "from api import message_pb2 as api_dot_message__pb2",
        "from scratchy_pad_app.api import message_pb2 as api_dot_message__pb2")
    _create_init("./scratchy_pad_app/api")
    print("server file generated")


def generate():
    _generate_client()
    _generate_server()