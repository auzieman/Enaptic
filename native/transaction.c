/* Enaptic native solver bridge. GPL-2.0-only (links APK's GPL-2.0-only ABI).
 * API headers and library: apk-tools 3.0.8, upstream notices retained in build.
 * The GUI never runs this bridge privileged directly; the installed helper
 * validates requests and gives it a bounded protocol through stdin.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <signal.h>
#include "apk_database.h"
#include "apk_solver.h"
#include "apk_version.h"
#include "apk_print.h"
#include "apk_io.h"
static char *read_block(void){unsigned n;if(scanf("%u\n",&n)!=1||n>1024*1024)return NULL;char *s=calloc(n+1,1);if(!s)return NULL;if(fread(s,1,n,stdin)!=n){free(s);return NULL;}return s;}
static void digest(FILE *f,struct apk_package *p){if(!p){fputs("-",f);return;}fprintf(f,"%u:",p->digest_alg);int n=apk_digest_alg_len(p->digest_alg);for(int i=0;i<n;i++)fprintf(f,"%02x",p->digest[i]);}
static int compare(const void *a,const void *b){return strcmp(*(char *const*)a,*(char *const*)b);}
static char *identity(struct apk_changeset *set){char **lines=calloc(apk_array_len(set->changes)+1,sizeof(char*));unsigned n=0;apk_array_foreach(c,set->changes){if(c->old_pkg==c->new_pkg&&!c->reinstall&&c->old_repository_tag==c->new_repository_tag)continue;struct apk_package *p=c->new_pkg?c->new_pkg:c->old_pkg;char *s=NULL;size_t len=0;FILE *f=open_memstream(&s,&len);fprintf(f,"%s\t",p->name->name);if(c->old_pkg)fprintf(f,BLOB_FMT,BLOB_PRINTF(*c->old_pkg->version));else fputs("—",f);fputc('\t',f);if(c->new_pkg)fprintf(f,BLOB_FMT,BLOB_PRINTF(*c->new_pkg->version));else fputs("—",f);fputc('\t',f);digest(f,c->old_pkg);fputc('\t',f);digest(f,c->new_pkg);fprintf(f,"\t%u\t%u\t%u\n",c->old_repository_tag,c->new_repository_tag,c->reinstall);fclose(f);lines[n++]=s;}qsort(lines,n,sizeof(char*),compare);char *out=NULL;size_t len=0;FILE *f=open_memstream(&out,&len);for(unsigned i=0;i<n;i++){fputs(lines[i],f);free(lines[i]);}fclose(f);free(lines);return out;}
int main(int argc,char **argv){int test=argc==3&&!strcmp(argv[1],"apply-test");int apply=test||(argc==2&&!strcmp(argv[1],"apply"));if(!apply&&(argc!=3||strcmp(argv[1],"plan")))return 2;if(apply&&geteuid()!=0)return 2;
 signal(SIGPIPE,SIG_IGN);umask(022);struct apk_ctx ctx;struct apk_database db;struct apk_dependency_array *world;struct apk_changeset changes={0};int result=1;char *world_text=NULL,*expected=NULL,*actual=NULL;apk_crypto_init();apk_ctx_init(&ctx);ctx.open_flags=(apply?APK_OPENF_WRITE:APK_OPENF_READ)|APK_OPENF_NO_AUTOUPDATE;ctx.lock_wait=10;ctx.interactive=APK_NO;ctx.pretty_print=APK_NO;ctx.out.progress=APK_NO;ctx.out.verbosity=1;
 char cache[4096];if(test){ctx.root=argv[2];ctx.keys_dir="/etc/apk/keys";ctx.flags|=APK_NO_SCRIPTS|APK_NO_COMMIT_HOOKS;}if(!apply){ctx.root=argv[2];ctx.keys_dir="/etc/apk/keys";snprintf(cache,sizeof(cache),"%s/var/cache/apk",argv[2]);ctx.cache_dir=cache;ctx.flags|=APK_NO_SCRIPTS|APK_NO_COMMIT_HOOKS|APK_NO_LOGFILE;}else ctx.cache_predownload=1;
 apk_io_url_init(&ctx.out);apk_io_url_set_timeout(30);apk_db_init(&db,&ctx);apk_dependency_array_init(&world);apk_change_array_init(&changes.changes);
 if(apk_ctx_prepare(&ctx)||apk_db_open(&db))goto done;
 if(apply){puts("LOCKED");fflush(stdout);}unsigned upgrade_all,count;if(scanf("%u\n",&upgrade_all)!=1||upgrade_all>1)goto done;world_text=read_block();if(!world_text)goto done;apk_blob_t blob=APK_BLOB_STR(world_text);if(apk_blob_pull_deps(&blob,&db,&world,true)||APK_BLOB_IS_NULL(blob))goto done;
 if(scanf("%u\n",&count)!=1||count>1000)goto done;for(unsigned i=0;i<count;i++){char name[512];if(!fgets(name,sizeof(name),stdin))goto done;name[strcspn(name,"\n")]=0;struct apk_name *p=apk_db_get_name(&db,APK_BLOB_STR(name));apk_solver_set_name_flags(p,APK_SOLVERF_UPGRADE,APK_SOLVERF_UPGRADE);}
 expected=read_block();if(!expected)goto done;
 if(apk_db_check_world(&db,world)||apk_db_repository_check(&db))goto done;
 if(apk_solver_solve(&db,upgrade_all?APK_SOLVERF_UPGRADE:0,world,&changes)){apk_solver_print_errors(&db,&changes,world);goto done;}
 actual=identity(&changes);
 if(apply){if(strcmp(expected,actual)){fputs("STALE: native transaction differs from the reviewed package identities. Preview again.\n",stderr);goto done;}puts("COMMITTING reviewed transaction");fflush(stdout);result=apk_solver_commit_changeset(&db,&changes,world);}
 else {printf("IDENTITY\n%sEND_IDENTITY\n",actual);uint64_t download=0;int64_t disk=0;apk_array_foreach(c,changes.changes){if(c->old_pkg==c->new_pkg&&!c->reinstall&&c->old_repository_tag==c->new_repository_tag)continue;struct apk_package *p=c->new_pkg?c->new_pkg:c->old_pkg;const char *action=!c->new_pkg?"Purging":!c->old_pkg?"Installing":c->old_pkg==c->new_pkg?"Reinstalling":apk_version_compare(*c->new_pkg->version,*c->old_pkg->version)==APK_VERSION_LESS?"Downgrading":"Upgrading";printf("CHANGE\t%s\t",p->name->name);if(c->old_pkg)printf(BLOB_FMT,BLOB_PRINTF(*c->old_pkg->version));else fputs("—",stdout);fputc('\t',stdout);if(c->new_pkg)printf(BLOB_FMT,BLOB_PRINTF(*c->new_pkg->version));else fputs("—",stdout);printf("\t%s\n",action);if(c->new_pkg){disk+=c->new_pkg->installed_size;if(c->new_pkg!=c->old_pkg&&!c->new_pkg->cached)download+=c->new_pkg->size;}if(c->old_pkg)disk-=c->old_pkg->installed_size;}printf("TOTAL\t%llu\t%lld\n",(unsigned long long)download,(long long)disk);result=0;}
 done:free(world_text);free(expected);free(actual);apk_change_array_free(&changes.changes);apk_dependency_array_free(&world);apk_db_close(&db);apk_ctx_free(&ctx);return result?1:0;
}
