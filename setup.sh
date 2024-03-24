#! /bin/sh
echo "start to setup epaper script on rasberry pi"
echo "- input APP_ID on https://www.weatherapi.com/"
echo -n "input APP_ID: "
read API_KEY
if [ -z $API_KEY ]; then
    echo "  APP_ID is empty."
    echo "  weather info will be not displayed."
fi

BASE_PATH=`pwd`
MAIN_SCRIPT=$BASE_PATH/main.py
CRON_PATH=$BASE_PATH/cron.d/epaper-countdown-calendar
TARGET_PATH=/etc/cron.d/epaper-countdown-calendar
echo ""
echo "- setup cron.d"
echo "  you need to enter your password"
cat $CRON_PATH.sample | \
    sed -e "s%__APP_ID__%$API_KEY%" | \
    sed -e "s%__PATH_TO_MAIN__%$MAIN_SCRIPT%" > $CRON_PATH

if [ -f $TARGET_PATH ]; then
    echo "  cron file is already existed."
    echo "  move file to /tmp"
    sudo cp $TARGET_PATH /tmp/.
fi
sudo mv $CRON_PATH $TARGET_PATH
sudo chmod 600 $TARGET_PATH
sudo chown root $TARGET_PATH
echo "-- setup may finished propaly -- "
