## Утилита fd (быстрее, чем find)
https://github.com/sharkdp/fd

## Прогрев SFS/NFS

```bash
date; \
base_path="/sfs/gvXX-sfs-turbo01/storage/data/git/gitea-repositories"; \
time for i in {{0..9},{a..z}}; \
 	do echo "$i: "; \
	time fd -p -t f '^(.*\.d/gitea)|(proc-receive)$' $base_path/$i*/*.git/hooks 2>/dev/null -x cat {} > /dev/null 2>/dev/null || true; \
done;
```

## Копирование файлов (замена хуков с gitea на gitverse)

```bash
date; \
hook_name="post-receive.d/gitea"; \
base_path="/sfs/gvXX-sfs-turbo01/storage/data/git/backend-repositories"; \
time for i in {{0..9},{a..z}}; do \
	echo -n "$i: "; users_count=$(ls -ld $base_path/$i*/ 2>/dev/null | wc -l); \
	if [[ $users_count -ne "0" ]]; \
		then fd -p -t f $hook_name $base_path/$i*/*.git/hooks 2>/dev/null -x cp /sfs/hooks/$hook_name {}; \
	fi; \
done
```

```bash
date; \
hook_name="pre-receive.d/gitea"; \
base_path="/sfs/gvXX-sfs-turbo01/storage/data/git/backend-repositories"; \
time for i in {{0..9},{a..z}}; do \
	echo -n "$i: "; users_count=$(ls -ld $base_path/$i*/ 2>/dev/null | wc -l); \
	if [[ $users_count -ne "0" ]]; \
		then fd -p -t f $hook_name $base_path/$i*/*.git/hooks 2>/dev/null -x cp /sfs/hooks/$hook_name {}; \
	fi; \
done
```

```bash
date; \
hook_name="update.d/gitea"; \
base_path="/sfs/gvXX-sfs-turbo01/storage/data/git/backend-repositories"; \
time for i in {{0..9},{a..z}}; do \
	echo -n "$i: "; users_count=$(ls -ld $base_path/$i*/ 2>/dev/null | wc -l); \
	if [[ $users_count -ne "0" ]]; \
		then fd -p -t f $hook_name $base_path/$i*/*.git/hooks 2>/dev/null -x cp /sfs/hooks/$hook_name {}; \
	fi; \
done
```

```bash
date; \
hook_name="proc-receive"; \
base_path="/sfs/gvXX-sfs-turbo01/storage/data/git/backend-repositories"; \
time for i in {{0..9},{a..z}}; do \
	echo -n "$i: "; users_count=$(ls -ld $base_path/$i*/ 2>/dev/null | wc -l); \
	if [[ $users_count -ne "0" ]]; \
		then fd -p -t f $hook_name $base_path/$i*/*.git/hooks 2>/dev/null -x cp /sfs/hooks/$hook_name {}; \
	fi; \
done
```

