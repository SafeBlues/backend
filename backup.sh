set -e
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
BACKUP_PASSWORD="pwd for step 3"
name=backup-$(date +%s)
mkdir -p /home/ubuntu/backup/$name
pushd /home/ubuntu/backup/$name
docker exec -i sb-aws_postgres_1 pg_dump -U postgres > backup.sql
zstd -17 backup.sql
cloaker --password $BACKUP_PASSWORD --encrypt backup.sql.zst
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
 aws s3 cp /home/ubuntu/backup/$name/backup.sql.zst.cloaker s3://sb-encrypted-backups/ads/$name.sql.zst.cloaker
echo Backed up to s3://sb-encrypted-backups/ads/$name.sql.zst.cloaker
popd
rm -rf /home/ubuntu/backup/$name
