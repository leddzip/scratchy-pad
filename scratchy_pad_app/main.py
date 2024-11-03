import scratchy_pad_app.api.message_pb2 as message_pb2
import scratchy_pad_app.api.message_pb2_grpc as message_pb2_grpc
import grpc

import logging

from concurrent import futures

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # logging.FileHandler('app.log'), # to configure with a property file
        logging.StreamHandler()
    ]
)


class ToggleService(message_pb2_grpc.ToggleServiceServicer):

    def __init__(self):
        self.logger = logging.getLogger("ToggleServiceServicer")

    def Toggle(self, request, context):
        try:
            self.logger.info(f"Received message: {request.appName}")
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return message_pb2.ToggleResponse(response="Error processing message")
        return message_pb2.ToggleResponse(response="Message received")


class Server:

    def __init__(self, toggle_service: ToggleService):
        self.toggle_service = toggle_service
        self.logger = logging.getLogger("Server")

    def server(self):
        grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        message_pb2_grpc.add_ToggleServiceServicer_to_server(self.toggle_service, grpc_server)

        # to configure using a property file
        local_socket = "unix:/tmp/scratchy-pad.sock"
        grpc_server.add_insecure_port(local_socket)
        self.logger.info(f"Starting server on {local_socket}")
        grpc_server.start()
        self.logger.info("Server started")
        grpc_server.wait_for_termination()


def run():
    toggle_service = ToggleService()
    server = Server(toggle_service)
    server.server()


if __name__ == "__main__":
    run()