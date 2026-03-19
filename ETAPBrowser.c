#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <libgen.h>

int main(int argc, char *argv[]) {
    char path[1024];
    ssize_t len = readlink("/proc/self/exe", path, sizeof(path) - 1); //tam yol
    
    if (len != -1) {
        path[len] = '\0';
        char *dir = dirname(path); //mutlak yol
        
        char script_path[1024];
        snprintf(script_path, sizeof(script_path), "%s/main.py", dir); //main.py'ın mutlak yolu

        char **new_argv = malloc((argc + 2) * sizeof(char *)); //args
        new_argv[0] = "python3";
        new_argv[1] = script_path;
        
        for (int i = 1; i < argc; i++) {
            new_argv[i + 1] = argv[i];
        }
        new_argv[argc + 1] = NULL;

        execvp("python3", new_argv); //main.py
    }

    perror("Hata: main.py bulunamadı veya başlatılamadı");
    return 1;
}