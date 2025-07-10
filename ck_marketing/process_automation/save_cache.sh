TS=$(timestamp)
echo $TS
cp ck_marketing/process_automation/cache.verify_email.json ~/src/backup/cache.verify_email.$TS.json
cp ck_marketing/process_automation/cache.find_email.json ~/src/backup/cache.find_email.$TS.json
cp ck_marketing/process_automation/cache.enrich.json ~/src/backup/cache.enrich.$TS.json
ls -lh ~/src/backup
chmod -w ~/src/backup/*
