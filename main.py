import json
import time
from concurrent import futures
from branch import Branch, serve
from customer import Customer

def run_branch(branch_data):
    branch = Branch(branch_data['id'], branch_data['balance'], [b['id'] for b in branches])
    serve(branch)

def run_customer(customer_data):
    customer = Customer(customer_data['id'], customer_data['events'])
    return customer.executeEvents()

if __name__ == '__main__':
    # Read input data
    with open('input.json', 'r') as f:
        data = json.load(f)

    # Separate branch and customer data
    branches = [item for item in data if item['type'] == 'branch']
    customers = [item for item in data if item['type'] == 'customer']

    # Start branch processes
    executor = futures.ThreadPoolExecutor(max_workers=len(branches))
    branch_futures = [executor.submit(run_branch, branch) for branch in branches]
    
    # Delay to allow branch servers to initialize fully
    time.sleep(2)

    # Execute each customer’s events in sequence with delays between customers
    output = []
    for customer in customers:
        result = run_customer(customer)
        output.append({"id": customer['id'], "recv": result})
        
        # Short delay to ensure branches have synchronized before the next customer runs
        time.sleep(1)

    # Write output to file
    with open('output.json', 'w') as f:
        json.dump(output, f, indent=2)

    # Ensure all branch processes complete
    for future in branch_futures:
        future.result()

    print("All processes completed. Output written to output.json.")
