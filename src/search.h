#ifndef ENAPTIC_SEARCH_H
#define ENAPTIC_SEARCH_H
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
typedef struct Expr { char op; char *text; struct Expr *left,*right; } Expr;
static const char *query_cursor;static int query_error,query_depth;
static void expr_free(Expr *e){if(!e)return;expr_free(e->left);expr_free(e->right);free(e->text);free(e);}
static Expr *expr_or(void);
static void spaces(void){while(isspace((unsigned char)*query_cursor))query_cursor++;}
static Expr *node(char op,Expr *a,Expr *b){Expr *e=calloc(1,sizeof(*e));if(!e){query_error=1;expr_free(a);expr_free(b);return NULL;}e->op=op;e->left=a;e->right=b;return e;}
static Expr *expr_term(void){spaces();if(++query_depth>32){query_error=1;query_depth--;return NULL;}Expr *e=NULL;
 if(*query_cursor=='('){query_cursor++;e=expr_or();spaces();if(*query_cursor!=')')query_error=1;else query_cursor++;}
 else {char token[513];size_t n=0;char quote=0;
  while(*query_cursor){char c=*query_cursor;if(!quote&&(c=='|'||c=='+'||c=='('||c==')'))break;query_cursor++;
   if(c=='"'||c=='\''){if(!quote){quote=c;continue;}if(c==quote){quote=0;continue;}}
   if(n>=512){query_error=1;break;}token[n++]=c;}
  while(n&&isspace((unsigned char)token[n-1]))n--;token[n]=0;
  if(!n||quote)query_error=1;else{e=node('t',NULL,NULL);if(e)e->text=strdup(token);}}
 query_depth--;return e;}
static Expr *expr_and(void){Expr *e=expr_term();spaces();while(*query_cursor=='+'){query_cursor++;e=node('+',e,expr_term());spaces();}return e;}
static Expr *expr_or(void){Expr *e=expr_and();spaces();while(*query_cursor=='|'){query_cursor++;e=node('|',e,expr_and());spaces();}return e;}
static Expr *expr_parse(const char *s,int *error){query_cursor=s;query_error=query_depth=0;spaces();if(!*query_cursor){*error=0;return NULL;}Expr *e=expr_or();spaces();if(*query_cursor)query_error=1;*error=query_error;if(*error){expr_free(e);return NULL;}return e;}
static int contains(const char *text,const char *needle){if(!text)return 0;size_t n=strlen(needle);for(;*text;text++)if(!strncasecmp(text,needle,n))return 1;return !n;}
static int expr_match(Expr *e,const char **fields){if(!e)return 1;if(e->op=='+')return expr_match(e->left,fields)&&expr_match(e->right,fields);if(e->op=='|')return expr_match(e->left,fields)||expr_match(e->right,fields);
 const char *names[]={"name:","description:","repo:","source:","license:"};for(int i=0;i<5;i++)if(!strncasecmp(e->text,names[i],strlen(names[i])))return contains(fields[i],e->text+strlen(names[i]));for(int i=0;i<5;i++)if(contains(fields[i],e->text))return 1;return 0;}
#endif
