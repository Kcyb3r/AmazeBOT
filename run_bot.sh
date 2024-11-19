#!/bin/bash

# Function to check if process is running
is_running() {
    if [ -f bot.pid ]; then
        pid=$(cat bot.pid)
        if ps -p $pid > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Kill existing instance if running
if is_running; then
    echo "Stopping existing bot instance..."
    pid=$(cat bot.pid)
    kill $pid
    sleep 2
fi

# Clean up old PID file
rm -f bot.pid

# Start the bot
echo "Starting bot..."
python3 terminal_bot.py &

# Wait for PID file to be created
sleep 2

if is_running; then
    echo "Bot started successfully"
else
    echo "Failed to start bot"
fi 