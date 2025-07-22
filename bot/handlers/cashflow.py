
import re
import logging
from bson import ObjectId
from decimal import Decimal
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from bot.handlers.base import BaseHandler

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from bot.services.database import AsyncSessionLocal
from bot.services.llm_model import LLMModel
from bot.services.cache import CacheMessage
from bot.models.user_model import User
from bot.models.cashflow_model import Cashflow
from bot.models.wallet_model import Wallet
from bot.helpers.output_messages import render_wallet_summary, render_grouped_table
from bot.helpers.text_util import parse_json
from bot.helpers.date_util import string_to_datetime

logger = logging.getLogger(__name__)


class CashflowHandler(BaseHandler):
    def __init__(self, llm_model: LLMModel, cache: CacheMessage):
        self.llm_model = llm_model
        self.cache = cache

    async def input_cashflow_by_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict = None):
        telegram_user = update.effective_user
        message = update.message.text

        context.user_data['data'] = data

        chat = self.llm_model.create_parse_chat_model()

        response = chat.send_message(message)
        response = parse_json(response.text)

        self.cache.save_message(telegram_user.id, message, 'user')
        self.cache.save_message(telegram_user.id, response, 'model')

        await update.message.reply_text(render_grouped_table(response), parse_mode='Markdown')

        keyboard = [
                [
                    InlineKeyboardButton('✅ Ya', callback_data='cashflow_yes'),
                    InlineKeyboardButton('❌ Tidak', callback_data='cashflow_no'),
                ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Apakah data transaksi ini benar?', reply_markup=reply_markup)

    async def handle_confirmation_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        data = context.user_data.get('data')
        telegram_user = update.effective_user

        cache = self.cache.get_context(telegram_user.id)

        if not cache or 'messages' not in cache:
            await query.edit_message_text('❌ Error, tolong ulangi promt')
            return
        
        cashflows = [message for message in cache['messages'] if message['role'] == 'model']

        if cashflows is None:
            await query.edit_message_text('❌ Error, tolong ulangi promt')
            return
        
        cashflows = cashflows[0]

        wallet_use, wallet_id = cashflows['text'][0]['wallet'], None

        for row in data['user']['wallets']:
            if wallet_use.lower() == row['name'].lower():
                wallet_id = row['id']
                break

        try:
            if query.data == 'cashflow_yes':
                total_amount = Decimal('0.00')

                async with AsyncSessionLocal() as session:
                    async with session.begin():
                        for row in cashflows['text']:

                            row_total = Decimal(row['price']) * Decimal(row['quantity'])
                            
                            cashflow = Cashflow(
                                id=str(ObjectId()),
                                userId=data['user']['id'],
                                walletId=wallet_id,
                                transactionDate=string_to_datetime(row['date']),
                                activityName=row['activityName'],
                                description='',
                                categoryId=1,
                                quantity=row['quantity'],
                                unit=row['unit'],
                                flowType=row['flowType'],
                                price=row['price'],
                                total=row_total,
                            )

                            session.add(cashflow)

                            if row['flowType'] == 'income':
                                total_amount -= row_total
                            if row['flowType'] == 'expense':
                                total_amount += row_total

                        result = await session.execute(select(Wallet).where(Wallet.id == wallet_id))
                        wallet = result.scalar_one_or_none()
                        if wallet:
                            wallet.balance = wallet.balance + total_amount
                            await session.flush()  # flush ke DB
                    await session.commit()

                await query.edit_message_text('✅ Data telah disimpan')
            elif query.data == 'cashflow_no':
                await query.edit_message_text('🚫 Data dibatalkan. Silakan prompt ulang')
            
        except Exception as e:
            logger.error(f'Error handling confirmation: {e}')
            await query.edit_message_text('❌ Terjadi kesalahan saat memproses konfirmasi.')

        finally:
            self.cache.clear_user_data(telegram_user.id)
