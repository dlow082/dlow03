from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
from deep_translator import GoogleTranslator
import logging
from langdetect import detect, DetectorFactory, LangDetectException

# لضمان اتساق نتائج الكشف عن اللغة
DetectorFactory.seed = 0

# إعداد تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '7324790103:AAGBOPDWAF7HsPajKU3LDqBr-6uBMlMZcsw'
CHANNEL_USERNAME = 'Red_LA'  # اسم القناة بدون @
DEVELOPER_USERNAME = 'dlow0'

# قاعدة بيانات لتخزين محاولات المستخدمين
user_attempts = {}

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("المطور", callback_data='show_developer_info')],
        [InlineKeyboardButton("القناة", url='https://t.me/Red_LA')],
        [InlineKeyboardButton("بدأ الترجمة", callback_data='start_translation')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo='https://i.imgur.com/vZJGpUH.jpeg',  # الصورة الجديدة
        caption='مرحبًا! اختر إحدى الخيارات أدناه:',
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    data = query.data

    if data == 'show_developer_info':
        keyboard = [
            [InlineKeyboardButton("أطلق من يدخل ⚡ اضغط هنا علشان تراسلني", url=f'https://t.me/{DEVELOPER_USERNAME}')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo='https://i.imgur.com/5zOB7Uq.jpeg',  # الصورة الجديدة
            caption='للتواصل مع المطور، يمكنك الضغط على الزر أدناه.',
            reply_markup=reply_markup
        )
    elif data == 'start_translation':
        await update.effective_chat.send_message('حسنًا، الآن أرسل النص الذي تريد ترجمته ⚡')

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id not in user_attempts or user_attempts[user_id] <= 0:
        user_attempts[user_id] = 300
        await update.message.reply_text(f'تم تجديد محاولاتك! لديك الآن {user_attempts[user_id]} محاولة.')
        return

    user_attempts[user_id] -= 1

    text = update.message.text

    try:
        # محاولة كشف اللغة
        lang = detect(text)
        
        # تحقق من أن اللغة هي العربية أو الإنجليزية
        if lang not in ['ar', 'en']:
            await update.message.reply_text('الرجاء إرسال نص باللغة العربية أو الإنجليزية.')
            return

        if lang == 'ar':
            translated_text = GoogleTranslator(source='ar', target='en').translate(text)
        elif lang == 'en':
            translated_text = GoogleTranslator(source='en', target='ar').translate(text)
        
        await update.message.reply_text(f'الترجمة: {translated_text}')
    except LangDetectException:
        await update.message.reply_text('تعذر الكشف عن اللغة. يرجى إرسال نص باللغة العربية أو الإنجليزية.')
    except Exception as e:
        await update.message.reply_text(f'حدث خطأ أثناء الترجمة: {e}')

async def handle_subscribe(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            if user_id not in user_attempts:
                user_attempts[user_id] = 100
                await update.message.reply_text(f'تم اشتراكك بنجاح! لديك {user_attempts[user_id]} محاولة.')
            else:
                user_attempts[user_id] += 70
                await update.message.reply_text(f'تم اشتراكك بنجاح مسبقًا! لديك الآن {user_attempts[user_id]} محاولة.')
        else:
            await update.message.reply_text('يرجى الاشتراك في قناة المطور أولاً.')
    except Exception as e:
        await update.message.reply_text(f'حدث خطأ أثناء التحقق من الاشتراك: {e}')

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('اشترك'), handle_subscribe))
    
    application.run_polling()

if __name__ == '__main__':
    main()