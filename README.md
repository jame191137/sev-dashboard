## BUILD IMAGE
```bash
docker build -t auto_backup_db .
```
## START SERVICE (DEV)
```bash
docker-compose up -d
```
## START SERVICE (PRODUCTION)
```bash
docker-compose -f pro.yml up -d
```
## CRONTAB
เริ่มแก้ไข crontab
```bash
sudo crontab -e
```
แก้ไข crontab ตามนี้โดยเวลาเป็นเวลาบน Server(UTC) เป็นเวลาไทยคือเที่ยงคืน และ เที่ยงคืนหนึ่งนาที
และทุกวันที่ 15 ของเดือนจะ Clear Cash บน Server ทิ้ง
```bash
0 17 * * * curl http://localhost:7777/backup
10 17 * * * curl http://localhost:7777/backup_mongo
0 15 15 * * curl http://localhost:7777/remove/korkla
```
restart crontab
```bash
sudo /etc/init.d/cron restart
```
