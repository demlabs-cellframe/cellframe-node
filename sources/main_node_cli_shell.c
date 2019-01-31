#include <locale.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ttydefaults.h>
#include <unistd.h>
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
int _rl_eof_char = CTRL('D');
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
//rl_vintfunc_t *rl_prep_term_function = rl_prep_terminal;
//rl_voidfunc_t *rl_deprep_term_function = rl_deprep_terminal;

/* Clear any pending input pushed with rl_execute_next() */
int
rl_clear_pending_input(void)
{
    rl_pending_input = 0;
    RL_UNSETSTATE(RL_STATE_INPUTPENDING);
    return 0;
}

int rl_getc(FILE *stream)
{
    int result;
    unsigned char c;

    while(1)
    {
//        RL_CHECK_SIGNALS();

        /* We know at this point that _rl_caught_signal == 0 */

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

/* Set up the prompt and expand it.  Called from readline() and
 rl_callback_handler_install (). */
int
rl_set_prompt(const char *prompt)
{
    free(rl_prompt);
    rl_prompt = prompt ? savestring(prompt) : (char *) NULL;
    rl_display_prompt = rl_prompt ? rl_prompt : "";
    fprintf(stdout, prompt);
    fflush(stdout);
    //rl_visible_prompt_length = rl_expand_prompt (rl_prompt);
    return 0;
}

/* Read a key, including pending input. */
int
rl_read_key(void)
{
    int c, r;

    if(rl_pending_input)
    {
        c = rl_pending_input; /* XXX - cast to unsigned char if > 0? */
        rl_clear_pending_input();
    }
    else
    {
        /* If input is coming from a macro, then use that. */
//        if(c = _rl_next_macro_key())
//            return ((unsigned char) c);
//        if(rl_get_char(&c) == 0)
        c = rl_getc(rl_instream);
        /* fprintf(stderr, "rl_read_key: calling RL_CHECK_SIGNALS: _rl_caught_signal = %d", _rl_caught_signal); */
//        RL_CHECK_SIGNALS();
    }

    return (c);
}

int readline_internal_char(void)
{
    static int lastc, eof_found;
    int c, code, lk, r;

    lastc = EOF;

#if !defined (READLINE_CALLBACKS)
    eof_found = 0;
    while(rl_done == 0)
    {
#endif
        lk = _rl_last_command_was_kill;

#if defined (HAVE_POSIX_SIGSETJMP)
        code = sigsetjmp (_rl_top_level, 0);
#else
        code = setjmp(_rl_top_level);
#endif

        if(code)
        {
            //(*rl_redisplay_function) ();
            //_rl_want_redisplay = 0;

            /* If we get here, we're not being called from something dispatched
             from _rl_callback_read_char(), which sets up its own value of
             _rl_top_level (saving and restoring the old, of course), so
             we can just return here. */
//      if (RL_ISSTATE (RL_STATE_CALLBACK))
//        return (0);
        }

        if(rl_pending_input == 0)
                {
            /* Then initialize the argument and number of keys read. */
            //_rl_reset_argument();
            //rl_executing_keyseq[rl_key_sequence_length = 0] = '\0';
        }

        RL_SETSTATE(RL_STATE_READCMD);
        c = rl_read_key();
        RL_UNSETSTATE(RL_STATE_READCMD);

        /* look at input.c:rl_getc() for the circumstances under which this will
         be returned; punt immediately on read error without converting it to
         a newline; assume that rl_read_key has already called the signal
         handler. */
        if(c == READERR)
        {
#if defined (READLINE_CALLBACKS)
            RL_SETSTATE(RL_STATE_DONE);
            return (rl_done = 1);
#else
            eof_found = 1;
            break;
#endif
        }

        /* EOF typed to a non-blank line is ^D the first time, EOF the second
         time in a row.  This won't return any partial line read from the tty.
         If we want to change this, to force any existing line to be returned
         when read(2) reads EOF, for example, this is the place to change. */
        if(c == EOF && rl_end)
                {
//            if(RL_SIG_RECEIVED())
//            {
//                RL_CHECK_SIGNALS();
//                if(rl_signal_event_hook)
//                    (*rl_signal_event_hook)(); /* XXX */
//            }

            /* XXX - reading two consecutive EOFs returns EOF */
            if(RL_ISSTATE(RL_STATE_TERMPREPPED))
                    {
                if(lastc == _rl_eof_char || lastc == EOF)
                    rl_end = 0;
                else
                    c = _rl_eof_char;
            }
            else
                c = NEWLINE;
        }

        /* The character _rl_eof_char typed to blank line, and not as the
         previous character is interpreted as EOF.  This doesn't work when
         READLINE_CALLBACKS is defined, so hitting a series of ^Ds will
         erase all the chars on the line and then return EOF. */
        if(((c == _rl_eof_char && lastc != c) || c == EOF) && rl_end == 0)
                {
#if defined (READLINE_CALLBACKS)
            RL_SETSTATE(RL_STATE_DONE);
            return (rl_done = 1);
#else
            eof_found = 1;
            break;
#endif
        }

        lastc = c;
        //r = _rl_dispatch((unsigned char) c, _rl_keymap);
//        RL_CHECK_SIGNALS();

        /* If there was no change in _rl_last_command_was_kill, then no kill
         has taken place.  Note that if input is pending we are reading
         a prefix command, so nothing has changed yet. */
        if(rl_pending_input == 0 && lk == _rl_last_command_was_kill)
            _rl_last_command_was_kill = 0;

//        _rl_internal_char_cleanup();

#if defined (READLINE_CALLBACKS)
        return 0;
#else
    }

    return (eof_found);
#endif
}

/**
 *  Read a line of input.  Prompt with PROMPT.  An empty PROMPT means none.
 *  A return value of NULL means that EOF was encountered.
 */
char *rl_readline(const char *prompt)
{
    char *value;

    /* If we are at EOF return a NULL string. */
    if(rl_pending_input == EOF)
    {
        rl_clear_pending_input();
        return ((char *) NULL);
    }

    rl_set_prompt(prompt);

//    rl_initialize();
//    if(rl_prep_term_function)
//        (*rl_prep_term_function)(_rl_meta_flag);

    /* Read a line of input from the global rl_instream, doing output on
     the global rl_outstream.
     If rl_prompt is non-null, then that is our prompt. */
    {
//        readline_internal_setup();
        int eof = 1;

        while(rl_done == 0)
            eof = readline_internal_char();
        value = (char *)(intptr_t) eof; //readline_internal_teardown(eof);
    }
//    if(rl_deprep_term_function)
//        (*rl_deprep_term_function)();

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

/* Query the right environment variables and call setlocale() to initialize
 the C library locale settings. */
char* _rl_init_locale(void)
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

/* Initialize readline (and terminal if not already). */
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
//      readline_initialize_everything ();
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
