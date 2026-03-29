#!/usr/bin/env python3
"""
Terminal Chat Application - Complete Documentation PDF Generator
"""

from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'Terminal-Based Chat Application - Complete Guide', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', fill=True)
        self.ln(4)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(0, 0, 128)
        self.cell(0, 8, title, 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def code_block(self, code):
        self.set_font('Courier', '', 9)
        self.set_fill_color(240, 240, 240)
        for line in code.split('\n'):
            self.cell(0, 5, line, 0, 1, 'L', fill=True)
        self.ln(2)
        self.set_font('Helvetica', '', 10)

    def table_row(self, col1, col2, header=False):
        self.set_font('Helvetica', 'B' if header else '', 9)
        self.cell(60, 7, col1, 1)
        self.cell(0, 7, col2, 1, 1)

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# ===== TITLE PAGE =====
pdf.set_font('Helvetica', 'B', 20)
pdf.ln(30)
pdf.cell(0, 15, 'Terminal-Based Chat Application', 0, 1, 'C')
pdf.set_font('Helvetica', 'B', 16)
pdf.cell(0, 10, 'Complete Documentation & Guide', 0, 1, 'C')
pdf.ln(10)
pdf.set_font('Helvetica', '', 12)
pdf.cell(0, 8, 'Name: Md. Tofazzol Alam Rahat', 0, 1, 'C')
pdf.cell(0, 8, 'Roll: BSSE-1740', 0, 1, 'C')
pdf.cell(0, 8, 'Course: Structured Programming Lab', 0, 1, 'C')
pdf.ln(20)

# ===== TABLE OF CONTENTS =====
pdf.add_page()
pdf.chapter_title('Table of Contents')
toc_items = [
    '1. How to Run - Commands (IP, Port)',
    '2. Server Code (bsse_1740_server.c) - Complete Explanation',
    '3. Client Code (bsse_1740_client.c) - Complete Explanation',
    '4. Header Files (.h) - Line by Line Explanation',
    '5. Alternative Approaches',
    '6. Message Protocol',
    '7. Quick Reference'
]
for item in toc_items:
    pdf.body_text(item)

# ===== SECTION 1: HOW TO RUN =====
pdf.add_page()
pdf.chapter_title('1. HOW TO RUN - Commands with IP & Port')

pdf.section_title('Step 1: Install Required Libraries')
pdf.body_text('Linux/Ubuntu-te ncurses library install korte hobe:')
pdf.code_block('sudo apt install libncurses5-dev libncursesw5-dev')

pdf.section_title('Step 2: Compile Server')
pdf.body_text('Server compile korar command:')
pdf.code_block('gcc bsse_1740_server.c -o bsse_1740_server -lpthread')
pdf.body_text('''-lpthread: pthread library link kore (multithreading er jonno)
-o bsse_1740_server: output file er naam''')

pdf.section_title('Step 3: Compile Client')
pdf.body_text('Client compile korar command:')
pdf.code_block('gcc bsse_1740_client.c -o bsse_1740_client -lncurses -lpthread')
pdf.body_text('''-lncurses: ncurses library (UI er jonno)
-lpthread: pthread library (multithreading er jonno)''')

pdf.section_title('Step 4: Run Server')
pdf.body_text('Server start korte:')
pdf.code_block('./bsse_1740_server')
pdf.body_text('Server automatically port 8080-te listen korbe.')

pdf.section_title('Step 5: Run Client')
pdf.body_text('Client start korte (server_ip aar port dite hobe):')
pdf.code_block('./bsse_1740_client <server_ip> <port>')
pdf.body_text('Examples:')
pdf.code_block('''# Same computer-e test korte (localhost):
./bsse_1740_client 127.0.0.1 8080

# LAN-e onno computer-e connect korte:
./bsse_1740_client 192.168.1.100 8080

# Public IP diye connect korte:
./bsse_1740_client 13.127.60.129 8080''')

pdf.section_title('IP Address Kibhabe Pabo?')
pdf.body_text('Server er IP address ber korar jonno:')
pdf.code_block('''# Linux-e:
hostname -I
# or
ip addr show

# Windows-e:
ipconfig''')

# ===== SECTION 2: SERVER CODE EXPLANATION =====
pdf.add_page()
pdf.chapter_title('2. SERVER CODE (bsse_1740_server.c) - Complete Explanation')

pdf.section_title('2.1 Header Files - Kon File Ki Kaj Kore')
pdf.body_text('''Protiita #include line er bistorito byakhya:''')

headers_server = [
    ('#include <stdio.h>', 'Standard Input/Output - printf(), perror(), fopen(), fclose(), fputs()'),
    ('#include <stdlib.h>', 'Standard Library - malloc(), free(), exit(), atoi()'),
    ('#include <string.h>', 'String operations - strlen(), strcmp(), strcpy(), strncpy(), memset(), strdup()'),
    ('#include <unistd.h>', 'UNIX standard - close(), read(), write(), sleep()'),
    ('#include <pthread.h>', 'POSIX Threads - pthread_create(), pthread_mutex_lock/unlock(), pthread_detach()'),
    ('#include <netinet/in.h>', 'Internet address structures - struct sockaddr_in, INADDR_ANY'),
    ('#include <ctype.h>', 'Character type checking - isalnum() for username validation'),
    ('#include <time.h>', 'Time functions - time(), localtime_r(), strftime() for timestamps'),
    ('#include <arpa/inet.h>', 'IP address conversion - htons(), htonl(), ntohl(), inet_pton()'),
    ('#include <signal.h>', 'Signal handling - sigaction(), SIGINT for Ctrl+C handling'),
    ('#include <stdint.h>', 'Fixed-width integers - uint32_t for 4-byte message length'),
    ('#include <errno.h>', 'Error numbers - EINTR check for interrupted system calls'),
]

for h, desc in headers_server:
    pdf.set_font('Courier', 'B', 9)
    pdf.cell(0, 6, h, 0, 1)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 5, f'   Kaj: {desc}', 0, 1)
pdf.ln(3)

pdf.section_title('2.2 #define Constants (Macros)')
pdf.code_block('''#define MAX_CLIENTS 100   // Maximum 100 clients connect korte parbe
#define MAX_MSG_LEN 4096  // Maximum message length 4KB
#define MAX_NAME_LEN 50   // Username maximum 50 characters
#define PORT 8080         // Server port number''')
pdf.body_text('''Keno #define use kora hoyeche?
- Code-e magic numbers avoid kora jay
- Ekbar change korle sobkhane change hoy
- Compile time-e value replace hoy (fast)

Alternative: const int MAX_CLIENTS = 100; 
(But #define preprocessor level-e kaj kore, array size declare korte easier)''')

pdf.section_title('2.3 Global Variables')
pdf.code_block('''static int server_sock = -1;              // Server socket descriptor
static int client_socks[MAX_CLIENTS];      // All client sockets array
static char *usernames[MAX_CLIENTS];       // All usernames array
static int client_count = 0;               // Currently connected clients
static pthread_mutex_t clients_lock;       // Mutex for thread safety
static volatile sig_atomic_t shutting_down = 0;  // Shutdown flag''')
pdf.body_text('''static: File scope-e limited, onno file theke access korte parbe na.
volatile sig_atomic_t: Signal handler theke safely modify kora jay.
pthread_mutex_t: Multiple threads ekisathe data access korle race condition avoid kore.''')

pdf.add_page()
pdf.section_title('2.4 Function: send_all()')
pdf.code_block('''ssize_t send_all(int sock, const void *buf, size_t len) {
    size_t sent = 0;
    const char *p = (const char *)buf;
    while (sent < len) {
        ssize_t n = send(sock, p + sent, len - sent, 0);
        if (n <= 0) {
            if (errno == EINTR) continue;  // Signal interrupted, retry
            return -1;                      // Error
        }
        sent += (size_t)n;
    }
    return (ssize_t)sent;
}''')
pdf.body_text('''Kaj: Shob bytes send kora ensure kore.
Keno dorkar? send() function ekbare shob data send korte pare na. 
TCP buffer full thakle partial send hoy.
Loop cholte thake until shob bytes send na hoy.

EINTR: System call signal diye interrupt hole retry kore.

Alternative: write() function use kora jeto, but send() socket-specific flags support kore.''')

pdf.section_title('2.5 Function: recv_all()')
pdf.code_block('''ssize_t recv_all(int sock, void *buf, size_t len) {
    size_t recvd = 0;
    char *p = (char *)buf;
    while (recvd < len) {
        ssize_t n = recv(sock, p + recvd, len - recvd, 0);
        if (n <= 0) {
            if (n == 0) return 0;          // Connection closed
            if (errno == EINTR) continue;   // Signal interrupt
            return -1;                      // Error
        }
        recvd += (size_t)n;
    }
    return (ssize_t)recvd;
}''')
pdf.body_text('''Kaj: Exactly len bytes receive kore.
TCP stream-based, tai data packet-e ashe na, stream-e ashe.
Ei function ensure kore exact amount of data receive hoyeche.

n == 0: Mane connection close hoyeche (peer disconnected).''')

pdf.section_title('2.6 Message Framing Functions')
pdf.code_block('''int send_message_framed(int sock, const char *data, uint32_t len) {
    uint32_t nl = htonl(len);  // Network byte order-e convert
    if (send_all(sock, &nl, sizeof(nl)) != sizeof(nl)) return -1;
    if (len > 0 && send_all(sock, data, len) != (ssize_t)len) return -1;
    return 0;
}''')
pdf.body_text('''Message Framing Concept:
TCP stream-based, tai kokhon message shesh hoyeche bujha jay na.
Solution: Message er age 4-byte length pathao.

htonl(): Host byte order -> Network byte order
(Intel CPU little-endian, network big-endian. Convert na korle different 
machines-e problem hobe.)

Frame Structure:
[4-byte length][actual message data]

Alternative: Delimiter-based (\n diye end mark) - but binary data-te problem hoy.''')

pdf.add_page()
pdf.section_title('2.7 Function: recv_message_framed()')
pdf.code_block('''ssize_t recv_message_framed(int sock, char *buf, size_t bufcap) {
    uint32_t nl;
    ssize_t r = recv_all(sock, &nl, sizeof(nl));
    if (r == 0) return 0;           // Connection closed
    if (r < 0) return -1;           // Error
    
    uint32_t len = ntohl(nl);       // Network -> Host order
    if (len >= bufcap) {            // Message too big
        char *tmp = malloc(len + 1);
        recv_all(sock, tmp, len);   // Read and discard
        free(tmp);
        return -2;                  // Signal oversized
    }
    
    r = recv_all(sock, buf, len);
    if (r <= 0) return r;
    buf[len] = '\\0';               // Null terminate
    return (ssize_t)len;
}''')
pdf.body_text('''Kaj: Framed message receive kore.
1. First 4 bytes read kore length pao
2. ntohl() diye host order-e convert
3. Length check kore (buffer overflow prevent)
4. Exact length bytes read kore
5. Null terminate kore (C string er jonno)

Return values:
>0: Successfully read bytes
0: Connection closed
-1: Error
-2: Message too large (discarded)''')

pdf.section_title('2.8 Function: format_time()')
pdf.code_block('''void format_time(char *out, size_t outlen) {
    time_t now = time(NULL);        // Current Unix timestamp
    struct tm tm_info;
    localtime_r(&now, &tm_info);    // Thread-safe local time
    strftime(out, outlen, "[%H:%M]", &tm_info);  // Format: [HH:MM]
}''')
pdf.body_text('''Kaj: Chat message-e timestamp add kore.
localtime_r(): Thread-safe version (localtime() non-reentrant).
strftime(): Time-ke formatted string-e convert kore.

Alternative: localtime() use kora jeto but thread-safe na.''')

pdf.section_title('2.9 Function: is_valid_username()')
pdf.code_block('''int is_valid_username(const char *name) {
    if (!name) return 0;
    size_t len = strlen(name);
    if (len < 3 || len > 20) return 0;
    for (size_t i = 0; i < len; ++i) {
        if (!isalnum((unsigned char)name[i])) return 0;
    }
    return 1;
}''')
pdf.body_text('''Validation rules:
- NULL check
- Length 3-20 characters
- Only alphanumeric (a-z, A-Z, 0-9)

isalnum(): ctype.h theke - alphabet or number check kore.
(unsigned char) cast: Negative char value-te undefined behavior avoid.

Keno validation dorkar?
- Security: Injection attack prevent
- Consistency: Special characters message parsing break korte pare''')

pdf.add_page()
pdf.section_title('2.10 Function: broadcast_all()')
pdf.code_block('''void broadcast_all(const char *msg, int exclude_sock) {
    pthread_mutex_lock(&clients_lock);      // Lock acquire
    for (int i = 0; i < client_count; ++i) {
        int s = client_socks[i];
        if (s == exclude_sock) continue;    // Skip sender
        send_message_framed(s, msg, (uint32_t)strlen(msg));
    }
    pthread_mutex_unlock(&clients_lock);    // Lock release
}''')
pdf.body_text('''Kaj: Shob connected clients-ke message pathay.
exclude_sock: Sender-ke skip kore (nijer message nije pabe na).

Mutex Locking:
- pthread_mutex_lock(): Critical section e dhukchi
- pthread_mutex_unlock(): Critical section shesh
- Keno? client_socks array multiple threads access kore
- Lock na dile race condition hobe (data corruption)

Alternative: Read-write lock use kora jeto (rwlock) - multiple readers allow.''')

pdf.section_title('2.11 Function: send_private()')
pdf.code_block('''void send_private(const char *recipient, const char *msg) {
    pthread_mutex_lock(&clients_lock);
    for (int i = 0; i < client_count; ++i) {
        if (usernames[i] && strcmp(usernames[i], recipient) == 0) {
            send_message_framed(client_socks[i], msg, (uint32_t)strlen(msg));
            break;  // Found recipient, exit loop
        }
    }
    pthread_mutex_unlock(&clients_lock);
}''')
pdf.body_text('''Kaj: Specific user-ke private message send kore.
strcmp(): Username match kore.
break: Recipient paile loop exit (efficiency).

Alternative: Hash table use korle O(1) lookup hoto O(n) er bodole.''')

pdf.section_title('2.12 Function: broadcast_userlist()')
pdf.code_block('''void broadcast_userlist(void) {
    char list[MAX_MSG_LEN];
    size_t off = 0;
    off += snprintf(list + off, sizeof(list) - off, "[userlist]");
    
    pthread_mutex_lock(&clients_lock);
    for (int i = 0; i < client_count; ++i) {
        if (usernames[i]) {
            off += snprintf(list + off, sizeof(list) - off, 
                           "%s,", usernames[i]);
        }
    }
    pthread_mutex_unlock(&clients_lock);
    
    strncat(list, "\\n", sizeof(list) - strlen(list) - 1);
    broadcast_all(list, -1);  // -1 = don't exclude anyone
}''')
pdf.body_text('''Kaj: Active user list shob client-ke pathay.
Format: [userlist]user1,user2,user3,
Client ei prefix dekhe UI update kore.

snprintf(): Buffer overflow safe formatting.
off variable: Offset track kore, string append korte help kore.''')

pdf.add_page()
pdf.section_title('2.13 Function: save_history()')
pdf.code_block('''void save_history(const char *msg) {
    FILE *fp = fopen("chat_history.txt", "a");  // Append mode
    if (!fp) return;
    fputs(msg, fp);
    fclose(fp);
}''')
pdf.body_text('''Kaj: Message chat_history.txt file-e save kore.
"a" mode: Append - existing content thakbe, niche add hobe.

Alternative: 
- fprintf() use kora jeto
- mmap() use kore memory-mapped file (faster)
- Database use kora jeto (SQLite)''')

pdf.section_title('2.14 Function: remove_client_by_socket()')
pdf.code_block('''void remove_client_by_socket(int sock) {
    pthread_mutex_lock(&clients_lock);
    for (int i = 0; i < client_count; ++i) {
        if (client_socks[i] == sock) {
            free(usernames[i]);  // Free allocated username
            // Shift remaining elements left
            for (int j = i; j < client_count - 1; ++j) {
                client_socks[j] = client_socks[j + 1];
                usernames[j] = usernames[j + 1];
            }
            client_count--;
            break;
        }
    }
    pthread_mutex_unlock(&clients_lock);
}''')
pdf.body_text('''Kaj: Disconnected client-er data remove kore.
Memory cleanup: strdup() diye allocate kora username free kora hoy.
Array shift: Gap fill up kore (O(n) complexity).

Alternative: Linked list use korle O(1) removal hoto.''')

pdf.section_title('2.15 Function: handle_client() - Client Handler Thread')
pdf.code_block('''void *handle_client(void *arg) {
    int sock = *(int *)arg;
    free(arg);  // Free the malloc'd argument
    
    char buf[MAX_MSG_LEN + 1];
    char username[MAX_NAME_LEN];
    
    // Receive username
    ssize_t r = recv_message_framed(sock, buf, sizeof(buf));
    if (r <= 0) { close(sock); return NULL; }
    
    strncpy(username, buf, sizeof(username) - 1);
    username[strcspn(username, "\\n")] = '\\0';  // Remove newline
    
    // Validate username
    if (!is_valid_username(username)) {
        send_message_framed(sock, "[server] Invalid username\\n", 27);
        close(sock);
        return NULL;
    }
    // ... (continued)
}''')
pdf.body_text('''Kaj: Each client-er jonno separate thread-e run kore.
void *arg: pthread_create() theke argument pass hoy.
*(int *)arg: Pointer dereference kore socket number pao.
free(arg): main() e malloc kora chilo, ekhane free.

strcspn(): "\\n" er position return kore, sei position-e null set kore.''')

pdf.add_page()
pdf.section_title('2.16 handle_client() - Message Processing Loop')
pdf.code_block('''    while (!shutting_down) {
        ssize_t len = recv_message_framed(sock, buf, sizeof(buf));
        if (len == 0) break;     // Connection closed
        if (len < 0) {
            if (len == -2) continue;  // Oversized, skip
            break;               // Error
        }
        
        // Parse: type|sender|target|content
        char *saveptr = NULL;
        char *type = strtok_r(buf, "|", &saveptr);
        char *sender = strtok_r(NULL, "|", &saveptr);
        char *target = strtok_r(NULL, "|", &saveptr);
        char *content = strtok_r(NULL, "\\n", &saveptr);
        
        if (type && sender && target && content) {
            if (strcmp(type, "group") == 0)
                broadcast_all(formatted, sock);
            else if (strcmp(type, "private") == 0)
                send_private(target, formatted);
        }
    }''')
pdf.body_text('''Message Format: type|sender|target|content
Examples:
- group|Rahat|all|Hello everyone!
- private|Rahat|John|Hi John!

strtok_r(): Thread-safe string tokenizer.
strtok() use korle thread-safe na hoto (static buffer use kore).
saveptr: Internal state store kore.

strcmp(): String compare - 0 mane equal.''')

pdf.section_title('2.17 Function: sigint_handler() - Graceful Shutdown')
pdf.code_block('''void sigint_handler(int sig) {
    (void)sig;  // Suppress unused parameter warning
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
}''')
pdf.body_text('''Kaj: Ctrl+C press korle gracefully shutdown kore.
SHUT_RDWR: Read aar Write both direction close.
shutdown() then close(): Proper cleanup sequence.

(void)sig: Unused parameter warning suppress korar idiom.

Alternative: atexit() handler use kora jeto cleanup er jonno.''')

pdf.add_page()
pdf.section_title('2.18 main() Function - Server Entry Point')
pdf.code_block('''int main(void) {
    // Signal handler setup
    struct sigaction sa;
    sa.sa_handler = sigint_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGINT, &sa, NULL);
    
    // Create socket
    server_sock = socket(AF_INET, SOCK_STREAM, 0);
    
    // Allow address reuse
    int opt = 1;
    setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    // Setup address
    struct sockaddr_in srv;
    memset(&srv, 0, sizeof(srv));
    srv.sin_family = AF_INET;
    srv.sin_addr.s_addr = INADDR_ANY;  // Listen on all interfaces
    srv.sin_port = htons(PORT);
    
    // Bind and listen
    bind(server_sock, (struct sockaddr *)&srv, sizeof(srv));
    listen(server_sock, 16);  // Backlog queue size
    
    printf("Server started on port %d\\n", PORT);''')
pdf.body_text('''Socket Creation Steps:
1. socket(): TCP socket create (AF_INET = IPv4, SOCK_STREAM = TCP)
2. setsockopt(): SO_REUSEADDR - restart korle "Address in use" error avoid
3. bind(): Local address assign
4. listen(): Incoming connections accept korar jonno ready

INADDR_ANY: Shob network interface-e listen kore.
htons(): Host-to-network short (port number convert).

Backlog (16): Maximum pending connections queue size.''')

pdf.code_block('''    // Accept loop
    while (!shutting_down) {
        struct sockaddr_in cli;
        socklen_t cli_len = sizeof(cli);
        int client_sock = accept(server_sock, 
                                 (struct sockaddr *)&cli, &cli_len);
        
        if (client_sock < 0) {
            if (errno == EINTR && shutting_down) break;
            continue;
        }
        
        int *pclient = malloc(sizeof(int));
        *pclient = client_sock;
        
        pthread_t tid;
        pthread_create(&tid, NULL, handle_client, pclient);
        pthread_detach(tid);  // Auto cleanup when thread exits
    }
    return 0;
}''')
pdf.body_text('''accept(): Blocking call - new connection er jonno wait kore.
Returns new socket descriptor for that specific client.

malloc(sizeof(int)): Socket number heap-e store kore thread-ke pass korar jonno.
(Local variable pass korle race condition hobe - overwritten hoye jabe.)

pthread_create(): New thread create kore client handle korar jonno.
pthread_detach(): Thread exit korle automatically cleanup hobe, join() lagbe na.

Alternative: Thread pool use kora jeto efficiency er jonno.''')

# ===== SECTION 3: CLIENT CODE =====
pdf.add_page()
pdf.chapter_title('3. CLIENT CODE (bsse_1740_client.c) - Complete Explanation')

pdf.section_title('3.1 Additional Headers (Client-specific)')
pdf.code_block('''#include <ncurses.h>   // Terminal UI library
#include <stdarg.h>    // Variable argument lists (va_list)''')
pdf.body_text('''ncurses.h: Terminal-based graphical UI create kore.
- Windows (panels) create kora jay
- Colors, borders, cursor control
- Keyboard input handling

stdarg.h: Variable number of arguments handle kore (printf-like functions).
va_list, va_start, va_end macros.''')

pdf.section_title('3.2 Client-specific Constants')
pdf.code_block('''#define MAX_TARGET_LEN 50   // Private message target name
#define MAX_INPUT_LEN  800  // User input buffer
#define MAX_HISTORY    500  // Chat history lines to keep
#define MAX_USERS      100  // Maximum users in list''')

pdf.section_title('3.3 UI Windows and State Variables')
pdf.code_block('''static WINDOW *win_users = NULL;  // Left panel - user list
static WINDOW *win_chat  = NULL;  // Right panel - chat messages
static WINDOW *win_input = NULL;  // Bottom panel - input box

static char username[MAX_NAME_LEN] = {0};
static char target[MAX_TARGET_LEN] = "all";  // Default: group chat
static int sockfd = -1;                       // Socket descriptor
static volatile sig_atomic_t exiting = 0;     // Exit flag

static pthread_mutex_t ui_lock = PTHREAD_MUTEX_INITIALIZER;

static char *chat_history[MAX_HISTORY];  // Message history buffer
static int chat_count = 0;                // Total messages
static int scroll_offset = 0;             // Scroll position''')
pdf.body_text('''WINDOW*: ncurses window pointer.
PTHREAD_MUTEX_INITIALIZER: Static mutex initialization.
chat_history: Pointer array - each points to strdup'd message.''')

pdf.add_page()
pdf.section_title('3.4 Function: init_ui() - UI Initialization')
pdf.code_block('''void init_ui(void) {
    initscr();        // Initialize ncurses
    cbreak();         // Disable line buffering
    noecho();         // Don't echo typed characters
    start_color();    // Enable colors
    
    // Define color pairs
    init_pair(1, COLOR_CYAN,    COLOR_BLACK);  // Generic
    init_pair(2, COLOR_GREEN,   COLOR_BLACK);  // Group msg
    init_pair(3, COLOR_YELLOW,  COLOR_BLACK);  // Private msg
    init_pair(4, COLOR_MAGENTA, COLOR_BLACK);  // System
    init_pair(5, COLOR_BLUE,    COLOR_BLACK);  // Current user
    
    // Calculate window sizes
    int height = LINES / 3;  // LINES = terminal rows
    
    // Create windows: newwin(height, width, start_y, start_x)
    win_users = newwin(height, COLS / 4, 0, 0);
    win_chat  = newwin(height * 2, COLS - COLS / 4, 0, COLS / 4);
    win_input = newwin(height, COLS, height * 2, 0);
    
    scrollok(win_chat, TRUE);   // Enable scrolling
    keypad(win_input, TRUE);    // Enable arrow keys
    keypad(win_chat, TRUE);
    
    // Draw borders and titles
    box(win_users, 0, 0);
    box(win_chat, 0, 0);
    box(win_input, 0, 0);
}''')
pdf.body_text('''ncurses UI Setup:
initscr(): Terminal ke ncurses mode-e niye jay.
cbreak(): Character-by-character input (Enter er jonno wait na kore).
noecho(): Typed character screen-e show korbe na (nijer control).
LINES, COLS: Terminal er total rows aar columns (global).

newwin(): New window create kore specific position aar size-e.

Alternative: PDCurses (Windows native), termbox (simpler API).''')

pdf.section_title('3.5 Function: shutdown_ui() - Cleanup')
pdf.code_block('''void shutdown_ui(void) {
    pthread_mutex_lock(&ui_lock);
    if (win_users) { delwin(win_users); win_users = NULL; }
    if (win_chat)  { delwin(win_chat);  win_chat  = NULL; }
    if (win_input) { delwin(win_input); win_input = NULL; }
    pthread_mutex_unlock(&ui_lock);
    endwin();  // Restore terminal to normal mode
}''')
pdf.body_text('''delwin(): Window memory free kore.
endwin(): ncurses mode exit kore, terminal normal state-e fire ashe.
NULL check: Double-free avoid korar jonno.''')

pdf.add_page()
pdf.section_title('3.6 Function: scroll_chat() - Manual Scrolling')
pdf.code_block('''void scroll_chat(int direction) {
    scroll_offset += direction;
    // Boundary checks
    if (scroll_offset < 0) scroll_offset = 0;
    if (scroll_offset > chat_count - 1) 
        scroll_offset = chat_count - 1;
    
    pthread_mutex_lock(&ui_lock);
    werase(win_chat);           // Clear window
    box(win_chat, 0, 0);        // Redraw border
    
    int lines = getmaxy(win_chat) - 2;  // Available lines
    int start = (chat_count > lines) ? 
                chat_count - lines - scroll_offset : 0;
    
    for (int i = start, row = 1; i < end; ++i, ++row) {
        mvwprintw(win_chat, row, 1, "%s", chat_history[i]);
    }
    
    wrefresh(win_chat);
    pthread_mutex_unlock(&ui_lock);
}''')
pdf.body_text('''Kaj: PgUp/PgDn key press-e chat scroll kore.
werase(): Window content clear kore.
getmaxy(): Window er height return kore.
mvwprintw(): Move cursor and print (row, col position specify kore).
wrefresh(): Window screen-e render kore.''')

pdf.section_title('3.7 Function: print_chat_colored() - Formatted Output')
pdf.code_block('''void print_chat_colored(int pair, const char *fmt, ...) {
    char msg_buf[1024];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(msg_buf, sizeof(msg_buf), fmt, ap);
    va_end(ap);
    
    // Store in history
    if (chat_count < MAX_HISTORY) {
        chat_history[chat_count++] = strdup(msg_buf);
    } else {
        free(chat_history[0]);  // Remove oldest
        memmove(&chat_history[0], &chat_history[1], 
                sizeof(char*) * (MAX_HISTORY - 1));
        chat_history[MAX_HISTORY - 1] = strdup(msg_buf);
    }
    
    // Print with color
    pthread_mutex_lock(&ui_lock);
    wattron(win_chat, COLOR_PAIR(pair));   // Color on
    wprintw(win_chat, "%s", msg_buf);
    wattroff(win_chat, COLOR_PAIR(pair));  // Color off
    wrefresh(win_chat);
    pthread_mutex_unlock(&ui_lock);
}''')
pdf.body_text('''Variable Arguments: printf() er moto flexible function.
va_list ap: Argument list holder.
va_start(ap, fmt): Last fixed parameter er pore arguments access.
vsnprintf(): va_list diye formatted string create.
va_end(): Cleanup.

Circular Buffer Logic:
- MAX_HISTORY e pouche gele oldest delete, shift left, new add.
- memmove(): Overlapping memory regions safely copy kore.
- memcpy() safe na overlap er ksetre.''')

pdf.add_page()
pdf.section_title('3.8 Function: update_userlist() - User List Display')
pdf.code_block('''void update_userlist(const char *list) {
    pthread_mutex_lock(&ui_lock);
    
    if (list != NULL && strlen(list) > 0) {
        char *copy = strdup(list);
        char *tok = strtok(copy, ",");
        user_count = 0;
        while (tok && user_count < MAX_USERS) {
            strncpy(user_list[user_count], tok, MAX_NAME_LEN - 1);
            user_count++;
            tok = strtok(NULL, ",");
        }
        free(copy);
    }
    
    werase(win_users);
    box(win_users, 0, 0);
    
    for (int i = start, row = 1; i < end; i++, row++) {
        // Highlight selected user
        if (i == selected_user_index) 
            wattron(win_users, A_REVERSE);
        
        // Highlight current user differently
        if (strcmp(user_list[i], username) == 0)
            wattron(win_users, COLOR_PAIR(5));
        
        mvwprintw(win_users, row, 1, "%s", user_list[i]);
        
        wattroff(win_users, A_REVERSE);
        wattroff(win_users, COLOR_PAIR(5));
    }
    wrefresh(win_users);
    pthread_mutex_unlock(&ui_lock);
}''')
pdf.body_text('''Kaj: User list window update kore.
strtok(): Comma-separated values parse kore.
A_REVERSE: Background/foreground swap kore (selection highlight).

Server "[userlist]user1,user2," pathay, ei function parse kore display kore.''')

pdf.section_title('3.9 Function: recv_thread_fn() - Receiver Thread')
pdf.code_block('''void *recv_thread_fn(void *arg) {
    (void)arg;
    char buf[MAX_MSG_LEN + 1];
    
    while (!exiting) {
        ssize_t r = recv_message_framed(sockfd, buf, sizeof(buf));
        if (r == 0) break;  // Connection closed
        if (r < 0) {
            if (r == -2) continue;  // Oversized, skip
            break;
        }
        
        // Handle userlist updates
        if (strncmp(buf, "[userlist]", 10) == 0) {
            update_userlist(buf + 10);
            continue;
        }
        
        // Color-code based on message type
        if (strstr(buf, "[group]")) {
            print_chat_colored(2, "%s\\n", buf);
        } else if (strstr(buf, "[private]")) {
            print_chat_colored(3, "%s\\n", buf);
        } else {
            print_chat_colored(1, "%s\\n", buf);
        }
    }
    return NULL;
}''')
pdf.body_text('''Kaj: Background-e server theke message receive kore UI update kore.
Separate thread-e run kore tai main thread input handle korte pare.
strstr(): Substring search - message type identify kore.
strncmp(): First n characters compare kore.''')

pdf.add_page()
pdf.section_title('3.10 main() Function - Client Entry Point')
pdf.code_block('''int main(int argc, char *argv[]) {
    // Signal handler setup
    struct sigaction sa;
    sa.sa_handler = sigint_handler;
    sigaction(SIGINT, &sa, NULL);
    
    init_ui();  // Initialize ncurses
    
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    
    // Parse command line arguments
    if (argc != 3) {
        shutdown_ui();
        printf("Usage: %s <server_ip> <port>\\n", argv[0]);
        return 1;
    }
    
    const char *server_ip = argv[1];
    int port = atoi(argv[2]);  // String to integer
    
    struct sockaddr_in srv;
    srv.sin_family = AF_INET;
    srv.sin_port = htons(port);
    inet_pton(AF_INET, server_ip, &srv.sin_addr);
    
    connect(sockfd, (struct sockaddr *)&srv, sizeof(srv));''')
pdf.body_text('''argc, argv: Command line arguments.
argc: Argument count.
argv[0]: Program name.
argv[1]: Server IP.
argv[2]: Port number.

atoi(): ASCII to integer conversion.
inet_pton(): IP string ke binary format-e convert kore.''')

pdf.section_title('3.11 main() - Input Processing Loop')
pdf.code_block('''    while (!exiting) {
        int ch = wgetch(win_input);  // Get character/key
        
        // Page Up/Down for scrolling
        if (ch == KEY_PPAGE) { scroll_chat(-1); continue; }
        if (ch == KEY_NPAGE) { scroll_chat(1); continue; }
        
        // Arrow keys for user selection
        if (ch == KEY_UP) {
            selected_user_index--;
            update_userlist(NULL);
            refresh_filtered_chat(user_list[selected_user_index]);
            continue;
        }
        
        // Process text input
        ungetch(ch);  // Push character back
        wgetnstr(win_input, input, MAX_INPUT_LEN);
        
        // Handle commands
        if (strcmp(input, "/quit") == 0) break;
        if (strncmp(input, "/to ", 4) == 0) {
            strncpy(target, input + 4, sizeof(target) - 1);
            continue;
        }
        
        // Handle @username private message
        if (input[0] == '@') { /* ... */ }
        
        // Send message
        const char *type = (strcmp(target, "all") == 0) ? 
                           "group" : "private";
        snprintf(framed, sizeof(framed), "%s|%s|%s|%s\\n", 
                 type, username, target, input);
        send_message_framed(sockfd, framed, strlen(framed));
    }''')
pdf.body_text('''wgetch(): Single key press read kore. Special keys (arrows, PgUp) er jonno
KEY_PPAGE, KEY_UP etc. constants return kore.

ungetch(): Character ke input buffer-e push back kore (unread).
wgetnstr(): Full line input read kore.

Commands:
/quit - Exit
/to <user> - Set private message target
@user <msg> - One-time private message''')

# ===== SECTION 4: HEADER FILES DETAILED =====
pdf.add_page()
pdf.chapter_title('4. HEADER FILES (.h) - Line by Line Explanation')

pdf.section_title('4.1 stdio.h (Standard Input/Output)')
pdf.body_text('''Functions used:''')
pdf.table_row('Function', 'Purpose', header=True)
pdf.table_row('printf()', 'Formatted output to stdout')
pdf.table_row('fprintf()', 'Formatted output to file/stderr')
pdf.table_row('perror()', 'Print error message with errno')
pdf.table_row('fopen()', 'Open file')
pdf.table_row('fclose()', 'Close file')
pdf.table_row('fputs()', 'Write string to file')
pdf.body_text('''Alternative: write() system call, but less convenient for formatted output.''')

pdf.section_title('4.2 stdlib.h (Standard Library)')
pdf.table_row('Function', 'Purpose', header=True)
pdf.table_row('malloc()', 'Allocate memory on heap')
pdf.table_row('free()', 'Deallocate memory')
pdf.table_row('exit()', 'Terminate program')
pdf.table_row('atoi()', 'String to integer')
pdf.body_text('''Alternative: calloc() (zero-initialized), realloc() (resize).''')

pdf.section_title('4.3 string.h (String Operations)')
pdf.table_row('Function', 'Purpose', header=True)
pdf.table_row('strlen()', 'String length')
pdf.table_row('strcmp()', 'Compare strings (0 = equal)')
pdf.table_row('strncpy()', 'Copy n characters (safer)')
pdf.table_row('strdup()', 'Duplicate string (malloc + copy)')
pdf.table_row('memset()', 'Fill memory with value')
pdf.table_row('memmove()', 'Copy memory (overlap safe)')
pdf.table_row('strcspn()', 'Find first char from set')
pdf.table_row('strtok_r()', 'Tokenize string (thread-safe)')
pdf.table_row('strstr()', 'Find substring')

pdf.section_title('4.4 unistd.h (UNIX Standard)')
pdf.table_row('Function', 'Purpose', header=True)
pdf.table_row('close()', 'Close file descriptor')
pdf.table_row('read()', 'Read from fd')
pdf.table_row('write()', 'Write to fd')
pdf.table_row('sleep()', 'Sleep for seconds')
pdf.table_row('usleep()', 'Sleep for microseconds')
pdf.body_text('''POSIX specific - Windows-e different APIs.''')

pdf.add_page()
pdf.section_title('4.5 pthread.h (POSIX Threads)')
pdf.table_row('Function/Type', 'Purpose', header=True)
pdf.table_row('pthread_t', 'Thread identifier type')
pdf.table_row('pthread_mutex_t', 'Mutex type')
pdf.table_row('pthread_create()', 'Create new thread')
pdf.table_row('pthread_detach()', 'Auto-cleanup on exit')
pdf.table_row('pthread_mutex_lock()', 'Acquire lock')
pdf.table_row('pthread_mutex_unlock()', 'Release lock')
pdf.body_text('''Alternative: C11 threads (<threads.h>), Windows threads.
Compile with -lpthread flag.''')

pdf.section_title('4.6 netinet/in.h & arpa/inet.h (Networking)')
pdf.table_row('Item', 'Purpose', header=True)
pdf.table_row('struct sockaddr_in', 'IPv4 socket address')
pdf.table_row('INADDR_ANY', 'Listen on all interfaces')
pdf.table_row('htons()', 'Host to network short')
pdf.table_row('htonl()', 'Host to network long')
pdf.table_row('ntohl()', 'Network to host long')
pdf.table_row('inet_pton()', 'IP string to binary')
pdf.body_text('''Byte order conversion essential for cross-platform compatibility.
Network = big-endian, Intel = little-endian.''')

pdf.section_title('4.7 signal.h (Signal Handling)')
pdf.table_row('Item', 'Purpose', header=True)
pdf.table_row('struct sigaction', 'Signal handler config')
pdf.table_row('sigaction()', 'Install signal handler')
pdf.table_row('sigemptyset()', 'Clear signal set')
pdf.table_row('SIGINT', 'Ctrl+C signal')
pdf.table_row('sig_atomic_t', 'Signal-safe integer')
pdf.body_text('''Alternative: signal() function (older, less reliable).''')

pdf.section_title('4.8 ncurses.h (Terminal UI)')
pdf.table_row('Function', 'Purpose', header=True)
pdf.table_row('initscr()', 'Initialize screen')
pdf.table_row('endwin()', 'End ncurses mode')
pdf.table_row('newwin()', 'Create window')
pdf.table_row('delwin()', 'Delete window')
pdf.table_row('wgetch()', 'Get character from window')
pdf.table_row('wgetnstr()', 'Get string from window')
pdf.table_row('mvwprintw()', 'Move and print')
pdf.table_row('wrefresh()', 'Update screen')
pdf.table_row('box()', 'Draw border')
pdf.table_row('wattron/wattroff()', 'Enable/disable attributes')
pdf.body_text('''Compile with -lncurses flag.
Alternative: termbox (simpler), FTXUI (C++).''')

# ===== SECTION 5: ALTERNATIVES =====
pdf.add_page()
pdf.chapter_title('5. ALTERNATIVE APPROACHES')

pdf.section_title('5.1 Threading Alternatives')
pdf.body_text('''Current: pthread (POSIX Threads)
Alternatives:
1. C11 Threads (<threads.h>) - Portable, but limited support
2. select()/poll()/epoll() - Single-threaded async I/O
3. libuv/libevent - Event-driven libraries
4. OpenMP - Parallel computing

epoll() example:
- Linux-specific, highly scalable
- Single thread-e thousands of connections handle kora jay
- Used by Nginx, Node.js''')

pdf.section_title('5.2 Data Structure Alternatives')
pdf.body_text('''Current: Arrays for client storage
Alternatives:
1. Linked List - O(1) insertion/deletion
2. Hash Table - O(1) lookup by username
3. Tree (Red-Black) - Sorted data

Current array approach O(n) search kore. Hash table use korle
username lookup O(1)-e hoto.''')

pdf.section_title('5.3 Protocol Alternatives')
pdf.body_text('''Current: Custom length-prefixed framing
Alternatives:
1. Line-based (\\n delimiter) - Simple but binary unsafe
2. HTTP/WebSocket - Browser compatible
3. Protocol Buffers - Efficient binary serialization
4. JSON over TCP - Human readable
5. MQTT - IoT messaging protocol''')

pdf.section_title('5.4 UI Alternatives')
pdf.body_text('''Current: ncurses (Terminal UI)
Alternatives:
1. termbox - Simpler API
2. notcurses - Modern ncurses alternative
3. Qt/GTK - GUI applications
4. Web interface - Browser-based''')

pdf.section_title('5.5 Security Improvements')
pdf.body_text('''Current: Plain TCP (no encryption)
Should add:
1. TLS/SSL - Encrypted communication (OpenSSL)
2. Authentication - Password/token based
3. Input sanitization - Already done (alphanumeric check)
4. Rate limiting - Prevent spam''')

# ===== SECTION 6: MESSAGE PROTOCOL =====
pdf.add_page()
pdf.chapter_title('6. MESSAGE PROTOCOL DETAILS')

pdf.section_title('6.1 Frame Structure')
pdf.code_block('''[4-byte length (network order)] [message payload]

Example:
Length: 00 00 00 1C (28 in decimal)
Payload: "group|Rahat|all|Hello World!\\n"''')

pdf.section_title('6.2 Message Format')
pdf.code_block('''type|sender|target|content\\n

Types:
- "group"   : Broadcast to all users
- "private" : Send to specific user

Examples:
group|Rahat|all|Hello everyone!
private|Rahat|John|Hey John, how are you?''')

pdf.section_title('6.3 Special Server Messages')
pdf.code_block('''[server] OK\\n              - Registration successful
[server] Invalid username\\n - Username rejected
[server] Username already taken\\n - Duplicate name
[userlist]user1,user2,\\n   - Active user list
[server] X has joined the chat.\\n
[server] X has left the chat.\\n''')

# ===== SECTION 7: QUICK REFERENCE =====
pdf.add_page()
pdf.chapter_title('7. QUICK REFERENCE')

pdf.section_title('Build Commands')
pdf.code_block('''# Server
gcc bsse_1740_server.c -o bsse_1740_server -lpthread

# Client  
gcc bsse_1740_client.c -o bsse_1740_client -lncurses -lpthread''')

pdf.section_title('Run Commands')
pdf.code_block('''# Start server (listens on port 8080)
./bsse_1740_server

# Connect client
./bsse_1740_client 127.0.0.1 8080        # localhost
./bsse_1740_client 192.168.1.100 8080    # LAN IP
./bsse_1740_client <public_ip> 8080      # Remote''')

pdf.section_title('Client Controls')
pdf.table_row('Key/Command', 'Action', header=True)
pdf.table_row('/quit', 'Exit chat')
pdf.table_row('/to <user>', 'Set private message target')
pdf.table_row('@user <msg>', 'One-time private message')
pdf.table_row('Page Up/Down', 'Scroll chat history')
pdf.table_row('Arrow Up/Down', 'Select user from list')
pdf.table_row('Enter', 'Confirm selection')
pdf.table_row('a', 'Show all messages (clear filter)')

pdf.section_title('Required Libraries')
pdf.code_block('''# Ubuntu/Debian
sudo apt install libncurses5-dev libncursesw5-dev build-essential

# Fedora
sudo dnf install ncurses-devel

# Arch
sudo pacman -S ncurses''')

pdf.section_title('File Structure')
pdf.table_row('File', 'Description', header=True)
pdf.table_row('bsse_1740_server.c', 'Multi-threaded chat server')
pdf.table_row('bsse_1740_client.c', 'ncurses-based chat client')
pdf.table_row('chat_history.txt', 'Server-side message log')

# Save PDF
output_path = '/home/rahat/terminal_chat_analysis/Terminal_Chat_Complete_Guide.pdf'
pdf.output(output_path)
print(f"PDF created: {output_path}")
