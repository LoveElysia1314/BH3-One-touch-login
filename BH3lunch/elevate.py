import ctypes
import sys


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def elevate():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)


# 示例使用方法
if __name__ == "__main__":
    elevate()
    print("已成功提升为管理员权限运行")

# 其他程序import并使用


def run_with_elevation(function_to_run, *args, **kwargs):
    elevate()
    return function_to_run(*args, **kwargs)

# 使用示例


def sample_function(x, y):
    return x + y


if __name__ == "__main__":
    result = run_with_elevation(sample_function, 3, 4)
    print(f"Result: {result}")
