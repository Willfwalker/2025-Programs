import socket
import threading
from queue import Queue

def scan_port(target, port, open_ports):
    """Attempt to connect to a port, add to open_ports list if successful"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set timeout to 1 second
        result = sock.connect_ex((target, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    except:
        pass

def port_scanner():
    # Get user input
    target = input("Enter the target IP address: ")
    start_port = int(input("Enter the starting port: "))
    end_port = int(input("Enter the ending port: "))

    print(f"\nScanning {target} for open ports...\n")

    # Create a queue to hold the ports and a list for open ports
    port_queue = Queue()
    open_ports = []
    print(open_ports)

    # Add ports to the queue
    for port in range(start_port, end_port + 1):
        port_queue.put(port)

    # Create and start threads
    thread_list = []
    for _ in range(100):  # Use 100 threads for faster scanning
        thread = threading.Thread(target=worker, args=(target, port_queue, open_ports))
        thread_list.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in thread_list:
        thread.join()

    # Print results
    if open_ports:
        print("Open ports found:")
        for port in sorted(open_ports):
            print(f"Port {port} is open")
    else:
        print("No open ports found in the specified range.")

def worker(target, port_queue, open_ports):
    """Worker function for threads to process ports from the queue"""
    while True:
        try:
            port = port_queue.get_nowait()
            scan_port(target, port, open_ports)
            port_queue.task_done()
        except Queue.Empty:
            break

if __name__ == "__main__":
    port_scanner()
