import grpc
import example_pb2
import example_pb2_grpc
import time

class Customer:
    def __init__(self, id, events):
        self.id = id
        self.events = events
        self.recvMsg = list()
        self.stub = None

    def createStub(self):
        # 创建与分支通信的stub
        channel = grpc.insecure_channel(f'localhost:{50000 + self.id}')
        self.stub = example_pb2_grpc.RPCStub(channel)

    def executeEvents(self):
        if not self.stub:
            self.createStub()

        for event in self.events:
            request = example_pb2.Request(
                id=event['id'],
                interface=event['interface'],
                money=event.get('money', 0)
            )

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
            
            # Sleep for a short time to ensure sequential execution and allow propagation to complete.
            time.sleep(0.5)

        return self.recvMsg
