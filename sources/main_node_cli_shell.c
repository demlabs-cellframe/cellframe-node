
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/types.h>
#include <getopt.h>
#include <signal.h>
#include <string.h>
#include <assert.h>
#include <setjmp.h>
#include <locale.h>

#ifdef _WIN32
#include <winsock2.h>
#include <windows.h>
#include <mswsock.h>
#include <ws2tcpip.h>
#include <io.h>
#include <pthread.h>
#else
#include <sys/ttydefaults.h>
#endif

#include "dap_common.h"
#include "main_node_cli.h"
#include "main_node_cli_shell.h"

//#include "posixjmp.h"

#ifndef savestring
#define savestring(x) strcpy ((char *)malloc (1 + strlen (x)), (x))
#endif

typedef void rl_voidfunc_t(void);
typedef void rl_vintfunc_t(int);

/* Current prompt. */
char *rl_prompt = (char *) NULL;
int rl_visible_prompt_length = 0;

/* Non-zero means we have been called at least once before. */
static int rl_initialized;

/* The stuff that gets printed out before the actual text of the line.
 This is usually pointing to rl_prompt. */
char *rl_display_prompt = (char *) NULL;

/* Non-zero makes this the next keystroke to read. */
int rl_pending_input = 0;

/* Make this non-zero to return the current input_line. */
int rl_done;
/* Non-zero if the previous command was a kill command. */
int _rl_last_command_was_kill = 0;

/* Top level environment for readline_internal (). */
jmp_buf _rl_top_level;

/* Length of the current input line. */
int rl_end;

/* The character that can generate an EOF.  Really read from
 the terminal driver... just defaulted here. */
//int _rl_eof_char = CTRL('D');

#define NEWLINE '\n'

/* Input error; can be returned by (*rl_getc_function) if readline is reading
 a top-level command (RL_ISSTATE (RL_STATE_READCMD)). */
#define READERR         (-2)

/* Possible state values for rl_readline_state */
#define RL_STATE_NONE       0x000000        /* no state; before first call */

#define RL_STATE_INITIALIZING   0x0000001   /* initializing */
#define RL_STATE_INITIALIZED    0x0000002   /* initialization done */
#define RL_STATE_READCMD    0x0000008   /* reading a command key */
#define RL_STATE_INPUTPENDING   0x0020000   /* rl_execute_next called */
#define RL_STATE_TERMPREPPED    0x0000004   /* terminal is prepped */

/* Flags word encapsulating the current readline state. */
unsigned long rl_readline_state = RL_STATE_NONE;

#define RL_SETSTATE(x)      (rl_readline_state |= (x))
#define RL_UNSETSTATE(x)    (rl_readline_state &= ~(x))
#define RL_ISSTATE(x)       (rl_readline_state & (x))

/* The names of the streams that we do input and output to. */
FILE *rl_instream = (FILE *) NULL;
FILE *rl_outstream = (FILE *) NULL;

/**
 * Read one symbol
 */
unsigned char rl_getc(FILE *stream)
{
    int result;
    unsigned char c;

    while(1)
    {

#if defined (__MINGW32__)
        if (isatty (fileno (stream)))
        return (_getch ()); /* "There is no error return." */
#endif
        result = 0;
        if(result >= 0)
            result = read(fileno(stream), &c, sizeof(unsigned char));
        if(result == sizeof(unsigned char))
            return (c);

        /* If zero characters are returned, then the file that we are
         reading from is empty!  Return EOF in that case. */
        if(result == 0)
            return (EOF);
    }
}

/**
 *  Set up the prompt and expand it.  Called from readline()
 */
int rl_set_prompt(const char *prompt)
{
    free(rl_prompt);
    rl_prompt = prompt ? savestring(prompt) : (char *) NULL;
    rl_display_prompt = rl_prompt ? rl_prompt : "";
    fprintf(stdout, "%s", prompt);
    fflush(stdout);
    //rl_visible_prompt_length = rl_expand_prompt (rl_prompt);
    return 0;
}

/**
 *  Read a line of input.  Prompt with PROMPT.  An empty PROMPT means none.
 *  A return value of NULL means that EOF was encountered.
 */
char *rl_readline(const char *prompt)
{
    int value_size = 3, value_len = 0;
    char *value = DAP_NEW_Z_SIZE(char, value_size + 1);

    // Set up the prompt
    rl_set_prompt(prompt);

    // Read a line of input from the global rl_instream, doing output on the global rl_outstream.
    while(1)
    {
        unsigned char c = rl_getc(rl_instream);

        if(c == EOF || c == NEWLINE)
            break;
        value[value_len] = c;
        value_len++;
        if(value_len == value_size) {
            value_size += 32;
            value = realloc(value, value_size + 1);
        }
    }
    return (value);
}

static char* _rl_get_locale_var(const char *v)
{
    char *lspec;

    lspec = getenv("LC_ALL");
    if(lspec == 0 || *lspec == 0)
        lspec = getenv(v);
    if(lspec == 0 || *lspec == 0)
        lspec = getenv("LANG");

    return lspec;
}

/*
 * Query the right environment variables and call setlocale() to initialize
 * the C library locale settings.
 */
static char* _rl_init_locale(void)
{
    char *ret, *lspec;

    /* Set the LC_CTYPE locale category from environment variables. */
    lspec = _rl_get_locale_var("LC_CTYPE");
    /* Since _rl_get_locale_var queries the right environment variables,
     we query the current locale settings with setlocale(), and, if
     that doesn't return anything, we set lspec to the empty string to
     force the subsequent call to setlocale() to define the `native'
     environment. */
    if(lspec == 0 || *lspec == 0)
        lspec = setlocale(LC_CTYPE, (char *) NULL);
    if(lspec == 0)
        lspec = "";
    ret = setlocale(LC_CTYPE, lspec); /* ok, since it does not change locale */

    //_rl_utf8locale = (ret && *ret) ? utf8locale (ret) : 0;

    return ret;
}

/*
 *  Initialize readline (and terminal if not already).
 */
int rl_initialize(void)
{
    /* If we have never been called before, initialize the
     terminal and data structures. */
    if(rl_initialized == 0)
            {
        RL_SETSTATE(RL_STATE_INITIALIZING);
        rl_instream = (FILE *) stdin;
        rl_outstream = (FILE *) stdout;
        RL_UNSETSTATE(RL_STATE_INITIALIZING);
        rl_initialized++;
        RL_SETSTATE(RL_STATE_INITIALIZED);
    }
    else
        (void) _rl_init_locale(); /* check current locale */
    RL_SETSTATE(RL_STATE_INITIALIZING);
    rl_instream = (FILE *) stdin;
    rl_outstream = (FILE *) stdout;
    RL_UNSETSTATE(RL_STATE_INITIALIZING);
}

int parse_shell_options(char **argv, int arg_start, int arg_end)
{
    int arg_index;
    int arg_character, on_or_off, next_arg, i;
    char *o_option, *arg_string;

    arg_index = arg_start;
    while(arg_index != arg_end && (arg_string = argv[arg_index]) &&
            (*arg_string == '-' || *arg_string == '+'))
    {
        /* There are flag arguments, so parse them. */
        next_arg = arg_index + 1;

        /* A single `-' signals the end of options.  From the 4.3 BSD sh.
         An option `--' means the same thing; this is the standard
         getopt(3) meaning. */
        if(arg_string[0] == '-' &&
                (arg_string[1] == '\0' ||
                        (arg_string[1] == '-' && arg_string[2] == '\0')))
            return (next_arg);

        i = 1;
        on_or_off = arg_string[0];
        while(arg_character = arg_string[i++])
        {
            switch (arg_character)
            {
            case 'c':
                //want_pending_command = 1;
                break;

            case 'l':
                //make_login_shell = 1;
                break;

            case 's':
                //read_from_stdin = 1;
                break;

            case 'o':
                o_option = argv[next_arg];
                if(o_option == 0)
                        {
                    //list_minus_o_opts(-1, (on_or_off == '-') ? 0 : 1);
                    break;
                }
                //if(set_minus_o_option(on_or_off, o_option) != EXECUTION_SUCCESS)
                //    exit(EX_BADUSAGE);
                next_arg++;
                break;

            case 'O':
                /* Since some of these can be overridden by the normal
                 interactive/non-interactive shell initialization or
                 initializing posix mode, we save the options and process
                 them after initialization. */
                o_option = argv[next_arg];
                if(o_option == 0)
                        {
                    //shopt_listopt(o_option, (on_or_off == '-') ? 0 : 1);
                    break;
                }
                //add_shopt_to_alist(o_option, on_or_off);
                next_arg++;
                break;

            case 'D':
                //dump_translatable_strings = 1;
                break;

            default:
                break;
//                if(change_flag(arg_character, on_or_off) == FLAG_ERROR)
//                        {
//                    report_error(_("%c%c: invalid option"), on_or_off, arg_character);
//                    show_shell_usage(stderr, 0);
//                    exit(EX_BADUSAGE);
//                }
            }
        }
        /* Can't do just a simple increment anymore -- what about
         "bash -abouo emacs ignoreeof -hP"? */
        arg_index = next_arg;
    }

    return (arg_index);
}

/**
 *  Strip whitespace from the start and end of STRING.  Return a pointer into STRING.
 */
char * rl_stripwhite(char *string)
{
    register char *s, *t;

    for(s = string; whitespace(*s); s++)
        ;

    if(*s == 0)
        return (s);

    t = s + strlen(s) - 1;
    while(t > s && whitespace(*t))
        t--;
    *++t = '\0';

    return s;
}

/* The structure used to store a history entry. */
typedef struct _hist_entry {
    char *line;
    char *timestamp; /* char * rather than time_t for read/write */
    char *data;
} HIST_ENTRY;

/**
 *  Place STRING at the end of the history list.
 */
void add_history(const char *string)
{
    HIST_ENTRY *temp;
    //   The data field is set to NULL
    // TODO
}
