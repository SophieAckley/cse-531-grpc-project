import grpc
import example_pb2
import example_pb2_grpc
from concurrent import futures

class Branch(example_pb2_grpc.RPCServicer):

    def __init__(self, id, balance, branches):
        self.id = id
        self.balance = balance
        self.branches = branches
        self.stubList = list()
        self.recvMsg = list()
        
        # 创建与其他分支通信的 stubs
        for branch_id in self.branches:
            if branch_id != self.id:
                channel = grpc.insecure_channel(f'localhost:{50000 + branch_id}')
                stub = example_pb2_grpc.RPCStub(channel)
                self.stubList.append(stub)

    def MsgDelivery(self, request, context):
        self.recvMsg.append(request)
        
        if request.interface == "query":
            return self.Query(request)
        elif request.interface == "deposit":
            return self.Deposit(request)
        elif request.interface == "withdraw":
            return self.Withdraw(request)
        elif request.interface == "propagate_deposit":
            return self.Propogate_Deposit(request)
        elif request.interface == "propagate_withdraw":
            return self.Propogate_Withdraw(request)
        else:
            return example_pb2.Response(interface="error", result="Invalid interface")

    def Query(self, request):
        return example_pb2.Response(interface="query", balance=self.balance)

    def Deposit(self, request):
        # 更新当前分支的余额
        self.balance += request.money
        
        # 将存款操作传播到其他分支
        self.Propagate_To_Branches("propagate_deposit", request.money)
        
        return example_pb2.Response(interface="deposit", result="success")

    def Withdraw(self, request):
        if self.balance >= request.money:
            # 更新当前分支的余额
            self.balance -= request.money
            
            # 将取款操作传播到其他分支
            self.Propagate_To_Branches("propagate_withdraw", request.money)
            
            return example_pb2.Response(interface="withdraw", result="success")
        else:
            return example_pb2.Response(interface="withdraw", result="fail")

    def Propogate_Deposit(self, request):
        # 接收其他分支的存款传播请求并更新余额
        self.balance += request.money
        return example_pb2.Response(interface="propagate_deposit", result="success")

    def Propogate_Withdraw(self, request):
        # 接收其他分支的取款传播请求并更新余额
        self.balance -= request.money
        return example_pb2.Response(interface="propagate_withdraw", result="success")

    def Propagate_To_Branches(self, interface, money):
        # 将存款或取款操作传播到所有其他分支
        for stub in self.stubList:
            try:
                request = example_pb2.Request(interface=interface, money=money)
                stub.MsgDelivery(request)
            except Exception as e:
                print(f"Error propagating to branch: {e}")

def serve(branch):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    example_pb2_grpc.add_BankServiceServicer_to_server(branch, server)
    server.add_insecure_port(f'[::]:{50000 + branch.id}')
    server.start()
    server.wait_for_termination()
