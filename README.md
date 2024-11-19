![Screenshot from 2024-11-20 01-45-29](https://github.com/user-attachments/assets/3b666932-3830-4b22-a2a0-9ddfa2ded2dc)

# Introduction
  
  This is telegram bot to send files in desktop server and store in working directory ...
  
  Features :
  1. See files of desktop using ls button.
  2. Download files from desktop using download button.
  3. Run basic command in desktop from telegram bot using, send to bot like /cmd __cmd__ & enter.
  4. See content of file using cat button.

# Installation
 - In Ubuntu / Kali linux :
 - Tested in Ubuntu.
 - Perfectly working.
 - Steps to install :
   
    ```
     git clone https://github.com/Kcyb3r/AmazeBOT.git 

     cd AmazeBOT
  
     pip3 install -r requirements.txt --break-system-packages
    ```

    - Then, add your telegram user ID and bot token in terminal_bot.py.
       - find your telegram user ID from telegram's bot @userinfobot.
       - send ' /start ' to @userinfobot and get your telegram user ID then, paste in python file.
       - create a telegram bot from telegram's bot @BotFather.
       - send ' /newbot ' to @BotFather, then send your telegram name that you want.
       - copy the HTTP API Token and paste in our terminal_bot.py in require place in code.
       - also note the link of your telegram bot.

    - Now, edit USERNAME AND DIRECTORY PATH in terminal-bot.service.
       - edit only there , where is written #IMP.
     
    -Then, paste below cmd in terminal :
   ```
    sudo systemctl start terminal-bot.service
    sudo systemctl status terminal-bot.service
   ```
   - Then, open the created telegram bot.
   - send ' /start ' cmd to start the bot.
   - send ' /help ' cmd for help.



     - Made by Kcyb3r ...
