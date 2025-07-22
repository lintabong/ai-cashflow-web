
import logging
from bson import ObjectId
from decimal import Decimal
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.handlers.base import BaseHandler

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from bot.services.database import AsyncSessionLocal
from bot.services.llm_model import LLMModel
from bot.models.user_model import User
from bot.models.wallet_model import Wallet
from bot.helpers.output_messages import render_wallet_summary

logger = logging.getLogger(__name__)


class WalletHandler(BaseHandler):
    def __init__(self, llm_model: LLMModel):
        self.llm_model = llm_model
        self.WALLET_NAME, self.WALLET_BALANCE = range(2)

    async def wallet_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE, response):
        await update.message.reply_text(render_wallet_summary(response['user']['wallets']), parse_mode='Markdown')

    async def start_add_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start wallet addition conversation."""
        user = update.effective_user
        await update.message.reply_text(f'Halo {user.username} masukkan nama wallet:')
        return self.WALLET_NAME
    
    async def get_wallet_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get wallet name from user."""
        context.user_data['wallet_name'] = update.message.text.strip()
        await update.message.reply_text('Masukkan nominal awal wallet:')
        return self.WALLET_BALANCE
    
    async def get_wallet_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get wallet balance and create wallet."""
        telegram_user = update.effective_user

        try:
            balance = Decimal(update.message.text.strip())
            wallet_name = context.user_data['wallet_name']

            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(User)
                    .options(selectinload(User.wallets))
                    .where(User.telegramId == telegram_user.id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    await update.message.reply_text('Kamu belum terdaftar. Ketik /register')
                    return ConversationHandler.END
                
                existing_active_wallet = next(
                    (w for w in user.wallets if w.name == wallet_name and w.isActive), None
                )
                if existing_active_wallet:
                    await update.message.reply_text("❌ Wallet dengan nama ini sudah aktif. Tidak bisa membuat baru.")
                    return ConversationHandler.END

                new_wallet = Wallet(
                    id=str(ObjectId()), 
                    userId=user.id,
                    name=wallet_name,
                    balance=balance,
                )

                session.add(new_wallet)
                await session.commit()

        except ValueError:
            await update.message.reply_text("❌ Nominal tidak valid. Masukkan angka yang benar.")
            logger.info(f'Invalid WALLET_BALANCE {update.message.text}')
            return self.WALLET_BALANCE

        await update.message.reply_text(
            f"✅ Wallet *{wallet_name}* berhasil dibuat dengan saldo *Rp {balance:,.2f}*",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    async def cancel_add_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel wallet addition."""
        await update.message.reply_text("Operasi dibatalkan.")
        return ConversationHandler.END
