# File Tree: expense_tracker_app

**Generated:** 2/14/2026, 11:54:43 AM
**Root Path:** `g:\My Drive\New Github Working Projects\Finance\expense_tracker_app`

```
├── 📁 app
│   ├── 📁 routes
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 accounts.py
│   │   ├── 🐍 api.py
│   │   ├── 🐍 budgets.py
│   │   ├── 🐍 categories.py
│   │   ├── 🐍 errors.py
│   │   ├── 🐍 export.py
│   │   ├── 🐍 health.py
│   │   ├── 🐍 help.py
│   │   ├── 🐍 logs.py
│   │   ├── 🐍 main.py
│   │   ├── 🐍 profile.py
│   │   ├── 🐍 reports.py
│   │   ├── 🐍 transactions.py
│   │   └── 🐍 updates.py
│   ├── 📁 static
│   │   ├── 📁 css
│   │   │   └── 🎨 style.css
│   │   ├── 📁 js
│   │   │   └── 📄 main.js
│   │   └── 📁 postman
│   │       └── ⚙️ expense-tracker-api.json
│   ├── 📁 templates
│   │   ├── 📁 accounts
│   │   │   └── 🌐 index.html
│   │   ├── 📁 budgets
│   │   │   └── 🌐 index.html
│   │   ├── 📁 categories
│   │   │   └── 🌐 index.html
│   │   ├── 📁 dashboard
│   │   │   └── 🌐 index.html
│   │   ├── 📁 errors
│   │   │   ├── 🌐 404.html
│   │   │   ├── 🌐 429.html
│   │   │   └── 🌐 500.html
│   │   ├── 📁 help
│   │   │   ├── 📁 guides
│   │   │   │   ├── 🌐 accounts.html
│   │   │   │   ├── 🌐 api.html
│   │   │   │   ├── 🌐 budgets.html
│   │   │   │   ├── 🌐 categories.html
│   │   │   │   ├── 🌐 export.html
│   │   │   │   ├── 🌐 filters.html
│   │   │   │   ├── 🌐 getting-started.html
│   │   │   │   ├── 🌐 reports.html
│   │   │   │   ├── 🌐 transactions.html
│   │   │   │   └── 🌐 troubleshooting.html
│   │   │   ├── 🌐 contact.html
│   │   │   ├── 🌐 faq.html
│   │   │   ├── 🌐 glossary.html
│   │   │   └── 🌐 index.html
│   │   ├── 📁 logs
│   │   │   └── 🌐 index.html
│   │   ├── 📁 profile
│   │   │   └── 🌐 index.html
│   │   ├── 📁 transactions
│   │   │   └── 🌐 index.html
│   │   ├── 📁 updates
│   │   │   └── 🌐 index.html
│   │   └── 🌐 base.html
│   ├── 📁 utils
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 exporters.py
│   │   ├── 🐍 helpers.py
│   │   ├── 🐍 reports.py
│   │   └── 🐍 validators.py
│   ├── 🐍 __init__.py
│   └── 🐍 models.py
├── 📁 backups
│   └── ⚙️ .gitkeep
├── 📁 data
│   ├── 📁 _tmp
│   │   └── 📁 spilldb
│   │       ├── 📄 WiredTiger
│   │       ├── 📄 WiredTiger.lock
│   │       ├── 📄 WiredTiger.turtle
│   │       ├── 📄 WiredTiger.wt
│   │       └── 📄 WiredTigerHS.wt
│   ├── 📁 diagnostic.data
│   │   ├── 📄 metrics.2026-02-13T07-31-25Z-00000
│   │   └── 📄 metrics.2026-02-13T07-33-17Z-00000
│   ├── 📁 journal
│   │   ├── 📄 WiredTigerLog.0000000002
│   │   └── 📄 WiredTigerPreplog.0000000001
│   ├── ⚙️ .gitkeep
│   ├── 📄 WiredTiger
│   ├── 📄 WiredTiger.lock
│   ├── 📄 WiredTiger.turtle
│   ├── 📄 WiredTiger.wt
│   ├── 📄 WiredTigerHS.wt
│   ├── 📄 _mdb_catalog.wt
│   ├── 📄 collection-251aaf1e-6594-4611-a4c9-f47a48423970.wt
│   ├── 📄 collection-4c93c887-58c2-4f4a-bb9e-c1783be1129f.wt
│   ├── 📄 collection-7c2e4874-c34c-4826-8b44-b8ce89f6af35.wt
│   ├── 📄 index-1edf669d-24c6-45c3-a371-205be8e705b8.wt
│   ├── 📄 index-7e456850-6883-4fd5-8e02-19e9bfdabdaf.wt
│   ├── 📄 index-aa936909-9d26-4f9a-8a2c-ac8ab2d7b863.wt
│   ├── 📄 index-e8c10428-928a-4740-96ba-ac0c1e6ab850.wt
│   ├── 📄 mongod.lock
│   ├── 📄 sizeStorer.wt
│   └── 📄 storage.bson
├── 📁 logs
│   └── ⚙️ .gitkeep
├── 📁 nginx
│   └── ⚙️ nginx.conf
├── 📁 scripts
│   ├── 🐍 create_test_data.py
│   └── 📄 setup.sh
├── 📁 supervisor
│   └── ⚙️ expense-tracker.conf
├── 📁 tests
│   ├── 🐍 __init__.py
│   ├── 🐍 conftest.py
│   └── 🐍 test_transactions.py
├── ⚙️ .env.example
├── ⚙️ .eslintrc.json
├── ⚙️ .prettierrc
├── 🐳 Dockerfile
├── ⚙️ FILETREE_GENERATED.json
├── 📄 LICENSE
├── 📝 README.MD
├── 🐍 config.py
├── 🐍 create_db.py
├── 🐍 debug_mongo.py
├── ⚙️ docker-compose.prod.yml
├── ⚙️ docker-compose.yml
├── ⚙️ filetree_expense_tracker_app_svg.xml
├── 📄 folder_structure.txt
├── 🐍 manage.py
├── 📄 requirements.txt
├── 🐍 run.py
├── 📄 setup.bat
├── 🐍 test_complete_flow.py
├── 🐍 test_mongo.py
└── 🐍 wsgi.py
```

---

_Generated by FileTree Pro Extension_
