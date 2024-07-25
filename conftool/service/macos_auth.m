#ifdef __APPLE__


#import <Foundation/Foundation.h>


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

#endif