#ifdef __APPLE__


#import <Foundation/Foundation.h>

#include "Foundation/NSString.h"
#include "Foundation/NSAppleScript.h"
#

int callSec (char *tool, char* args[]) {
    NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];
	
    // Create authorization reference
    AuthorizationRef authorizationRef;
    OSStatus status;
	
    status = AuthorizationCreate(NULL, kAuthorizationEmptyEnvironment, kAuthorizationFlagDefaults, &authorizationRef);
	
    // Run the tool using the authorization reference
    FILE *pipe = NULL;
	
    status = AuthorizationExecuteWithPrivileges(authorizationRef, tool, kAuthorizationFlagDefaults, args, &pipe);
	
    if (status == errAuthorizationSuccess) {
        return 0; 
    } else {
        NSLog(@"Authorization Result Code: %d", status);
    }
	
    [pool drain];
    return -1;
}


int callSecScript(char *script)
{
    NSDictionary *error = [NSDictionary new];
    NSString *appleScriptString = @"do shell script ";
    appleScriptString = [appleScriptString stringByAppendingString:@"\""];
    appleScriptString = [appleScriptString stringByAppendingString:[NSString stringWithUTF8String: script]];
    appleScriptString = [appleScriptString stringByAppendingString:@"\""];
    appleScriptString = [appleScriptString stringByAppendingString:@" with administrator privileges"];
    NSAppleScript *appleScript = [[NSAppleScript alloc] initWithSource:appleScriptString];
    NSString *result;
    result = [[appleScript executeAndReturnError: &error] stringValue];
    return 0;
}

#endif