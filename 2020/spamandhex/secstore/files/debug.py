#!/usr/bin/python3
import os
import sys
import random
import subprocess
import string
import shutil

class HashCash(object):
    def __init__(self, bits=28):
        import random, string
        self.rand = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
        self.bits = bits
        self.msg = 'Solve PoW with: hashcash -mqb{} {}'.format(bits, self.rand)

    def check(self, stamp):
        import hashlib
        assert stamp.startswith('1:')
        assert stamp.split(':')[3] == self.rand
        assert int(hashlib.sha1(stamp.encode()).hexdigest(), 16) < 2**(160-self.bits)

    @staticmethod
    def check_stdin(bits=28):
        import sys
        hc = HashCash(bits)
        print(hc.msg)
        sys.stdout.flush()
        hc.check(sys.stdin.readline().strip())


def main():
    os.system("./exploit/compile.sh")
    with open("./exploit/exploit", "rb") as f:
        data = f.read()
    os.system("rm -rf ./home")
    os.makedirs("./home/user/")
    shutil.copyfile("./app/initramfs.cpio.gz", "./initramfs.cpio.gz")
    with open("./home/user/exploit", "wb") as initramfs:
        initramfs.write(data)

    os.system("chmod 755 ./home/user/exploit && echo ./home/user/exploit | cpio -R +1000:+1000 -H newc -o | gzip -9 >> ./initramfs.cpio.gz");
    #os.system("chmod 755 ./init && echo ./init | cpio -R +1000:+1000 -H newc -o | gzip -9 >> ./initramfs.cpio.gz");
    print("Starting computer...")
    os.execvp("./app/qemu-system-aarch64",
            ["./app/qemu-system-aarch64",
            "-machine", "virt",
            "-cpu", "max",
            "-smp", "2",
            "-kernel", "./app/Image",
            "-initrd", "./initramfs.cpio.gz",
            "-m", "128m",
            "-nographic",
            "-nic", "none",
            "-append", "console=ttyAMA0 oops=panic",
            #"-append", "console=ttyAMA0 nokaslr",
            "-monitor", "/dev/null",
            "-d", "trace:pl666*"]
            )

if __name__ == "__main__":
    main()
