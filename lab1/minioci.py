#!/usr/bin/env python3
import os
import sys
import json
import ctypes

libc = ctypes.CDLL("libc.so.6", use_errno=True)

CLONE_NEWNS = 0x00020000
CLONE_NEWUTS = 0x04000000
CLONE_NEWPID = 0x20000000

MS_REC = 16384
MS_PRIVATE = 1 << 18

UTILITY_NAME = "minioci"


def die(msg):
    print("Ошибка", msg, file=sys.stderr)
    sys.exit(1)


def check_root():
    if os.geteuid() != 0:
        die("запусти программу через sudo")


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_dirs(container_id):
    base = f"/var/lib/{UTILITY_NAME}/{container_id}"
    upper = os.path.join(base, "upper")
    work = os.path.join(base, "work")
    merged = os.path.join(base, "merged")

    os.makedirs(upper, exist_ok=True)
    os.makedirs(work, exist_ok=True)
    os.makedirs(merged, exist_ok=True)

    return base, upper, work, merged


def unshare_namespaces():
    flags = CLONE_NEWNS | CLONE_NEWUTS | CLONE_NEWPID
    if libc.unshare(flags) != 0:
        err = ctypes.get_errno()
        die(f"unshare failed: {os.strerror(err)}")


def set_hostname(hostname):
    data = hostname.encode()
    if libc.sethostname(data, len(data)) != 0:
        err = ctypes.get_errno()
        die(f"sethostname failed: {os.strerror(err)}")


def make_mount_private():
    if libc.mount(None, b"/", None, MS_REC | MS_PRIVATE, None) != 0:
        err = ctypes.get_errno()
        die(f"mount private failed: {os.strerror(err)}")


def mount_overlay(lower, upper, work, merged):
    opts = f"lowerdir={lower},upperdir={upper},workdir={work}".encode()
    if libc.mount(b"overlay", merged.encode(), b"overlay", 0, opts) != 0:
        err = ctypes.get_errno()
        die(f"overlay mount failed: {os.strerror(err)}")


def mount_proc():
    os.makedirs("/proc", exist_ok=True)
    if libc.mount(b"proc", b"/proc", b"proc", 0, None) != 0:
        err = ctypes.get_errno()
        die(f"proc mount failed: {os.strerror(err)}")


def build_env(env_list):
    env = {}
    for item in env_list:
        if "=" in item:
            k, v = item.split("=", 1)
            env[k] = v
    if "PATH" not in env:
        env["PATH"] = "/bin:/sbin:/usr/bin:/usr/sbin"
    return env


def main():
    if len(sys.argv) != 3:
        print(f"Использование: sudo {sys.argv[0]} <id> <config.json>")
        sys.exit(1)

    check_root()

    container_id = sys.argv[1]
    config_path = sys.argv[2]

    config = load_config(config_path)

    hostname = config.get("hostname", "container")

    root = config.get("root", {})
    lowerdir = root.get("path")
    if not lowerdir:
        die("в config.json нет root.path")

    process = config.get("process", {})
    args = process.get("args")
    if not args:
        die("в config.json нет process.args")

    cwd = process.get("cwd", "/")
    env_list = process.get("env", ["PATH=/bin:/sbin:/usr/bin:/usr/sbin"])

    lowerdir = os.path.abspath(lowerdir)
    if not os.path.isdir(lowerdir):
        die(f"root.path не существует: {lowerdir}")

    base, upper, work, merged = make_dirs(container_id)

    #новые namespace
    unshare_namespaces()

    #изоляция mount namespace
    make_mount_private()

    #hostname из config.json
    set_hostname(hostname)

    #verlayfs
    mount_overlay(lowerdir, upper, work, merged)

    #после CLONE_NEWPID нужен fork,чтобы дочерний процесс стал PID=1
    pid = os.fork()

    if pid == 0:
        #child
        os.chroot(merged)
        os.chdir("/")

        mount_proc()

        try:
            os.chdir(cwd)
        except FileNotFoundError:
            die(f"cwd не существует внутри контейнера: {cwd}")

        env = build_env(env_list)
        os.execvpe(args[0], args, env)

    else:
        #parent
        _, status = os.waitpid(pid, 0)

        if os.WIFEXITED(status):
            sys.exit(os.WEXITSTATUS(status))
        elif os.WIFSIGNALED(status):
            sys.exit(128 + os.WTERMSIG(status))
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()