import grpc
import example_pb2
import example_pb2_grpc

class Branch(example_pb2_grpc.RPCServicer):

    def __init__(self, id, balance, branches):
        # Unique ID of the Branch
        self.id = id
        # Replica of the Branch's balance
        self.balance = balance
        # List of process IDs of the branches
        self.branches = branches
        # Client stubs for inter-branch communication
        self.stubList = []

        # Initialize gRPC stubs for communication with other branches
        for branch_id in branches:
            if branch_id != self.id:
                channel = grpc.insecure_channel(f'localhost:{50000 + branch_id}')
                stub = example_pb2_grpc.RPCStub(channel)
                self.stubList.append(stub)
        
        # List of received messages for debugging
        self.recvMsg = []

    def MsgDelivery(self, request, context):
        """Processes incoming requests and directs them to the appropriate method."""
        self.recvMsg.append(request)

        if request.interface == "query":
            return self.Query(request)
        elif request.interface == "deposit":
            return self.Deposit(request)
        elif request.interface == "withdraw":
            return self.Withdraw(request)
        elif request.interface == "propagate_deposit":
            return self.Propagate_Deposit(request)
        elif request.interface == "propagate_withdraw":
            return self.Propagate_Withdraw(request)
        else:
            # Return an error response if the request type is invalid
            return example_pb2.Response(interface="error", result="Invalid interface")

    def Query(self, request):
        """Handles balance query requests."""
        return example_pb2.Response(interface="query", balance=self.balance)

    def Deposit(self, request):
        """Handles deposit requests and propagates the deposit to other branches."""
        if request.money < 0:
            return example_pb2.Response(interface="deposit", result="fail")

        # Update balance
        self.balance += request.money
        # Propagate deposit to other branches
        self.Propagate_To_Branches("propagate_deposit", request.money)
        return example_pb2.Response(interface="deposit", result="success")

    def Withdraw(self, request):
        """Handles withdrawal requests and propagates the withdrawal to other branches."""
        if request.money < 0 or self.balance < request.money:
            return example_pb2.Response(interface="withdraw", result="fail")

        # Update balance
        self.balance -= request.money
        # Propagate withdrawal to other branches
        self.Propagate_To_Branches("propagate_withdraw", request.money)
        return example_pb2.Response(interface="withdraw", result="success")

    def Propagate_Deposit(self, request):
        """Processes deposit propagation from another branch."""
        self.balance += request.money
        return example_pb2.Response(interface="propagate_deposit", result="success")

    def Propagate_Withdraw(self, request):
        """Processes withdrawal propagation from another branch."""
        self.balance -= request.money
        return example_pb2.Response(interface="propagate_withdraw", result="success")

    def Propagate_To_Branches(self, interface, money):
        """Sends deposit or withdrawal propagation requests to other branches."""
        for stub in self.stubList:
            try:
                request = example_pb2.Request(interface=interface, money=money)
                stub.MsgDelivery(request)
            except grpc.RpcError as e:
                print(f"Error propagating to branch: {e.details()}")
