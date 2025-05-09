#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <yara.h>
#include <limits.h>
#include <unistd.h>
#include <errno.h>
#include <sys/stat.h>

#define PATH_SEPARATOR '/'
#define BUFFER_SIZE 1024

void displayErrorMessage(int errorCode) {
    printf("Error: %s\n", strerror(errorCode));
}

int scanCallback(
    YR_SCAN_CONTEXT* context,
    int message,
    void* message_data,
    void* user_data) {
    switch (message) {
    case CALLBACK_MSG_RULE_MATCHING:
        printf("Matched rule: %s\n", ((YR_RULE*)message_data)->identifier);
        break;
    case CALLBACK_MSG_RULE_NOT_MATCHING:
        printf("Did not match rule: %s\n", ((YR_RULE*)message_data)->identifier);
        break;
    case CALLBACK_MSG_SCAN_FINISHED:
        printf("Scan finished\n");
        break;
    case CALLBACK_MSG_TOO_MANY_MATCHES:
        printf("Too many matches\n");
        break;
    case CALLBACK_MSG_CONSOLE_LOG:
        printf("Console log: %s\n", (char*)message_data);
        break;
    default:
        break;
    }

    return CALLBACK_CONTINUE;
}


void scanFile(const char* filePath, YR_RULES* rules) {
    yr_rules_scan_file(rules, filePath, SCAN_FLAGS_REPORT_RULES_MATCHING, scanCallback, NULL, NULL);
}

void scanDirectory(const char* dirPath, YR_RULES* rules) {
    DIR* dir;
    struct dirent* entry;

    if (!(dir = opendir(dirPath))) {
        printf("Error opening directory\n");
        return;
    }

    while ((entry = readdir(dir)) != NULL) {
        // Note: Some Linux filesystems might not support d_type
        // A more portable approach would use stat()
        char path[BUFFER_SIZE];
        snprintf(path, sizeof(path), "%s%c%s", dirPath, PATH_SEPARATOR, entry->d_name);

        struct stat path_stat;
        stat(path, &path_stat);

        if (S_ISDIR(path_stat.st_mode)) {
            if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
                continue;
            }

            scanDirectory(path, rules);
        }
        else if (S_ISREG(path_stat.st_mode)) {
            scanFile(path, rules);
        }
    }
    closedir(dir);
}

void checkType(const char* path, YR_RULES* rules) {
    struct stat path_stat;
    if (stat(path, &path_stat) == 0) {
        if (S_ISREG(path_stat.st_mode)) {
            // Path is a regular file
            scanFile(path, rules);
        }
        else if (S_ISDIR(path_stat.st_mode)) {
            // Path is a directory
            scanDirectory(path, rules);
        }
        else {
            printf("Unknown file type\n");
        }
    }
    else {
        perror("Error getting file status");
    }
}


int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("[-] Incorrect parameters specified\n");
        return 1;
    }

    const char directory_path[] = "./rules";  // Use relative path or adjust to your Linux directory
    char* file_path = argv[1];

    // Initialize YARA
    int Initresult = yr_initialize();
    if (Initresult != 0) {
        printf("[-] Failed to initialize YARA\n");
        return 1;
    }

    printf("[+] Successfully initialized YARA\n");

    YR_COMPILER* compiler = NULL;
    int Compilerresult = yr_compiler_create(&compiler);
    if (Compilerresult != ERROR_SUCCESS) {
        printf("[-] Failed to initialize YARA compiler\n");
        yr_finalize();
        return 1;
    }

    printf("[+] Successfully created compiler\n");

    // Load YARA rules from each file in the directory
    DIR* directory = opendir(directory_path);
    if (directory == NULL) {
        printf("[-] Failed to open directory: %s\n", directory_path);
        yr_finalize();
        return 1;
    }

    printf("[+] Successfully opened rules directory\n");

    struct dirent* entry;
    while ((entry = readdir(directory)) != NULL) {
        // Check if file ends with .yar or .yara
        char rule_file_path[PATH_MAX];
        snprintf(rule_file_path, sizeof(rule_file_path), "%s/%s", directory_path, entry->d_name);

        struct stat path_stat;
        stat(rule_file_path, &path_stat);

        if (S_ISREG(path_stat.st_mode) && 
           (strstr(entry->d_name, ".yar") != NULL || strstr(entry->d_name, ".yara") != NULL)) {
            
            FILE* rule_file = fopen(rule_file_path, "rb");
            if (rule_file == NULL) {
                printf("[-] Failed to open rule file: %s\n", rule_file_path);
                displayErrorMessage(errno);
                continue;
            }
                
            int Addresult = yr_compiler_add_file(compiler, rule_file, NULL, NULL); 
            if (Addresult > 0) {
                printf("[-] Failed to compile YARA rule %s, number of errors found: %d\n", rule_file_path, Addresult);
                displayErrorMessage(errno);
            }
            else {
                printf("[+] Compiled rules %s\n", rule_file_path);
            }
            fclose(rule_file);
        }         
    }
  
    closedir(directory);

    YR_RULES* rules = NULL;
    int get_rules_result = yr_compiler_get_rules(compiler, &rules);
    if (get_rules_result != ERROR_SUCCESS || rules == NULL) {
        printf("[-] Failed to get compiled rules\n");
        yr_compiler_destroy(compiler);
        yr_finalize();
        return 1;
    }

    // Free the compiler as we don't need it anymore
    yr_compiler_destroy(compiler);

    // Scan the specified file or directory
    checkType(file_path, rules);

    // Clean up
    yr_rules_destroy(rules);
    yr_finalize();

    return 0;
}