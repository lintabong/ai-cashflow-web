telegram_finance_bot/
├── app/
│   ├── __init__.py
│   ├── main.py                     # Entry point untuk bot
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py             # Environment variables & configurations
│   │   └── constants.py            # Constants yang dipindah dari root
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── bot.py                  # Core bot initialization
│   │   ├── dependencies.py         # Dependency injection untuk FastAPI
│   │   └── exceptions.py           # Custom exceptions
│   │
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base handler class
│   │   ├── commands.py             # Command handlers (/start, /register, dll)
│   │   ├── messages.py             # Text message handlers
│   │   ├── callbacks.py            # Callback query handlers
│   │   ├── conversations/
│   │   │   ├── __init__.py
│   │   │   ├── wallet.py           # Wallet conversation handler
│   │   │   └── transaction.py      # Transaction conversation handler
│   │   └── webhooks.py             # FastAPI webhook handlers (future)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py           # Gemini AI service
│   │   ├── transaction_service.py  # Transaction processing logic
│   │   ├── wallet_service.py       # Wallet business logic
│   │   ├── user_service.py         # User business logic
│   │   └── notification_service.py # Notification service
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py             # Pydantic models untuk FastAPI
│   │   ├── responses.py            # Response models
│   │   └── schemas.py              # Additional schemas
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── formatters.py           # Message formatting utilities
│   │   ├── parsers.py              # JSON parsing utilities
│   │   ├── validators.py           # Input validation
│   │   └── decorators.py           # Custom decorators
│   │
│   └── api/                        # Future FastAPI routes
│       ├── __init__.py
│       ├── v1/
│       │   ├── __init__.py
│       │   ├── webhook.py          # Webhook endpoints
│       │   ├── users.py            # User API endpoints
│       │   ├── wallets.py          # Wallet API endpoints
│       │   └── transactions.py     # Transaction API endpoints
│       └── middleware.py           # FastAPI middleware
│
├── lib/                            # Existing database & cache modules
│   ├── __init__.py
│   ├── cache/
│   │   ├── __init__.py
│   │   └── cache.py                # Renamed from existing
│   └── database/
│       ├── __init__.py
│       ├── db.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user_model.py
│       │   ├── cashflow_model.py
│       │   └── wallet_model.py
│       └── managers/
│           ├── __init__.py
│           ├── user_manager.py
│           ├── cashflow_manager.py
│           └── wallet_manager.py
│
├── helpers/                        # Existing helpers
│   ├── __init__.py
│   └── output_message.py
│
├── tests/                          # Unit tests
│   ├── __init__.py
│   ├── test_handlers/
│   ├── test_services/
│   ├── test_utils/
│   └── conftest.py
│
├── scripts/                        # Deployment & utility scripts
│   ├── __init__.py
│   ├── run_bot.py                  # Script untuk menjalankan bot
│   ├── run_webhook.py              # Script untuk menjalankan FastAPI
│   └── migrate.py                  # Database migration script
│
├── docker/                         # Docker configuration
│   ├── Dockerfile.bot              # Untuk polling mode
│   ├── Dockerfile.webhook          # Untuk webhook mode
│   └── docker-compose.yml
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── pyproject.toml                  # Modern Python project configuration