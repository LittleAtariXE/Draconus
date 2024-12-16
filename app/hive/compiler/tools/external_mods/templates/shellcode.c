#include <stdio.h>
#include <string.h>
 
/*
by github.com/LittleAtariXE

compile:
gcc -fno-stack-protector -z execstack -m32 -o {{PATTERN_file_name}} {{PATTERN_file_name}}.c
 
shellcode:
 
{{SHELL_CODE}}
 
*/
 
 
int main(){
const char shell[] =
"{{SHELL_CODE}}";
printf("by: github.com/LittleAtariXE\n\nstrlen(shell)= %d\n", strlen(shell));
(*(void (*)()) shell)();
}