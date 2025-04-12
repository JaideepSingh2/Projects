#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/inotify.h>
#include <errno.h>
#include <limits.h>
#include <dirent.h>
#include <sys/stat.h>
#define EVENT_SIZE (sizeof(struct inotify_event))
#define EVENT_BUF_LEN (1024 * (EVENT_SIZE + 16))
#define PATH_SEPARATOR '/'

void displayErrorMessage(int errorCode) {
    printf("Error: %s\n", strerror(errorCode));
    fflush(stdout); // Ensure error messages are flushed
}

void CallDetectionEngine(const char* filePath) {
    printf("[+] Called detection for: %s\n", filePath);
    fflush(stdout);

    // Construct the command to execute, including the file path and the parameter
    char command[1024];
    snprintf(command, sizeof(command), "./engine \"%s\"", filePath);
    
    printf("[+] Executing command: %s\n", command);
    fflush(stdout);

    // Instead of using system(), we'll use popen to capture output
    FILE* fp = popen(command, "r");
    if (fp == NULL) {
        fprintf(stderr, "[-] Failed to execute command: %s\n", command);
        fflush(stderr);
        return;
    }
    
    // Read and forward the output
    char output[1024];
    while (fgets(output, sizeof(output), fp) != NULL) {
        printf("%s", output);
        fflush(stdout);
    }
    
    // Close the pipe and get the return code
    int returnCode = pclose(fp);
    if (returnCode != 0) {
        fprintf(stderr, "[-] Command exited with code: %d\n", returnCode);
        fflush(stderr);
    } else {
        printf("[+] Command executed successfully\n");
        fflush(stdout);
    }
}

// Function to perform initial scan of a directory
void scanDirectoryRecursively(const char* dirPath) {
    DIR* dir;
    struct dirent* entry;
    struct stat path_stat;
    char fullPath[PATH_MAX];

    printf("[+] Performing initial scan of directory: %s\n", dirPath);
    fflush(stdout);

    if (!(dir = opendir(dirPath))) {
        printf("[-] Error opening directory for initial scan: %s\n", dirPath);
        displayErrorMessage(errno);
        return;
    }

    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        snprintf(fullPath, PATH_MAX, "%s%c%s", dirPath, PATH_SEPARATOR, entry->d_name);
        
        if (stat(fullPath, &path_stat) == 0) {
            if (S_ISDIR(path_stat.st_mode)) {
                // Recursively scan subdirectories
                scanDirectoryRecursively(fullPath);
            } 
            else if (S_ISREG(path_stat.st_mode) && entry->d_name[0] != '.') {
                // Scan regular files (not hidden)
                printf("[+] Initial scan of file: %s\n", fullPath);
                fflush(stdout);
                
                // Call detection engine with the file path
                CallDetectionEngine(fullPath);
            }
        }
    }
    
    closedir(dir);
    printf("[+] Initial scan of directory completed: %s\n", dirPath);
    fflush(stdout);
}

void* MonitorDirectoryThread(void* arg) {
    char* directoryPath = (char*)arg;
    int fd, wd;
    char buffer[EVENT_BUF_LEN];

    // First, perform an initial scan of the directory
    printf("[+] STARTING INITIAL SCAN: %s\n", directoryPath);  
    fflush(stdout);
    scanDirectoryRecursively(directoryPath);
    printf("[+] COMPLETED INITIAL SCAN: %s\n", directoryPath);  
    fflush(stdout);

    // Then set up the monitoring
    fd = inotify_init();
    if (fd < 0) {
        printf("[-] Failed to initialize inotify for path: %s\n", directoryPath);
        displayErrorMessage(errno);
        free(directoryPath);
        return NULL;
    }

    // Add watch for the directory - add IN_DELETE event
    wd = inotify_add_watch(fd, directoryPath, IN_CREATE | IN_MODIFY | IN_CLOSE_WRITE | IN_DELETE);
    if (wd < 0) {
        printf("[-] Failed to add watch for directory: %s\n", directoryPath);
        displayErrorMessage(errno);
        close(fd);
        free(directoryPath);
        return NULL;
    }

    printf("[+] Now actively monitoring directory: %s\n", directoryPath);
    fflush(stdout);

    while (1) {
        int length = read(fd, buffer, EVENT_BUF_LEN);
        if (length < 0) {
            printf("[-] Error reading inotify events for: %s\n", directoryPath);
            displayErrorMessage(errno);
            break;
        }

        int i = 0;
        while (i < length) {
            struct inotify_event* event = (struct inotify_event*)&buffer[i];
            
            if (event->len) {
                // Handle file creation, modification, and deletion
                if (event->mask & (IN_CREATE | IN_MODIFY | IN_CLOSE_WRITE)) {
                    // Skip directories and hidden files
                    if (!(event->mask & IN_ISDIR) && event->name[0] != '.') {
                        // Construct full path
                        char fullPath[PATH_MAX];
                        snprintf(fullPath, PATH_MAX, "%s%c%s", directoryPath, PATH_SEPARATOR, event->name);

                        // Print full path
                        printf("[+] Change detected in file: %s\n", fullPath);
                        fflush(stdout);
                        
                        // Call detection engine with the file path
                        CallDetectionEngine(fullPath);
                    }
                } 
                // Handle file deletion separately
                else if (event->mask & IN_DELETE) {
                    if (!(event->mask & IN_ISDIR) && event->name[0] != '.') {
                        char fullPath[PATH_MAX];
                        snprintf(fullPath, PATH_MAX, "%s%c%s", directoryPath, PATH_SEPARATOR, event->name);
                        
                        printf("[+] File deleted: %s\n", fullPath);
                        fflush(stdout);
                    }
                }
            }
            
            i += EVENT_SIZE + event->len;
        }
    }

    // Clean up
    inotify_rm_watch(fd, wd);
    close(fd);
    free(directoryPath);
    return NULL;
}

int main(int argc, char* argv[]) {
    // Use command line arguments when provided
    char pathList[PATH_MAX];
    
    if (argc > 1) {
        strncpy(pathList, argv[1], PATH_MAX - 1);
        pathList[PATH_MAX - 1] = '\0';
    } else {
        // Default path for testing
        printf("[!] No path specified, using default path\n");
        strcpy(pathList, "/tmp");
    }
    
    printf("[+] Starting real-time monitoring with paths: %s\n", pathList);
    fflush(stdout);

    char* token;
    token = strtok(pathList, ";");
    pthread_t threads[100]; // Maximum 100 directories to monitor
    int threadCount = 0;

    while (token != NULL && threadCount < 100) {
        printf("[+] Processing directory: %s\n", token);
        fflush(stdout);
        
        // Create a copy of the token because strtok modifies the string
        char* dirPath = strdup(token);
        if (dirPath == NULL) {
            printf("[-] Failed to allocate memory for directory path\n");
            fflush(stdout);
            return 1;
        }

        // Create a thread for monitoring this directory
        if (pthread_create(&threads[threadCount], NULL, MonitorDirectoryThread, dirPath) != 0) {
            printf("[-] Failed to create thread for directory monitoring: %s\n", dirPath);
            displayErrorMessage(errno);
            free(dirPath);
            return 1;
        }
        threadCount++;
        
        token = strtok(NULL, ";");
    }
    
    if (threadCount == 0) {
        printf("[-] No valid directories to monitor\n");
        fflush(stdout);
        return 1;
    }
    
    printf("[+] Successfully started monitoring %d directories\n", threadCount);
    printf("[+] Initial scans in progress. Monitoring for file creation, modification, and deletion\n");
    printf("Press 'q' followed by Enter to exit...\n");
    fflush(stdout);

    // Wait for user input to exit
    char userInput;
    do {
        userInput = getchar();
    } while (userInput != 'q');

    printf("Exiting...\n");
    fflush(stdout);
    
    return 0;
}