mv .env .env_backup
mv .env_experiment .env
nohup python3 -u init_game.py > ./io/board_log/nohup.$(date "+%Y%m%d%H%M%S").out &
