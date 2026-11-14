#define _GNU_SOURCE
#include <dirent.h>
#include <drm/drm.h>
#include <drm/drm_mode.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/system_properties.h>
#include <unistd.h>

static int property_id(int fd, uint32_t object, uint32_t type,
                       const char *wanted, uint64_t *value) {
    struct drm_mode_obj_get_properties obj = {.obj_id = object, .obj_type = type};
    if (ioctl(fd, DRM_IOCTL_MODE_OBJ_GETPROPERTIES, &obj) < 0 || obj.count_props == 0 ||
        obj.count_props > 128) return -1;
    uint32_t *ids = calloc(obj.count_props, sizeof(*ids));
    uint64_t *values = calloc(obj.count_props, sizeof(*values));
    if (!ids || !values) { free(ids); free(values); return -1; }
    obj.props_ptr = (uintptr_t)ids;
    obj.prop_values_ptr = (uintptr_t)values;
    int found = -1;
    if (ioctl(fd, DRM_IOCTL_MODE_OBJ_GETPROPERTIES, &obj) == 0) {
        for (uint32_t i = 0; i < obj.count_props; ++i) {
            struct drm_mode_get_property prop = {.prop_id = ids[i]};
            if (ioctl(fd, DRM_IOCTL_MODE_GETPROPERTY, &prop) == 0 &&
                strcmp(prop.name, wanted) == 0) {
                found = (int)ids[i];
                if (value) *value = values[i];
                break;
            }
        }
    }
    free(ids);
    free(values);
    return found;
}

static int dsi_crtc(int fd, uint32_t *connector_out, uint32_t *crtc_out) {
    struct drm_mode_card_res res = {0};
    if (ioctl(fd, DRM_IOCTL_MODE_GETRESOURCES, &res) < 0) {
        perror("GETRESOURCES"); return -1;
    }
    fprintf(stderr, "connectors=%u crtcs=%u\n", res.count_connectors, res.count_crtcs);
    if (res.count_connectors == 0 || res.count_connectors > 64) return -1;
    uint32_t *ids = calloc(res.count_connectors, sizeof(*ids));
    if (!ids) return -1;
    res.connector_id_ptr = (uintptr_t)ids;
    res.count_fbs = 0;
    res.count_crtcs = 0;
    res.count_encoders = 0;
    int found = -1;
    if (ioctl(fd, DRM_IOCTL_MODE_GETRESOURCES, &res) == 0) {
        for (uint32_t i = 0; i < res.count_connectors; ++i) {
            struct drm_mode_get_connector conn = {.connector_id = ids[i]};
            if (ioctl(fd, DRM_IOCTL_MODE_GETCONNECTOR, &conn) < 0) {
                perror("GETCONNECTOR"); continue;
            }
            fprintf(stderr, "connector=%u type=%u connection=%u encoder=%u\n",
                    ids[i], conn.connector_type, conn.connection, conn.encoder_id);
            if (conn.connector_type != DRM_MODE_CONNECTOR_DSI || conn.connection != 1) continue;
            uint32_t crtc = 0;
            if (conn.encoder_id) {
                struct drm_mode_get_encoder enc = {.encoder_id = conn.encoder_id};
                if (ioctl(fd, DRM_IOCTL_MODE_GETENCODER, &enc) == 0) crtc = enc.crtc_id;
            }
            if (!crtc) {
                uint64_t value = 0;
                if (property_id(fd, ids[i], DRM_MODE_OBJECT_CONNECTOR,
                                "CRTC_ID", &value) >= 0) crtc = (uint32_t)value;
            }
            if (crtc) {
                *connector_out = ids[i];
                *crtc_out = crtc;
                found = 0;
                break;
            }
        }
    } else {
        perror("GETRESOURCES ids");
    }
    free(ids);
    return found;
}

static int atomic_active(int fd, uint32_t crtc, uint32_t active_prop,
                         uint64_t active, int test_only) {
    uint32_t objs[] = {crtc};
    uint32_t counts[] = {1};
    uint32_t props[] = {active_prop};
    uint64_t values[] = {active};
    struct drm_mode_atomic req = {
        .flags = DRM_MODE_ATOMIC_ALLOW_MODESET |
                 (test_only ? DRM_MODE_ATOMIC_TEST_ONLY : 0),
        .count_objs = 1,
        .objs_ptr = (uintptr_t)objs,
        .count_props_ptr = (uintptr_t)counts,
        .props_ptr = (uintptr_t)props,
        .prop_values_ptr = (uintptr_t)values,
    };
    return ioctl(fd, DRM_IOCTL_MODE_ATOMIC, &req);
}

static int panel_off(void) {
    char buf[32] = {0};
    int fd = open("/sys/class/drm/card0-DSI-1/dpms", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    return n > 0 ? strncmp(buf, "Off", 3) == 0 : -1;
}

int main(int argc, char **argv) {
    if (argc != 3 || (strcmp(argv[1], "inspect") && strcmp(argv[1], "blank") &&
                      strcmp(argv[1], "wake"))) {
        fprintf(stderr, "usage: charger_drm_blank inspect|blank|wake PID\n");
        return 2;
    }
    const int blank = strcmp(argv[1], "blank") == 0;
    const int wake = strcmp(argv[1], "wake") == 0;
    if (blank || wake) {
        char mode[PROP_VALUE_MAX] = {0};
        __system_property_get("ro.bootmode", mode);
        if (strcmp(mode, "charger") != 0) {
            fprintf(stderr, "refusing blank outside charger mode: %s\n", mode);
            return 2;
        }
    }
    int pid = atoi(argv[2]);
    if (pid <= 1) return 2;
    int pidfd = (int)syscall(__NR_pidfd_open, pid, 0);
    if (pidfd < 0) { perror("pidfd_open"); return 1; }
    char dirpath[64];
    snprintf(dirpath, sizeof(dirpath), "/proc/%d/fd", pid);
    DIR *dir = opendir(dirpath);
    if (!dir) { perror("opendir"); close(pidfd); return 1; }
    int result = 1;
    struct dirent *ent;
    while ((ent = readdir(dir)) != NULL) {
        char *end;
        long target = strtol(ent->d_name, &end, 10);
        if (*end || target < 0) continue;
        char linkpath[96], targetpath[256];
        snprintf(linkpath, sizeof(linkpath), "%s/%s", dirpath, ent->d_name);
        ssize_t n = readlink(linkpath, targetpath, sizeof(targetpath) - 1);
        if (n < 0) continue;
        targetpath[n] = 0;
        if (strcmp(targetpath, "/dev/dri/card0") != 0) continue;
        int fd = (int)syscall(__NR_pidfd_getfd, pidfd, target, 0);
        if (fd < 0) { perror("pidfd_getfd"); continue; }
        uint32_t conn = 0, crtc = 0;
        fprintf(stderr, "dup fd=%ld\n", target);
        if (dsi_crtc(fd, &conn, &crtc) < 0) { close(fd); continue; }
        uint64_t active = UINT64_MAX, mode = UINT64_MAX;
        int active_id = property_id(fd, crtc, DRM_MODE_OBJECT_CRTC, "ACTIVE", &active);
        int mode_id = property_id(fd, crtc, DRM_MODE_OBJECT_CRTC, "MODE_ID", &mode);
        printf("fd=%ld dsi=%u crtc=%u active_prop=%d active=%llu mode_prop=%d mode=%llu\n",
               target, conn, crtc, active_id, (unsigned long long)active,
               mode_id, (unsigned long long)mode);
        if (active_id < 0 || mode_id < 0) { close(fd); continue; }
        if (!blank && !wake) { result = 0; close(fd); break; }
        if (wake) {
            if (mode == 0) {
                fputs("cannot wake: missing CRTC mode\n", stderr);
            } else if (atomic_active(fd, crtc, (uint32_t)active_id, 1, 1) < 0) {
                perror("wake TEST_ONLY");
            } else if (atomic_active(fd, crtc, (uint32_t)active_id, 1, 0) < 0) {
                perror("wake commit");
            } else {
                usleep(300000);
                result = panel_off() == 0 ? 0 : 1;
                printf("panel after ACTIVE=1: %s\n", result ? "still Off" : "On");
            }
            close(fd);
            break;
        }
        if (atomic_active(fd, crtc, (uint32_t)active_id, 0, 1) < 0) {
            perror("atomic TEST_ONLY"); close(fd); continue;
        }
        if (atomic_active(fd, crtc, (uint32_t)active_id, 0, 0) < 0) {
            perror("atomic blank"); close(fd); continue;
        }
        usleep(300000);
        if (panel_off() == 1) {
            puts("panel Off after ACTIVE=0");
            result = 0;
        } else if (mode != 0 &&
                   atomic_active(fd, crtc, (uint32_t)active_id, 1, 1) == 0 &&
                   atomic_active(fd, crtc, (uint32_t)active_id, 1, 0) == 0) {
            usleep(150000);
            if (atomic_active(fd, crtc, (uint32_t)active_id, 0, 0) < 0) {
                perror("second atomic blank");
            } else {
                usleep(300000);
                result = panel_off() == 1 ? 0 : 1;
                printf("panel after ACTIVE=1->0: %s\n", result ? "still On" : "Off");
            }
        } else {
            fputs("panel still On; ACTIVE=1 resync unavailable\n", stderr);
        }
        close(fd);
        break;
    }
    closedir(dir);
    close(pidfd);
    if (result) fputs("no usable DSI DRM fd\n", stderr);
    return result;
}
