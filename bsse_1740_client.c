/*
Name        : Md.Tofazzol Alam Rahat
Roll        : BSSE-1740
Section     : B
E-mail      :bsse1740@iit.du.ac.bd
Course      : Structured Programming Lab
*/
/*
 client.c
 Build: gcc bsse_1740_client.c -o bsse_1740_client -lncurses -lpthread
            ./bsse_1740_client <server_ip> <port>
 Clean, organized, English-only comments. All existing features preserved:
 - ncurses UI: users, chat, input windows
 - message framing over TCP
 - chat history buffer with manual scroll
 - filter chat by selecting user from user list (arrow keys)
 - one-time private messages with @username prefix
 - /to command, /quit, page up/down scrolling
 - proper cleanup (free history, close socket, endwin)
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ncurses.h>
#include <pthread.h>
#include <netinet/in.h>
#include <ctype.h>
#include <arpa/inet.h>
#include <signal.h>
#include <stdint.h>
#include <errno.h>
#include <stdarg.h>

#define MAX_MSG_LEN     4096
#define MAX_NAME_LEN     50
#define MAX_TARGET_LEN   50
#define MAX_INPUT_LEN   800
#define PORT           8080
#define MAX_HISTORY    500
#define MAX_USERS      100

/* UI windows */
static WINDOW *win_users = NULL;
static WINDOW *win_chat  = NULL;
static WINDOW *win_input = NULL;

/* client state */
static char username[MAX_NAME_LEN] = {0};
static char target[MAX_TARGET_LEN] = "all";
static int sockfd = -1;
static volatile sig_atomic_t exiting = 0;

/* UI synchronization */
static pthread_mutex_t ui_lock = PTHREAD_MUTEX_INITIALIZER;

/* chat history buffer and scrolling */
static char *chat_history[MAX_HISTORY];
static int chat_count = 0;
static int scroll_offset = 0;      /* manual scroll offset (0 = newest) */

/* users list */
static char user_list[MAX_USERS][MAX_NAME_LEN];
static int user_count = 0;

/* selected user (for filtering) */
static int selected_user_index = -1;   /* -1 = none selected */
static char selected_user[MAX_NAME_LEN] = "all";
static int user_scroll_offset = 0;

/* Utility: reliable send/recv helpers (handle EINTR) */
ssize_t send_all(int sock, const void *buf, size_t len) {
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

/* Framed message send: 4-byte length prefix (network order) then payload */
int send_message_framed(int sock, const char *data, uint32_t len) {
    uint32_t nl = htonl(len);
    if (send_all(sock, &nl, sizeof(nl)) != sizeof(nl)) return -1;
    if (len > 0 && send_all(sock, data, len) != (ssize_t)len) return -1;
    return 0;
}

/* Framed message receive. Returns:
   >0 number of bytes read into buf
    0 connection closed
   -1 error
   -2 message too large for buffer (data discarded)
*/
ssize_t recv_message_framed(int sock, char *buf, size_t bufcap) {
    uint32_t nl;
    ssize_t r = recv_all(sock, &nl, sizeof(nl));
    if (r == 0) return 0;
    if (r < 0) return -1;
    uint32_t len = ntohl(nl);
    if (len >= bufcap) {
        char *tmp = malloc(len + 1);
        if (!tmp) return -1;
        (void)recv_all(sock, tmp, len); /* discard */
        free(tmp);
        return -2;
    }
    r = recv_all(sock, buf, len);
    if (r <= 0) return r;
    buf[len] = '\0';
    return (ssize_t)len;
}

/* Initialize ncurses UI and windows */
void init_ui(void) {
    initscr();
    cbreak();
    noecho();
    start_color();
    init_pair(1, COLOR_CYAN,    COLOR_BLACK);  /* generic */
    init_pair(2, COLOR_GREEN,   COLOR_BLACK);  /* group messages */
    init_pair(3, COLOR_YELLOW,  COLOR_BLACK);  /* private messages */
    init_pair(4, COLOR_MAGENTA, COLOR_BLACK);  /* system / symbolic */
    init_pair(5, COLOR_BLUE,    COLOR_BLACK);  /* highlight current user */

    int height = LINES / 3;
    win_users = newwin(height, COLS / 4, 0, 0);
    win_chat  = newwin(height * 2, COLS - COLS / 4, 0, COLS / 4);
    win_input = newwin(height, COLS, height * 2, 0);

    scrollok(win_chat, TRUE);
    keypad(win_input, TRUE);
    keypad(win_chat, TRUE);

    box(win_users, 0, 0);
    box(win_chat, 0, 0);
    box(win_input, 0, 0);
    mvwprintw(win_users, 0, 2, " Users ");
    mvwprintw(win_chat, 0, 2, " Chat ");
    mvwprintw(win_input, 0, 2, " Input ");

    pthread_mutex_lock(&ui_lock);
    wrefresh(win_users);
    wrefresh(win_chat);
    wrefresh(win_input);
    pthread_mutex_unlock(&ui_lock);
}

/* Shutdown and cleanup ncurses windows */
void shutdown_ui(void) {
    pthread_mutex_lock(&ui_lock);
    if (win_users) { delwin(win_users); win_users = NULL; }
    if (win_chat)  { delwin(win_chat);  win_chat  = NULL; }
    if (win_input) { delwin(win_input); win_input = NULL; }
    pthread_mutex_unlock(&ui_lock);
    endwin();
}

/* Repaint chat window using chat_history and scroll_offset */
void scroll_chat(int direction) {
    scroll_offset += direction;
    if (scroll_offset < 0) scroll_offset = 0;
    if (chat_count == 0) scroll_offset = 0;
    if (scroll_offset > chat_count - 1) scroll_offset = chat_count - 1;

    pthread_mutex_lock(&ui_lock);
    werase(win_chat);
    box(win_chat, 0, 0);
    mvwprintw(win_chat, 0, 2, " Chat ");

    int lines = getmaxy(win_chat) - 2;
    int start = (chat_count > lines) ? chat_count - lines - scroll_offset : 0;
    if (start < 0) start = 0;
    int end = start + lines;
    if (end > chat_count) end = chat_count;

    for (int i = start, row = 1; i < end; ++i, ++row) {
        mvwprintw(win_chat, row, 1, "%s", chat_history[i]);
    }

    wrefresh(win_chat);
    pthread_mutex_unlock(&ui_lock);
}

/* Append formatted message to chat history and print to chat window */
void print_chat_colored(int pair, const char *fmt, ...) {
    char msg_buf[1024];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(msg_buf, sizeof(msg_buf), fmt, ap);
    va_end(ap);

    if (chat_count < MAX_HISTORY) {
        chat_history[chat_count++] = strdup(msg_buf);
    } else {
        free(chat_history[0]);
        memmove(&chat_history[0], &chat_history[1], sizeof(char*) * (MAX_HISTORY - 1));
        chat_history[MAX_HISTORY - 1] = strdup(msg_buf);
    }

    pthread_mutex_lock(&ui_lock);
    wattron(win_chat, COLOR_PAIR(pair));
    wprintw(win_chat, "%s", msg_buf);
    wattroff(win_chat, COLOR_PAIR(pair));
    wrefresh(win_chat);
    pthread_mutex_unlock(&ui_lock);
}

/* Refresh chat window showing only messages containing filter (or all) */
void refresh_filtered_chat(const char *filter) {
    pthread_mutex_lock(&ui_lock);
    werase(win_chat);
    box(win_chat, 0, 0);
    mvwprintw(win_chat, 0, 2, " Chat ");

    int lines = getmaxy(win_chat) - 2;
    int shown = 0;

    for (int i = 0; i < chat_count && shown < lines; i++) {
        if (strcmp(filter, "all") == 0 || strstr(chat_history[i], filter) != NULL) {
            mvwprintw(win_chat, shown + 1, 1, "%s", chat_history[i]);
            shown++;
        }
    }

    wrefresh(win_chat);
    pthread_mutex_unlock(&ui_lock);
}

/* Detect symbolic messages (e.g. status notifications enclosed in brackets) */
int is_symbolic(const char *msg) {
    return (msg && strchr(msg, '[') && strchr(msg, ']'));
}

/* Update the users window.
   If list != NULL and non-empty: parse comma-separated user list from server.
   If list == NULL or empty: simply repaint using current user_list array.
   Highlight selected_user_index with reverse video.
*/
void update_userlist(const char *list) {
    pthread_mutex_lock(&ui_lock);

    if (list != NULL && strlen(list) > 0) {
        char *copy = strdup(list);
        char *tok = strtok(copy, ",");
        user_count = 0;
        while (tok && user_count < MAX_USERS) {
            strncpy(user_list[user_count], tok, MAX_NAME_LEN - 1);
            user_list[user_count][MAX_NAME_LEN - 1] = '\0';
            user_count++;
            tok = strtok(NULL, ",");
        }
        free(copy);

        if (selected_user_index >= user_count)
            selected_user_index = user_count - 1;
        if (selected_user_index < 0 && user_count > 0)
            selected_user_index = 0;
    }

    werase(win_users);
    box(win_users, 0, 0);
    mvwprintw(win_users, 0, 2, " Users ");

    int max_rows = getmaxy(win_users) - 2;
    if (user_scroll_offset < 0) user_scroll_offset = 0;
    if (user_scroll_offset > user_count - max_rows)
        user_scroll_offset = user_count - max_rows;
    if (user_scroll_offset < 0) user_scroll_offset = 0;

    int start = user_scroll_offset;
    int end = start + max_rows;
    if (end > user_count) end = user_count;

    for (int i = start, row = 1; i < end; i++, row++) {
        if (i == selected_user_index) wattron(win_users, A_REVERSE);

        if (strcmp(user_list[i], username) == 0)
            wattron(win_users, COLOR_PAIR(5));

        mvwprintw(win_users, row, 1, "%s", user_list[i]);

        if (strcmp(user_list[i], username) == 0)
            wattroff(win_users, COLOR_PAIR(5));
        if (i == selected_user_index) wattroff(win_users, A_REVERSE);
    }

    wrefresh(win_users);
    pthread_mutex_unlock(&ui_lock);
}

/* Receiver thread: reads framed messages and updates UI appropriately */
void *recv_thread_fn(void *arg) {
    (void)arg;
    char buf[MAX_MSG_LEN + 1];

    while (!exiting) {
        ssize_t r = recv_message_framed(sockfd, buf, sizeof(buf));
        if (r == 0) break;
        if (r < 0) {
            if (r == -2) continue; /* message too big, skipped */
            break;
        }

        if (strncmp(buf, "[userlist]", 10) == 0) {
            update_userlist(buf + 10);
            continue;
        }

        if (strstr(buf, username)) {
            print_chat_colored(5, "%s\n", buf);
            continue;
        }

        if (strstr(buf, "[group]")) {
            print_chat_colored(2, "%s\n", buf);
        } else if (strstr(buf, "[private]")) {
            print_chat_colored(3, "%s\n", buf);
        } else if (is_symbolic(buf)) {
            print_chat_colored(4, "%s\n", buf);
        } else {
            print_chat_colored(1, "%s\n", buf);
        }
    }

    print_chat_colored(1, "[client] Disconnected from server.\n");
    return NULL;
}

/* SIGINT handler: mark exit and close socket */
void sigint_handler(int sig) {
    (void)sig;
    exiting = 1;
    if (sockfd >= 0) {
        shutdown(sockfd, SHUT_RDWR);
        close(sockfd);
        sockfd = -1;
    }
}

/* Validate username: 3-20 alphanumeric characters */
int is_valid_username(const char *name) {
    if (!name) return 0;
    size_t len = strlen(name);
    if (len < 3 || len > 20) return 0;
    for (size_t i = 0; i < len; ++i) {
        if (!isalnum((unsigned char)name[i])) return 0;
    }
    return 1;
}

/* Entry point */
int main(int argc, char *argv[]){
    struct sigaction sa;
    sa.sa_handler = sigint_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGINT, &sa, NULL);

    init_ui();

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) { shutdown_ui(); perror("socket"); return 1; }

    struct sockaddr_in srv;
    memset(&srv, 0, sizeof(srv));
    srv.sin_family = AF_INET;
    //dynamic IP and port handling
    if (argc != 3) {
        shutdown_ui();
        printf("Usage: %s <server_ip> <port>\n", argv[0]);
        return 1;
    }

    const char *server_ip = argv[1];
    int port = atoi(argv[2]);

    srv.sin_port = htons(port);
    if (inet_pton(AF_INET, server_ip, &srv.sin_addr) != 1) {
        shutdown_ui();
        fprintf(stderr, "Invalid IP address.\n");
        close(sockfd);
        return 1;
    }

    if (connect(sockfd, (struct sockaddr *)&srv, sizeof(srv)) < 0) {
        shutdown_ui();
        perror("connect");
        close(sockfd);
        return 1;
    }


    pthread_mutex_lock(&ui_lock);
    mvwprintw(win_input, 1, 1, "Enter username: ");
    { int y, x; getyx(win_input, y, x); wmove(win_input, y, x); }
    wrefresh(win_input);
    pthread_mutex_unlock(&ui_lock);

    char input[MAX_INPUT_LEN + 1];
    echo();
    curs_set(1);
    wgetnstr(win_input, username, (int)sizeof(username) - 1);
    noecho();
    curs_set(0);
    username[strcspn(username, "\n")] = '\0';

    if (!is_valid_username(username)) {
        print_chat_colored(1, "[client] Invalid username (3-20 alnum chars required).\n");
        sleep(2);
        shutdown_ui();
        close(sockfd);
        return 1;
    }

    if (send_message_framed(sockfd, username, (uint32_t)strlen(username)) != 0) {
        print_chat_colored(1, "[client] Failed to send username.\n");
        shutdown_ui();
        close(sockfd);
        return 1;
    }

    char srv_resp[MAX_MSG_LEN + 1];
    ssize_t rr = recv_message_framed(sockfd, srv_resp, sizeof(srv_resp));
    if (rr <= 0) {
        print_chat_colored(1, "[client] No response from server.\n");
        shutdown_ui();
        close(sockfd);
        return 1;
    }
    srv_resp[rr] = '\0';
    if (strstr(srv_resp, "Invalid") || strstr(srv_resp, "taken")) {
        print_chat_colored(1, "[server] %s\n", srv_resp);
        sleep(2);
        shutdown_ui();
        close(sockfd);
        return 1;
    }

    pthread_t recv_thread;
    if (pthread_create(&recv_thread, NULL, recv_thread_fn, NULL) != 0) {
        print_chat_colored(1, "[client] Failed to create receive thread.\n");
        shutdown_ui();
        close(sockfd);
        return 1;
    }
    pthread_detach(recv_thread);

    char framed[MAX_MSG_LEN + 1];

    while (!exiting) {
        pthread_mutex_lock(&ui_lock);
        werase(win_input);
        box(win_input, 0, 0);

        /* features box: a small separate header line inside input window */
        mvwprintw(win_input, 0, 2, " Features ");
        /* draw a small features box area below the top border */
        mvwprintw(win_input, 0, 14, "[ /quit | /to <user> | @user msg | PgUp/PgDn scroll | a=all]");

        /* input prompt */
        mvwprintw(win_input, 1, 1, "To [%s]: ", target);
        { int y, x; getyx(win_input, y, x); wmove(win_input, y, x); }
        wrefresh(win_input);
        pthread_mutex_unlock(&ui_lock);

        int ch = wgetch(win_input);

        /* scrolling */
        if (ch == KEY_PPAGE) { scroll_chat(-1); continue; }
        if (ch == KEY_NPAGE) { scroll_chat(1); continue; }

        /* Navigate user list with arrows: update selected_user and refresh filtered chat */
        if (ch == KEY_UP) {
            if (selected_user_index > 0)
                selected_user_index--;

            if (selected_user_index < user_scroll_offset)
                user_scroll_offset--;

            update_userlist(NULL);
            if (selected_user_index >= 0)
                refresh_filtered_chat(user_list[selected_user_index]);
            else
                refresh_filtered_chat("all");
            continue;
        }

        if (ch == KEY_DOWN) {
            if (selected_user_index < user_count - 1)
                selected_user_index++;

            int max_rows = getmaxy(win_users) - 2;
            if (selected_user_index >= user_scroll_offset + max_rows)
                user_scroll_offset++;

            update_userlist(NULL);
            refresh_filtered_chat(user_list[selected_user_index]);
            continue;
        }


        /* Enter selects current filtered user to be target for sending messages */
        if (ch == 10) {
            if (selected_user_index >= 0 && selected_user_index < user_count) {
                strncpy(target, selected_user, sizeof(target) - 1);
                target[sizeof(target) - 1] = '\0';
            }
            continue;
        }

        /* 'a' resets filter to show all messages */
        if (ch == 'a' || ch == 'A') {
            strcpy(selected_user, "all");
            selected_user_index = -1;
            refresh_filtered_chat("all");
            update_userlist(NULL);
            continue;
        }

        /* otherwise assume user will type a message: push character back and read whole line */
        ungetch(ch);

        echo();
        curs_set(1);
        wgetnstr(win_input, input, MAX_INPUT_LEN);
        noecho();
        curs_set(0);

        input[strcspn(input, "\n")] = '\0';
        if (exiting) break;
        if (strlen(input) == 0) continue;

        if (strcmp(input, "/quit") == 0) {
            print_chat_colored(1, "[client] Quitting...\n");
            break;
        }

        if (strncmp(input, "/to ", 4) == 0) {
            strncpy(target, input + 4, sizeof(target) - 1);
            target[sizeof(target) - 1] = '\0';
            continue;
        }

        /* one-time private message with @username prefix */
        if (input[0] == '@') {
            char tmp_target[MAX_TARGET_LEN];
            const char *space = strchr(input, ' ');
            if (space) {
                size_t name_len = space - (input + 1);
                if (name_len > 0 && name_len < sizeof(tmp_target)) {
                    strncpy(tmp_target, input + 1, name_len);
                    tmp_target[name_len] = '\0';

                    const char *msg_text = space + 1;
                    if (strlen(msg_text) > 0) {
                        const char *type = "private";
                        int n = snprintf(framed, sizeof(framed), "%s|%s|%s|%s\n",
                                         type, username, tmp_target, msg_text);
                        if (n > 0 && n < (int)sizeof(framed)) {
                            send_message_framed(sockfd, framed, (uint32_t)strlen(framed));
                            print_chat_colored(3, "[private one-time] %s -> %s: %s\n",
                                               username, tmp_target, msg_text);
                        }
                    }
                }
            }
            continue;
        }
        
        /* normal send: group or private based on current target */
        const char *type = (strcmp(target, "all") == 0) ? "group" : "private";
        int n = snprintf(framed, sizeof(framed), "%s|%s|%s|%s\n", type, username, target, input);
        if (n < 0 || n >= (int)sizeof(framed)) {
            print_chat_colored(1, "[client] Message too long.\n");
            continue;
        }

        if (send_message_framed(sockfd, framed, (uint32_t)strlen(framed)) != 0) {
            print_chat_colored(1, "[client] Failed to send message.\n");
            break;
        }

        print_chat_colored(5, "[%s] %s -> %s: %s\n", type, username, target, input);
    }

    /* shutdown */
    exiting = 1;
    if (sockfd >= 0) {
        shutdown(sockfd, SHUT_RDWR);
        close(sockfd);
        sockfd = -1;
    }

    /* free chat history */
    for (int i = 0; i < chat_count; ++i) {
        free(chat_history[i]);
        chat_history[i] = NULL;
    }

    usleep(100000);
    shutdown_ui();
    return 0;
}
