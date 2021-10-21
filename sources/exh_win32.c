#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <conio.h>

#include "dap_common.h"

LONG ExceptionFilter( EXCEPTION_POINTERS *ep );

void  S_SetExceptionFilter( void )
{
  SetErrorMode( SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX );

  #ifdef WIN64
    AddVectoredExceptionHandler( 1, ExceptionFilter );
  #else
    SetUnhandledExceptionFilter( (LPTOP_LEVEL_EXCEPTION_FILTER) ExceptionFilter );
  #endif

  return;
}

#if 0
typedef struct _EXCEPTION_RECORD {
  DWORD                    ExceptionCode;
  DWORD                    ExceptionFlags;
  struct _EXCEPTION_RECORD *ExceptionRecord;
  PVOID                    ExceptionAddress;
  DWORD                    NumberParameters;
  ULONG_PTR                ExceptionInformation[EXCEPTION_MAXIMUM_PARAMETERS];
} EXCEPTION_RECORD;
#endif

LONG ExceptionFilter( EXCEPTION_POINTERS *ep )
{
//  printf( "\r\nExceptionCode = 0x%0X[%s]\r\n", ep->ExceptionRecord->ExceptionCode, buff );

  uint8_t buff[128];

  if ( ep->ExceptionRecord->ExceptionCode == EXCEPTION_ACCESS_VIOLATION)
    memcpy( buff, "EXCEPTION_ACCESS_VIOLATION", 27  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_ARRAY_BOUNDS_EXCEEDED)
    memcpy( buff, "EXCEPTION_ARRAY_BOUNDS_EXCEEDED", 32  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_BREAKPOINT)
    memcpy( buff, "EXCEPTION_BREAKPOINT", 21  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_DATATYPE_MISALIGNMENT)
    memcpy( buff, "EXCEPTION_DATATYPE_MISALIGNMENT", 32  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_FLT_DENORMAL_OPERAND)
    memcpy( buff, "EXCEPTION_FLT_DENORMAL_OPERAND", 31 );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_FLT_DIVIDE_BY_ZERO)
    memcpy( buff, "EXCEPTION_FLT_DIVIDE_BY_ZERO", 29  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_FLT_INEXACT_RESULT)
    memcpy( buff, "EXCEPTION_FLT_INEXACT_RESULT", 29  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_FLT_INVALID_OPERATION)
    memcpy( buff, "EXCEPTION_FLT_INVALID_OPERATION", 32  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_FLT_OVERFLOW)
    memcpy( buff, "EXCEPTION_FLT_OVERFLOW", 23  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_FLT_STACK_CHECK)
    memcpy( buff, "EXCEPTION_FLT_STACK_CHECK", 26  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_FLT_UNDERFLOW)
    memcpy( buff, "EXCEPTION_FLT_UNDERFLOW", 24  );
  else if (ep->ExceptionRecord->ExceptionCode == STATUS_ILLEGAL_INSTRUCTION)
    memcpy( buff, "EXCEPTION_ILLEGAL_INSTRUCTION", 30  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_IN_PAGE_ERROR)
    memcpy( buff, "EXCEPTION_IN_PAGE_ERROR", 24  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_INT_DIVIDE_BY_ZERO)
    memcpy( buff, "EXCEPTION_INT_DIVIDE_BY_ZERO", 29  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_INT_OVERFLOW)
    memcpy( buff, "EXCEPTION_INT_OVERFLOW", 23  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_INVALID_DISPOSITION)
    memcpy( buff, "EXCEPTION_INVALID_DISPOSITION", 30  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_NONCONTINUABLE_EXCEPTION)
    memcpy( buff, "EXCEPTION_NONCONTINUABLE_EXCEPTION", 35  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_PRIV_INSTRUCTION)
    memcpy( buff, "EXCEPTION_PRIV_INSTRUCTION", 27  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_SINGLE_STEP)
    memcpy( buff, "EXCEPTION_SINGLE_STEP", 22  );
  else if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_STACK_OVERFLOW)
    memcpy( buff, "EXCEPTION_STACK_OVERFLOW", 25  );
  else
    memcpy( buff, "EXCEPTION_UNKNOWN", 18  );

  HANDLE hConOut = GetStdHandle( STD_OUTPUT_HANDLE );
  SetConsoleTextAttribute( hConOut, 12 );

  printf( "\r\nExceptionCode = 0x%0lX[%s]\r\n", ep->ExceptionRecord->ExceptionCode, buff );

  SetConsoleTextAttribute( hConOut, 7 );

  dap_common_deinit( ); // close log file

  Beep( 1000, 200 );
  Sleep( 1000 );
  getch( );

  ExitProcess( -1 );
  return 0;
}
