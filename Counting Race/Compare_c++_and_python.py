import subprocess
import time
import os

def compile_cpp():
    try:
        # Use clang++ for Mac (or g++ if available)
        compiler = 'clang++' if os.system('which clang++') == 0 else 'g++'
        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cpp_file = os.path.join(current_dir, 'Counting_C++.cpp')
        output_file = os.path.join(current_dir, 'counting_cpp')
        
        subprocess.run([compiler, cpp_file, '-o', output_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Compilation error: {e}")
        exit(1)

def run_cpp():
    try:
        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cpp_executable = os.path.join(current_dir, 'counting_cpp')
        
        result = subprocess.run([cpp_executable], capture_output=True, text=True)
        return float(result.stdout.split(':')[1].split()[0])
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"Error running C++ program: {e}")
        exit(1)

def run_python():
    try:
        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        python_file = os.path.join(current_dir, 'Counting_python.py')
        
        result = subprocess.run(['python', python_file], capture_output=True, text=True)
        return float(result.stdout.split(':')[1].split()[0])
    except subprocess.CalledProcessError as e:
        print(f"Error running Python program: {e}")
        exit(1)

def main():
    print("Compiling C++ program...")
    compile_cpp()
    
    print("\nRunning both programs...")
    print("-" * 40)
    
    # Run C++
    print("Running C++ version...")
    cpp_time = run_cpp()
    
    # Run Python
    print("Running Python version...")
    python_time = run_python()
    
    print("\nResults:")
    print("-" * 40)
    print(f"C++ Time:    {cpp_time:.2f} seconds")
    print(f"Python Time: {python_time:.2f} seconds")
    print(f"Difference:  {python_time - cpp_time:.2f} seconds")
    print(f"Python is {python_time/cpp_time:.1f}x slower than C++")

if __name__ == "__main__":
    main()
