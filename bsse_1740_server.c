/*
Name        : Md.Tofazzol Alam Rahat
Roll        : BSSE-1740
Section     : B
E-mail      :bsse1740@iit.du.ac.bd
Course      : Structured Programming Lab
*/
/*
 * server.c
 * ---------------------------------------
 * Terminal-based group & private chat server.
 * 
 * Build: gcc bsse_1740_server.c -o bsse_1740_server -lpthread
            ./bsse_1740_server
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <netinet/in.h>
#include <ctype.h>
#include <time.h>
#include <arpa/inet.h>
#include <signal.h>
#include <stdint.h>
#include <errno.h>
#define MAX_CLIENTS 100
#define MAX_MSG_LEN 4096
#define MAX_NAME_LEN 50
#define PORT 9000

/*------------------------------------------------------------
 * Global Server State
 *-----------------------------------------------------------*/
static int server_sock = -1;
static int client_socks[MAX_CLIENTS];
static char *usernames[MAX_CLIENTS];
static int client_count = 0;
static pthread_mutex_t clients_lock = PTHREAD_MUTEX_INITIALIZER;
static volatile sig_atomic_t shutting_down = 0;

/*------------------------------------------------------------
 * Utility: Reliable Send and Receive
 *-----------------------------------------------------------*/

/* Send all bytes of a message */
ssize_t send_all(int sock, const void *buf, size_t len)
 {
    size_t sent = 0;
    const char *p = (const char *)buf;
    while (sent < len) {
        ssize_t n = send(sock, p + sent, len - sent, 0);
        if (n <= 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        sent += (size_t)n;
    }
    return (ssize_t)sent;
}

/* Receive all bytes of a message */
ssize_t recv_all(int sock, void *buf, size_t len) {
    size_t recvd = 0;
    char *p = (char *)buf;
    while (recvd < len) {
        ssize_t n = recv(sock, p + recvd, len - recvd, 0);
        if (n <= 0) {
            if (n == 0) return 0;
            if (errno == EINTR) continue;
            return -1;
        }
        recvd += (size_t)n;
    }
    return (ssize_t)recvd;
}

/*------------------------------------------------------------
 * Framed Message Protocol
 *-----------------------------------------------------------*/

/* Send a message with 4-byte length prefix */
int send_message_framed(int sock, const char *data, uint32_t len) {
    uint32_t nl = htonl(len);
    if (send_all(sock, &nl, sizeof(nl)) != sizeof(nl)) return -1;
    if (len > 0 && send_all(sock, data, len) != (ssize_t)len) return -1;
    return 0;
}

/* Receive a framed message safely */
ssize_t recv_message_framed(int sock, char *buf, size_t bufcap) {
    uint32_t nl;
    ssize_t r = recv_all(sock, &nl, sizeof(nl));
    if (r == 0) return 0;
    if (r < 0) return -1;

    uint32_t len = ntohl(nl);
    if (len >= bufcap) {
        /* Drop oversized message */
        char *tmp = malloc(len + 1);
        if (!tmp) return -1;
        recv_all(sock, tmp, len);
        free(tmp);
        return -2;
    }

    r = recv_all(sock, buf, len);
    if (r <= 0) return r;
    buf[len] = '\0';
    return (ssize_t)len;
}

/*------------------------------------------------------------
 * Helper Functions
 *-----------------------------------------------------------*/

/* Format current time as [HH:MM] */
void format_time(char *out, size_t outlen) {
    time_t now = time(NULL);
    struct tm tm_info;
    localtime_r(&now, &tm_info);
    strftime(out, outlen, "[%H:%M]", &tm_info);
}

/* Check if a username is valid */
int is_valid_username(const char *name) {
    if (!name) return 0;
    size_t len = strlen(name);
    if (len < 3 || len > 20) return 0;
    for (size_t i = 0; i < len; ++i) {
        if (!isalnum((unsigned char)name[i])) return 0;
    }
    return 1;
}

/*------------------------------------------------------------
 * Core Server Features
 *-----------------------------------------------------------*/

/* Broadcast a message to all clients (optionally excluding one) */
void broadcast_all(const char *msg, int exclude_sock) {
    pthread_mutex_lock(&clients_lock);
    for (int i = 0; i < client_count; ++i) {
        int s = client_socks[i];
        if (s == exclude_sock) continue;
        send_message_framed(s, msg, (uint32_t)strlen(msg));
    }
    pthread_mutex_unlock(&clients_lock);
}

/* Send a private message to a specific recipient */
void send_private(const char *recipient, const char *msg) {
    pthread_mutex_lock(&clients_lock);
    for (int i = 0; i < client_count; ++i) {
        if (usernames[i] && strcmp(usernames[i], recipient) == 0) {
            send_message_framed(client_socks[i], msg, (uint32_t)strlen(msg));
            break;
        }
    }
    pthread_mutex_unlock(&clients_lock);
}

/* Broadcast the active user list to all clients */
void broadcast_userlist(void) {
    char list[MAX_MSG_LEN];
    size_t off = 0;
    off += snprintf(list + off, sizeof(list) - off, "[userlist]");

    pthread_mutex_lock(&clients_lock);
    for (int i = 0; i < client_count; ++i) {
        if (usernames[i]) {
            off += snprintf(list + off, sizeof(list) - off, "%s,", usernames[i]);
            if (off >= sizeof(list)) break;
        }
    }
    pthread_mutex_unlock(&clients_lock);

    strncat(list, "\n", sizeof(list) - strlen(list) - 1);
    broadcast_all(list, -1);
}

/* Save a message to chat history file */
void save_history(const char *msg) {
    FILE *fp = fopen("chat_history.txt", "a");
    if (!fp) return;
    fputs(msg, fp);
    fclose(fp);
}

/* Remove client data by socket */
void remove_client_by_socket(int sock) {
    pthread_mutex_lock(&clients_lock);
    for (int i = 0; i < client_count; ++i) {
        if (client_socks[i] == sock) {
            free(usernames[i]);
            for (int j = i; j < client_count - 1; ++j) {
                client_socks[j] = client_socks[j + 1];
                usernames[j] = usernames[j + 1];
            }
            client_count--;
            break;
        }
    }
    pthread_mutex_unlock(&clients_lock);
}

/*------------------------------------------------------------
 * Client Handler Thread
 *-----------------------------------------------------------*/

void *handle_client(void *arg) {
    int sock = *(int *)arg;
    free(arg);

    char buf[MAX_MSG_LEN + 1];
    char username[MAX_NAME_LEN];

    /* Receive username */
    ssize_t r = recv_message_framed(sock, buf, sizeof(buf));
    if (r <= 0) {
        close(sock);
        return NULL;
    }
    strncpy(username, buf, sizeof(username) - 1);
    username[sizeof(username) - 1] = '\0';
    username[strcspn(username, "\n")] = '\0';

    /* Validate username */
    if (!is_valid_username(username)) {
        send_message_framed(sock, "[server] Invalid username\n", 27);
        close(sock);
        return NULL;
    }

    /* Ensure unique username */
    pthread_mutex_lock(&clients_lock);
    for (int i = 0; i < client_count; ++i) {
        if (strcmp(usernames[i], username) == 0) {
            pthread_mutex_unlock(&clients_lock);
            send_message_framed(sock, "[server] Username already taken\n", 33);
            close(sock);
            return NULL;
        }
    }

    /* Reject if server full */
    if (client_count >= MAX_CLIENTS) {
        pthread_mutex_unlock(&clients_lock);
        send_message_framed(sock, "[server] Server full\n", 22);
        close(sock);
        return NULL;
    }

    /* Register client */
    usernames[client_count] = strdup(username);
    client_socks[client_count] = sock;
    client_count++;
    pthread_mutex_unlock(&clients_lock);

    /* Confirm registration */
    send_message_framed(sock, "[server] OK\n", 13);

    /* Broadcast userlist and join message */
    broadcast_userlist();

    char ts[32];
    format_time(ts, sizeof(ts));
    char join_msg[MAX_MSG_LEN];
    snprintf(join_msg, sizeof(join_msg), "%s [server] %s has joined the chat.\n", ts, username);
    broadcast_all(join_msg, -1);
    save_history(join_msg);

    /* Main message loop */
    while (!shutting_down) {
        ssize_t len = recv_message_framed(sock, buf, sizeof(buf));
        if (len == 0) break;
        if (len < 0) {
            if (len == -2) continue;
            break;
        }

        /* Expected format: type|sender|target|content */
        char *saveptr = NULL;
        char *type = strtok_r(buf, "|", &saveptr);
        char *sender = strtok_r(NULL, "|", &saveptr);
        char *target = strtok_r(NULL, "|", &saveptr);
        char *content = strtok_r(NULL, "\n", &saveptr);

        if (type && sender && target && content) {
            char formatted[MAX_MSG_LEN];
            format_time(ts, sizeof(ts));
            snprintf(formatted, sizeof(formatted), "%s [%s] %s -> %s: %s\n",
                     ts, type, sender, target, content);
            save_history(formatted);

            if (strcmp(type, "group") == 0)
                broadcast_all(formatted, sock);
            else if (strcmp(type, "private") == 0)
                send_private(target, formatted);
            else
                send_message_framed(sock, "[server] Invalid message type\n", 31);
        } else {
            send_message_framed(sock, "[server] Invalid message format\n", 33);
        }
    }

    /* Cleanup client */
    close(sock);
    remove_client_by_socket(sock);
    broadcast_userlist();

    format_time(ts, sizeof(ts));
    char leave_msg[MAX_MSG_LEN];
    snprintf(leave_msg, sizeof(leave_msg), "%s [server] %s has left the chat.\n", ts, username);
    broadcast_all(leave_msg, -1);
    save_history(leave_msg);

    return NULL;
}

/*------------------------------------------------------------
 * Graceful Shutdown
 *-----------------------------------------------------------*/

void sigint_handler(int sig) {
    (void)sig;
    shutting_down = 1;

    if (server_sock >= 0) {
        shutdown(server_sock, SHUT_RDWR);
        close(server_sock);
        server_sock = -1;
    }

    pthread_mutex_lock(&clients_lock);
    for (int i = 0; i < client_count; ++i) {
        shutdown(client_socks[i], SHUT_RDWR);
        close(client_socks[i]);
    }
    pthread_mutex_unlock(&clients_lock);
}

/*------------------------------------------------------------
 * Main Server Entry Point
 *-----------------------------------------------------------*/

int main(void) {
    struct sigaction sa;
    sa.sa_handler = sigint_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGINT, &sa, NULL);

    server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock < 0) {
        perror("socket");
        return 1;
    }

    int opt = 1;
    setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in srv;
    memset(&srv, 0, sizeof(srv));
    srv.sin_family = AF_INET;
    srv.sin_addr.s_addr = INADDR_ANY;
    srv.sin_port = htons(PORT);

    if (bind(server_sock, (struct sockaddr *)&srv, sizeof(srv)) < 0) {
        perror("bind");
        close(server_sock);
        return 1;
    }

    if (listen(server_sock, 16) < 0) {
        perror("listen");
        close(server_sock);
        return 1;
    }

    printf("Server started on port %d\n", PORT);

    while (!shutting_down) {
        struct sockaddr_in cli;
        socklen_t cli_len = sizeof(cli);
        int client_sock = accept(server_sock, (struct sockaddr *)&cli, &cli_len);
        if (client_sock < 0) {
            if (errno == EINTR && shutting_down) break;
            perror("accept");
            continue;
        }

        int *pclient = malloc(sizeof(int));
        if (!pclient) {
            close(client_sock);
            continue;
        }

        *pclient = client_sock;
        pthread_t tid;
        if (pthread_create(&tid, NULL, handle_client, pclient) != 0) {
            perror("pthread_create");
            close(client_sock);
            free(pclient);
            continue;
        }
        pthread_detach(tid);
    }

    /* Final cleanup */
    if (server_sock >= 0) {
        close(server_sock);
        server_sock = -1;
    }

    pthread_mutex_lock(&clients_lock);
    for (int i = 0; i < client_count; ++i) {
        free(usernames[i]);
        usernames[i] = NULL;
    }
    client_count = 0;
    pthread_mutex_unlock(&clients_lock);

    printf("Server shutting down.\n");
    return 0;
}
