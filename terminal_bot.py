import logging
import os
import subprocess
import signal
import sys
import psutil
import atexit
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import Conflict

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# List of authorized user IDs
AUTHORIZED_USERS = [__ENTER-your-telegram-user-ID___]  # Replace with your actual User ID   {Imp}_____________________1

# Global variable for the PID file
PID_FILE = 'bot.pid'

def is_bot_running():
    """Check if another instance is running."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                old_pid = int(f.read())
            # Check if process with stored PID exists
            if psutil.pid_exists(old_pid):
                return True
        except (ValueError, psutil.NoSuchProcess):
            pass
    return False

def cleanup():
    """Cleanup function to remove PID file."""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            logger.info("Cleaned up PID file")
    except Exception as e:
        logger.error(f"Error cleaning up: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f'Received signal {signum}. Shutting down bot...')
    cleanup()
    sys.exit(0)

def main():
    """Start the bot."""
    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Check if bot is already running
        if is_bot_running():
            logger.error("Bot is already running!")
            sys.exit(1)

        # Write PID file
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))

        # Read token
        with open('token.txt', 'r') as file:
            TOKEN = file.read().strip()

        # Initialize bot with persistence
        application = Application.builder().token('_____ENTER-your-telegram-bot-token____').build()  {Imp}--------------2

        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("cmd", execute_command))
        application.add_handler(CommandHandler("pwd", pwd_command))
        application.add_handler(CommandHandler("ls", ls_command))
        application.add_handler(CommandHandler("cd", cd_command))
        application.add_handler(CommandHandler("back", cd_back))
        application.add_handler(CommandHandler("cat", cat_command))
        application.add_handler(CommandHandler("download", show_files_to_download))
        application.add_handler(CommandHandler("sudopass", handle_sudo_password))
        application.add_handler(CommandHandler("upload", upload_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        
        # Add button handler
        application.add_handler(CallbackQueryHandler(button_handler))

        # Add error handler
        application.add_error_handler(error_handler)

        # Add upload handlers
        application.add_handler(CommandHandler("upload", upload_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        application.add_handler(MessageHandler(
            filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO,
            handle_upload
        ))

        logger.info("Bot started successfully")
        
        # Start the bot with proper error handling
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False  # Prevent automatic closing
        )

    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        cleanup()
        sys.exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized access denied.")
        return
    
    await send_response_with_buttons(
        update.message,
        "🖥️ Welcome to Terminal Bot! 🖥️\n\n"
        "Available Commands:\n"
        "1. 📂 /pwd - Show current directory\n"
        "2. 📑 /ls - List files in directory\n"
        "3. 🔄 /cd <path> - Change directory\n"
        "4. ⬆️ /back - Go to parent directory\n"
        "5. 📄 /cat <filename> - View file contents\n"
        "6. 💻 /cmd <command> - Execute command\n"
        "7. 📥 /download - Download files\n"
        "8. 📤 /upload - Upload files\n\n"
        "You can also use the buttons below for quick access.\n\n"
        "⚠️ Security Note ⚠️\n"
        "- Only authorized users can use this bot\n"
        "- Be careful with system commands\n"
        "- Sudo commands require verification"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized access denied.")
        return
    
    await send_response_with_buttons(
        update.message,
        "🔍 Terminal Bot Help 🔍\n\n"
        "How to use:\n"
        "1. Use /cmd followed by your terminal command\n"
        "   Example: /cmd echo 'Hello World'\n\n"
        "2. Use /pwd to see current directory\n\n"
        "3. Use /ls to list files\n\n"
        "4. Use /cd to change directory\n"
        "   Example: /cd /home\n\n"
        "5. Use /back to go to parent directory\n"
        "   Same as 'cd ..'\n\n"
        "6. Use /cat to view file contents\n"
        "   Example: /cat filename.txt\n\n"
        "7. Use /download to get files\n"
        "8. Use /upload to upload files\n\n"
        "⚠️ Security Warning ⚠️\n"
        "- Only authorized users can use this bot\n"
        "- Be careful with system commands\n"
        "- Avoid destructive commands"
    )

async def send_response_with_buttons(message, text):
    """Send response message with command buttons."""
    await message.reply_text(
        text,
        reply_markup=get_command_buttons()
    )

def get_command_buttons():
    """Create command buttons layout."""
    keyboard = [
        [
            InlineKeyboardButton("📂 PWD", callback_data="cmd_pwd"),
            InlineKeyboardButton("📑 LS", callback_data="cmd_ls"),
            InlineKeyboardButton("⬆️ CD ..", callback_data="cmd_back")
        ],
        [
            InlineKeyboardButton("📄 CAT", callback_data="cmd_cat"),
            InlineKeyboardButton("💻 CMD", callback_data="cmd_cmd"),
            InlineKeyboardButton("📥 Download", callback_data="cmd_download")
        ],
        [
            InlineKeyboardButton("📤 Upload", callback_data="cmd_upload")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    query = update.callback_query
    
    if not query:
        return
    
    if update.effective_user.id not in AUTHORIZED_USERS:
        await query.answer("Unauthorized access denied.")
        return
    
    try:
        if query.data == "cmd_upload":
            # Create upload menu directly
            keyboard = [
                [
                    InlineKeyboardButton("📄 Document", callback_data="up_doc"),
                    InlineKeyboardButton("🖼️ Photo", callback_data="up_photo")
                ],
                [
                    InlineKeyboardButton("🎵 Audio", callback_data="up_audio"),
                    InlineKeyboardButton("🎥 Video", callback_data="up_video")
                ],
                [
                    InlineKeyboardButton("🔙 Back", callback_data="cmd_back")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(
                "📤 Upload File\n\n"
                "Select file type to upload:\n"
                "1. 📄 Document (any file type)\n"
                "2. 🖼️ Photo (images)\n"
                "3. 🎵 Audio (music, voice)\n"
                "4. 🎥 Video (movies, clips)\n\n"
                f"Current directory: {os.getcwd()}",
                reply_markup=reply_markup
            )
            await query.answer("Select file type to upload")
            return
            
        # Handle upload type selection
        if query.data.startswith("up_"):
            file_type = query.data.split('_')[1]
            context.user_data['awaiting_upload'] = file_type
            
            type_messages = {
                'doc': "📄 Send any file as a document",
                'photo': "🖼️ Send a photo",
                'audio': "🎵 Send an audio file",
                'video': "🎥 Send a video"
            }
            
            await query.message.edit_text(
                f"✨ Ready to receive {file_type} upload!\n\n"
                f"{type_messages.get(file_type)}\n\n"
                f"Current directory: {os.getcwd()}\n"
                "Send /cancel to cancel upload.",
                reply_markup=get_command_buttons()
            )
            await query.answer(f"Ready for {file_type} upload")
            return
            
        # Handle download requests
        if query.data.startswith("dl_"):
            filename = query.data[3:]  # Remove "dl_" prefix
            await handle_download(query, filename)
            return
            
        # Handle other commands
        cmd = query.data.split('_')[1]
        
        if cmd == "pwd":
            current_dir = os.getcwd()
            await query.message.edit_text(
                f"📂 Current Directory:\n{current_dir}",
                reply_markup=get_command_buttons()
            )
        
        elif cmd == "ls":
            files = os.listdir()
            response = "📑 Files in current directory:\n\n"
            for file in files:
                if os.path.isdir(file):
                    response += f"📁 {file}/\n"
                else:
                    response += f"📄 {file}\n"
            await query.message.edit_text(
                response,
                reply_markup=get_command_buttons()
            )
        
        elif cmd == "back":
            os.chdir('..')
            current_dir = os.getcwd()
            await query.message.edit_text(
                f"📂 Changed to parent directory:\n{current_dir}",
                reply_markup=get_command_buttons()
            )
        
        elif cmd == "cat":
            await query.message.edit_text(
                "Use /cat <filename> to view file contents\n"
                "Example: /cat readme.txt",
                reply_markup=get_command_buttons()
            )
        
        elif cmd == "cmd":
            await query.message.edit_text(
                "Use /cmd <command> to execute terminal command\n"
                "Example: /cmd echo 'hello world'",
                reply_markup=get_command_buttons()
            )
        
        elif cmd == "download":
            await show_files_to_download(update, context)
        
        elif cmd == "upload":
            await upload_command(update, context)
        
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in button_handler: {str(e)}")
        await query.answer("❌ An error occurred!")
        if query.message:
            await query.message.edit_text(
                f"❌ Error executing command: {str(e)}",
                reply_markup=get_command_buttons()
            )

async def execute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute terminal command."""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized access denied.")
        return
    
    if not context.args:
        await send_response_with_buttons(
            update.message,
            "Please provide a command to execute."
        )
        return
    
    command = ' '.join(context.args)
    
    # Check for sudo command
    if command.startswith('sudo'):
        keyboard = [
            [InlineKeyboardButton("Enter Sudo Password", callback_data="sudo_password")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔐 This command requires sudo privileges.\n"
            "Click below to enter sudo password:",
            reply_markup=reply_markup
        )
        context.user_data['pending_sudo_command'] = command
        return
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        response = "💻 Command Output:\n\n"
        if stdout:
            response += f"📤 Output:\n{stdout}\n"
        if stderr:
            response += f"⚠️ Error:\n{stderr}\n"
        if not stdout and not stderr:
            response += "No output generated."
        
        await send_response_with_buttons(update.message, response)
        
    except Exception as e:
        await send_response_with_buttons(
            update.message,
            f"Error executing command: {str(e)}"
        )

async def pwd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current working directory."""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized access denied.")
        return
    
    try:
        current_dir = os.getcwd()
        await send_response_with_buttons(
            update.message,
            f"📂 Current Directory:\n{current_dir}"
        )
    except Exception as e:
        await send_response_with_buttons(
            update.message,
            f"Error getting current directory: {str(e)}"
        )

async def ls_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List files in current directory."""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized access denied.")
        return
    
    try:
        files = os.listdir()
        response = "📑 Files in current directory:\n\n"
        for file in files:
            if os.path.isdir(file):
                response += f"📁 {file}/\n"
            else:
                response += f"📄 {file}\n"
        await send_response_with_buttons(update.message, response)
    except Exception as e:
        await send_response_with_buttons(
            update.message,
            f"Error listing directory: {str(e)}"
        )

async def cd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change directory."""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized access denied.")
        return
    
    if not context.args:
        await send_response_with_buttons(
            update.message,
            "Please provide a directory path."
        )
        return
    
    try:
        path = ' '.join(context.args)
        os.chdir(path)
        await send_response_with_buttons(
            update.message,
            f"📂 Changed directory to:\n{os.getcwd()}"
        )
    except Exception as e:
        await send_response_with_buttons(
            update.message,
            f"Error changing directory: {str(e)}"
        )

async def cd_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go back to parent directory."""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized access denied.")
        return
    
    try:
        os.chdir('..')
        await send_response_with_buttons(
            update.message,
            f"📂 Changed to parent directory:\n{os.getcwd()}"
        )
    except Exception as e:
        await send_response_with_buttons(
            update.message,
            f"Error changing directory: {str(e)}"
        )

async def cat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display contents of a file."""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized access denied.")
        return
    
    if not context.args:
        await send_response_with_buttons(
            update.message,
            "Please provide a file name to read."
        )
        return
    
    try:
        filename = ' '.join(context.args)
        if not os.path.exists(filename):
            await send_response_with_buttons(
                update.message,
                f"File not found: {filename}"
            )
            return
            
        with open(filename, 'r') as file:
            content = file.read()
            
        if not content:
            await send_response_with_buttons(
                update.message,
                f"File is empty: {filename}"
            )
            return
            
        response = f"📄 Contents of {filename}:\n\n{content}"
        
        # Split long messages
        if len(response) > 4096:
            for i in range(0, len(response), 4096):
                await update.message.reply_text(response[i:i+4096])
            await send_response_with_buttons(
                update.message,
                "File contents displayed above ⬆️"
            )
        else:
            await send_response_with_buttons(update.message, response)
            
    except Exception as e:
        await send_response_with_buttons(
            update.message,
            f"Error reading file: {str(e)}"
        )

async def show_files_to_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show downloadable files in current directory."""
    try:
        # Get the message object (either from callback query or direct message)
        message = update.callback_query.message if update.callback_query else update.message
        
        # List files in current directory
        files = os.listdir()
        keyboard = []
        
        # Create buttons for each file
        for file in files:
            if os.path.isfile(file):
                # Create safe callback data
                safe_filename = file[:30] if len(file) > 30 else file
                keyboard.append([
                    InlineKeyboardButton(
                        f"📄 {file}",
                        callback_data=f"dl_{safe_filename}"
                    )
                ])
        
        # Check if we found any files
        if not keyboard:
            await message.reply_text(
                "📂 No files available for download in current directory.",
                reply_markup=get_command_buttons()
            )
            return
        
        # Add back button
        keyboard.append([
            InlineKeyboardButton("🔙 Back to Menu", callback_data="cmd_back")
        ])
        
        # Create and send the file selection menu
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(
            "📥 Select a file to download:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in show_files_to_download: {str(e)}")
        if update.callback_query:
            await update.callback_query.message.reply_text(
                f"❌ Error listing files: {str(e)}",
                reply_markup=get_command_buttons()
            )
        else:
            await update.message.reply_text(
                f"❌ Error listing files: {str(e)}",
                reply_markup=get_command_buttons()
            )

async def handle_download(query: CallbackQuery, filename: str):
    """Handle file download."""
    try:
        # Find the actual filename (in case it was truncated)
        full_filename = None
        for file in os.listdir():
            if file.startswith(filename):
                full_filename = file
                break
        
        if not full_filename or not os.path.exists(full_filename):
            await query.answer("❌ File not found!")
            await query.message.reply_text(
                "File no longer exists.",
                reply_markup=get_command_buttons()
            )
            return
        
        # Send the file
        with open(full_filename, 'rb') as file:
            await query.message.reply_document(
                document=file,
                filename=full_filename,
                caption=f"📥 Downloaded: {full_filename}"
            )
        
        await query.answer("✅ Download complete!")
        await query.message.reply_text(
            f"✅ File sent successfully: {full_filename}",
            reply_markup=get_command_buttons()
        )
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        await query.answer("❌ Download failed!")
        await query.message.reply_text(
            f"❌ Error downloading file: {str(e)}",
            reply_markup=get_command_buttons()
        )

async def handle_sudo_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sudo password input."""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized access denied.")
        return
    
    # Delete the password message immediately for security
    await update.message.delete()
    
    if not context.args:
        await send_response_with_buttons(
            update.message,
            "Please provide the sudo password."
        )
        return
    
    if 'pending_sudo_command' not in context.user_data:
        await send_response_with_buttons(
            update.message,
            "No sudo command is pending."
        )
        return
    
    try:
        password = context.args[0]
        command = context.user_data['pending_sudo_command']
        
        # Execute sudo command with password
        process = subprocess.Popen(
            ['sudo', '-S'] + command[5:].split(),  # Remove 'sudo ' prefix
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=f"{password}\n")
        
        response = "🔐 Sudo Command Output:\n\n"
        if stdout:
            response += f"📤 Output:\n{stdout}\n"
        if stderr and 'password for' not in stderr.lower():
            response += f"⚠️ Error:\n{stderr}\n"
        if not stdout and not stderr:
            response += "No output generated."
        
        await send_response_with_buttons(update.message, response)
        
    except Exception as e:
        await send_response_with_buttons(
            update.message,
            f"Error executing sudo command: {str(e)}"
        )
    finally:
        # Clear the stored command for security
        context.user_data.pop('pending_sudo_command', None)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "An error occurred while processing your request.\n"
                "Please try again later."
            )
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")

async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file upload command."""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized access denied.")
        return
    
    keyboard = [
        [
            InlineKeyboardButton("📄 Document", callback_data="up_doc"),
            InlineKeyboardButton("🖼️ Photo", callback_data="up_photo")
        ],
        [
            InlineKeyboardButton("🎵 Audio", callback_data="up_audio"),
            InlineKeyboardButton("🎥 Video", callback_data="up_video")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="cmd_back")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📤 Upload File\n\n"
        "Select file type to upload:\n"
        "1. 📄 Document (any file type)\n"
        "2. 🖼️ Photo (images)\n"
        "3. 🎵 Audio (music, voice)\n"
        "4. 🎥 Video (movies, clips)\n\n"
        f"Current directory: {os.getcwd()}",
        reply_markup=reply_markup
    )

async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming files for upload."""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized access denied.")
        return
    
    if 'awaiting_upload' not in context.user_data:
        return
    
    try:
        expected_type = context.user_data['awaiting_upload']
        file_obj = None
        file_name = None
        
        # Check file type matches expected type
        if expected_type == 'doc' and update.message.document:
            file_obj = update.message.document
            file_name = file_obj.file_name
        elif expected_type == 'photo' and update.message.photo:
            file_obj = update.message.photo[-1]
            file_name = f"photo_{file_obj.file_unique_id}.jpg"
        elif expected_type == 'audio' and update.message.audio:
            file_obj = update.message.audio
            file_name = file_obj.file_name or f"audio_{file_obj.file_unique_id}.mp3"
        elif expected_type == 'video' and update.message.video:
            file_obj = update.message.video
            file_name = file_obj.file_name or f"video_{file_obj.file_unique_id}.mp4"
        else:
            await update.message.reply_text(
                f"❌ Please send a {expected_type} file.",
                reply_markup=get_command_buttons()
            )
            return
        
        # Download file
        file_path = os.path.join(os.getcwd(), file_name)
        new_file = await context.bot.get_file(file_obj.file_id)
        await new_file.download_to_drive(file_path)
        
        # Clear upload state
        del context.user_data['awaiting_upload']
        
        await send_response_with_buttons(
            update.message,
            f"✅ File uploaded successfully!\n\n"
            f"📁 Path: {file_path}\n"
            f"📄 Name: {file_name}\n"
            f"📦 Size: {os.path.getsize(file_path) / 1024:.1f} KB"
        )
        
    except Exception as e:
        await send_response_with_buttons(
            update.message,
            f"❌ Error uploading file: {str(e)}"
        )
        context.user_data.pop('awaiting_upload', None)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel ongoing upload."""
    if 'awaiting_upload' in context.user_data:
        del context.user_data['awaiting_upload']
        await send_response_with_buttons(
            update.message,
            "❌ Upload cancelled."
        )

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        cleanup()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        cleanup() 
