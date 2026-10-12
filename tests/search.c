#include <assert.h>
#include "../src/search.h"
int main(void){const char *fields[]={"video-editor","GTK video editor","https://example/community","editor-src","GPL-3.0"};int error;Expr *e=expr_parse("editor|video+gtk",&error);assert(!error&&expr_match(e,fields));expr_free(e);e=expr_parse("(editor|audio)+qt",&error);assert(!error&&!expr_match(e,fields));expr_free(e);e=expr_parse("repo:community+license:GPL",&error);assert(!error&&expr_match(e,fields));expr_free(e);e=expr_parse("editor+",&error);assert(error&&!e);e=expr_parse("\"g++\"",&error);assert(!error);expr_free(e);return 0;}
