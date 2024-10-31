import json
import time
from concurrent import futures
import grpc
import example_pb2
import example_pb2_grpc
from branch import Branch, serve
from customer import Customer

def run_branch(branch_data):
    branch = Branch(branch_data['id'], branch_data['balance'], [b['id'] for b in branches])
    serve(branch)

def run_customer(customer_data):
    customer = Customer(customer_data['id'], customer_data['events'])
    return customer.executeEvents()

if __name__ == '__main__':
    # 读取输入文件
    with open('input.json', 'r') as f:
        data = json.load(f)

    # 分离分支和客户数据
    branches = [item for item in data if item['type'] == 'branch']
    customers = [item for item in data if item['type'] == 'customer']

    # 启动分支进程
    executor = futures.ThreadPoolExecutor(max_workers=len(branches))
    branch_futures = [executor.submit(run_branch, branch) for branch in branches]

    # 等待分支进程启动
    time.sleep(2)

    # 按顺序执行客户事件
    output = []
    for customer in customers:
        result = run_customer(customer)
        output.append({"id": customer['id'], "recv": result})
        # 在客户之间添加短暂延迟,确保操作按顺序执行
        time.sleep(0.5)

    # 写入输出文件
    with open('output.json', 'w') as f:
        json.dump(output, f, indent=2)

    # 等待所有分支进程完成
    for future in branch_futures:
        future.result()

    print("All processes completed. Output written to output.json")