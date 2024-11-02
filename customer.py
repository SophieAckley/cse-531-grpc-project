import grpc
import example_pb2
import example_pb2_grpc
import time

class Customer:
    def __init__(self, id, events):
        # Unique ID of the Customer
        self.id = id
        # Events from the input
        self.events = events
        # A list of received messages used for debugging purpose
        self.recvMsg = []
        # Stub for gRPC communication
        self.stub = None

    def createStub(self):
        """Creates a stub to communicate with the bank branch server."""
        # Connect to the branch server assigned to this customer ID
        channel = grpc.insecure_channel(f'localhost:{50000 + self.id}')
        self.stub = example_pb2_grpc.RPCStub(channel)

    def executeEvents(self):
        """Executes each event in the list and sends it to the branch server."""
        # Ensure the stub is created
        if not self.stub:
            self.createStub()

        # Process each event in the event list
        for event in self.events:
            # Build the request based on the event type and parameters
            request = example_pb2.Request(
                id=event['id'],
                interface=event['interface'],
                money=event.get('money', 0)  # Default money to 0 if not provided
            )

            # Send the request and handle the response
            if event['interface'] == 'query':
                response = self.stub.MsgDelivery(request)
                self.recvMsg.append({
                    "interface": "query",
                    "balance": response.balance
                })
            elif event['interface'] in ['deposit', 'withdraw']:
                response = self.stub.MsgDelivery(request)
                self.recvMsg.append({
                    "interface": event['interface'],
                    "result": response.result
                })

            # Sleep briefly to allow for sequential processing and propagation
            time.sleep(0.5)

        return self.recvMsg
