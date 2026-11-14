#define _GNU_SOURCE
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: fd_probe PID FD\n");
        return 2;
    }
    long pid = strtol(argv[1], NULL, 10);
    long target_fd = strtol(argv[2], NULL, 10);
    int pidfd = (int)syscall(__NR_pidfd_open, pid, 0);
    if (pidfd < 0) {
        fprintf(stderr, "pidfd_open: errno=%d\n", errno);
        return 1;
    }
    int fd = (int)syscall(__NR_pidfd_getfd, pidfd, target_fd, 0);
    if (fd < 0) {
        fprintf(stderr, "pidfd_getfd: errno=%d\n", errno);
        return 1;
    }
    struct stat st;
    if (fstat(fd, &st) < 0) {
        fprintf(stderr, "fstat: errno=%d\n", errno);
        return 1;
    }
    printf("duplicated pid=%ld fd=%ld mode=%o rdev=%llu\n", pid, target_fd,
           st.st_mode, (unsigned long long)st.st_rdev);
    close(fd);
    close(pidfd);
    return 0;
}
