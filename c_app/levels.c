/* levels.c — 用 cJSON 解析 levels.json */
#include "levels.h"
#include "cJSON.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* 读整个文件到堆缓冲，调用者负责 free */
static char *read_file(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (sz < 0) { fclose(f); return NULL; }
    char *buf = (char *)malloc((size_t)sz + 1);
    if (!buf) { fclose(f); return NULL; }
    size_t rd = fread(buf, 1, (size_t)sz, f);
    fclose(f);
    buf[rd] = '\0';
    return buf;
}

int levels_load(const char *path, LevelSet *out) {
    out->items = NULL;
    out->count = 0;

    char *buf = read_file(path);
    if (!buf) {
        fprintf(stderr, "[levels] cannot open %s\n", path);
        return -1;
    }

    cJSON *root = cJSON_Parse(buf);
    free(buf);
    if (!root || !cJSON_IsArray(root)) {
        fprintf(stderr, "[levels] JSON parse failed or not array\n");
        if (root) cJSON_Delete(root);
        return -2;
    }

    int n = cJSON_GetArraySize(root);
    out->items = (Level *)calloc((size_t)n, sizeof(Level));
    if (!out->items) {
        cJSON_Delete(root);
        return -3;
    }
    out->count = n;

    int i = 0;
    cJSON *item;
    cJSON_ArrayForEach(item, root) {
        Level *lv = &out->items[i++];

        cJSON *jname = cJSON_GetObjectItem(item, "name");
        const char *sname = (jname && jname->valuestring) ? jname->valuestring : "";
        strncpy(lv->name, sname, sizeof(lv->name) - 1);
        lv->name[sizeof(lv->name) - 1] = '\0';

        cJSON *jpuz = cJSON_GetObjectItem(item, "puzzle");
        if (jpuz && cJSON_IsArray(jpuz)) {
            int rows = cJSON_GetArraySize(jpuz);
            lv->rowCount = rows;
            lv->puzzle = (char **)calloc((size_t)rows, sizeof(char *));
            for (int r = 0; r < rows; r++) {
                cJSON *jrow = cJSON_GetArrayItem(jpuz, r);
                const char *srow = (jrow && jrow->valuestring) ? jrow->valuestring : "";
                lv->puzzle[r] = strdup(srow);
            }
        } else {
            lv->rowCount = 0;
            lv->puzzle = NULL;
        }

        cJSON *jsol = cJSON_GetObjectItem(item, "solution");
        const char *ssol = (jsol && jsol->valuestring) ? jsol->valuestring : "";
        lv->solution = strdup(ssol);
    }

    cJSON_Delete(root);
    return 0;
}

void levels_free(LevelSet *set) {
    if (!set->items) return;
    for (int i = 0; i < set->count; i++) {
        Level *lv = &set->items[i];
        if (lv->puzzle) {
            for (int r = 0; r < lv->rowCount; r++) {
                if (lv->puzzle[r]) free(lv->puzzle[r]);
            }
            free(lv->puzzle);
        }
        if (lv->solution) free(lv->solution);
    }
    free(set->items);
    set->items = NULL;
    set->count = 0;
}
